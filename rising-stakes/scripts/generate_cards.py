"""Generate Rising Stakes ingredient cards on duplex A4 sheets."""

from __future__ import annotations

import argparse
import math
import re
import tempfile
from dataclasses import dataclass
from functools import cache
from io import BytesIO
from pathlib import Path

import yaml
from PIL import Image, ImageChops
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import getFont, getRegisteredFontNames, registerFont, stringWidth
from reportlab.pdfbase.ttfonts import TTFError, TTFont
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).resolve().parents[1]
FONT = "Chewy"
PAGE_WIDTH, PAGE_HEIGHT = A4
CARD_WIDTH, CARD_HEIGHT = 63 * mm, 88 * mm
COLUMNS, ROWS = 3, 3
CARDS_PER_SHEET = COLUMNS * ROWS
GRID_WIDTH, GRID_HEIGHT = COLUMNS * CARD_WIDTH, ROWS * CARD_HEIGHT
GRID_X, GRID_Y = (PAGE_WIDTH - GRID_WIDTH) / 2, (PAGE_HEIGHT - GRID_HEIGHT) / 2
FRONT_BLEED = 1.5 * mm  # around the outside of the grid only; neighbors share their edges
BACK_OVERFLOW = 6 * mm  # absorbs duplex drift, so the back never needs aligning
GUIDE_NEAR, GUIDE_FAR = 2.5 * mm, 6.5 * mm  # cut guides, measured outwards from the grid
ART_SIZE, ART_TOP, ART_PIXELS = 54 * mm, 6 * mm, 800
NAME_SIZE, MIN_NAME_SIZE = 20.0, 14.0
NAME_BASELINE, NAME_MARGIN = 14 * mm, 6 * mm
CAPTION_SIZE = 8.0
CREAM = (247, 237, 215)  # every illustration's paper is remapped to this
INK = colors.HexColor("#2A211B")
LINEN = colors.HexColor("#FFFCF6")
FILENAMES = ("rising-stakes-fronts.pdf", "rising-stakes-backs.pdf", "rising-stakes-duplex.pdf")

# Ondulato: wavy translucent bands whose washes compound where they cross. The repeat divides
# the card exactly (3 across, 4 down), so one continuous cloth behind a sheet gives every card
# the same back, with a crossing at its center.
REPEAT_X, REPEAT_Y = CARD_WIDTH / 3, CARD_HEIGHT / 4
AMPLITUDE, STEP, WASH = 1.5 * mm, 1 * mm, 0.45


class DeckError(ValueError):
    """A card definition cannot be printed safely."""


@dataclass(frozen=True)
class TierStyle:
    title: str
    cloth: str


CLOTHS = {
    "red": colors.HexColor("#C42B2F"),
    "green": colors.HexColor("#2E7A41"),
    "blue": colors.HexColor("#2756A3"),
}
TIERS = {
    "common": TierStyle("Common", "red"),
    "fine": TierStyle("Fine", "green"),
    "luxury": TierStyle("Luxury", "blue"),
    # Wild cards share the Common back, so they hide among the Commons.
    "wild": TierStyle("Wild", "red"),
}


@dataclass(frozen=True)
class Ingredient:
    id: str
    name: str


@dataclass(frozen=True)
class Tier:
    key: str
    copies: int
    ingredients: tuple[Ingredient, ...]


@dataclass(frozen=True)
class Deck:
    name: str
    tiers: tuple[Tier, ...]


@dataclass(frozen=True)
class Sheet:
    cloth: str
    tiers: tuple[str, ...]
    cards: tuple[Ingredient, ...]


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _unique_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode) -> dict[object, object]:
    result: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate YAML key: {key}", key_node.start_mark
            )
        result[key] = loader.construct_object(value_node)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)


def _mapping(value: object, context: str, fields: set[str] | None = None) -> dict[object, object]:
    if not isinstance(value, dict) or not value:
        raise DeckError(f"{context}: expected a non-empty mapping")
    if fields is not None and set(value) - fields:
        unknown = ", ".join(sorted(map(str, set(value) - fields)))
        raise DeckError(f"{context}: unknown field(s): {unknown}")
    return value


def _line(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\n" in value.strip():
        raise DeckError(f"{context}: expected a single line of text")
    return value.strip()


def load_deck(path: Path) -> Deck:
    try:
        data = yaml.load(path.read_text(encoding="utf-8-sig"), Loader=UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise DeckError(f"Cannot read {path}: {exc}") from exc
    data = _mapping(data, str(path), {"name", "tiers"})
    tiers_data = _mapping(data.get("tiers"), f"{path}: tiers", set(TIERS))
    seen: set[str] = set()
    tiers = []
    for key in TIERS:
        if key not in tiers_data:
            continue
        context = f"{path}: tier '{key}'"
        tier = _mapping(tiers_data[key], context, {"copies", "ingredients"})
        copies = tier.get("copies")
        if type(copies) is not int or copies < 1:
            raise DeckError(f"{context}: 'copies' must be a positive integer")
        ingredients = []
        for identifier, name in _mapping(
            tier.get("ingredients"), f"{context}: ingredients"
        ).items():
            if not isinstance(identifier, str) or not re.fullmatch(
                r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier
            ):
                raise DeckError(
                    f"{context}: id '{identifier}' must use lowercase letters, digits and "
                    "single hyphens"
                )
            if identifier in seen:
                raise DeckError(f"{context}: duplicate id '{identifier}'")
            seen.add(identifier)
            ingredients.append(Ingredient(identifier, _line(name, f"{context}: '{identifier}'")))
        tiers.append(Tier(key, copies, tuple(ingredients)))
    return Deck(_line(data.get("name"), f"{path}: name"), tuple(tiers))


def layout_sheets(deck: Deck) -> tuple[Sheet, ...]:
    """Fill one back color per sheet, spreading each ingredient's copies over different sheets."""
    groups: dict[str, list[tuple[str, Ingredient]]] = {}
    for tier in deck.tiers:
        groups.setdefault(TIERS[tier.key].cloth, []).extend(
            (tier.key, item) for _ in range(tier.copies) for item in tier.ingredients
        )
    sheets = []
    for cloth, cards in groups.items():
        count = math.ceil(len(cards) / CARDS_PER_SHEET)
        start = 0
        # Dealing the copy-by-copy sequence in even, consecutive runs keeps copies apart.
        for index in range(count):
            size = len(cards) // count + (index < len(cards) % count)
            run = cards[start : start + size]
            tiers = tuple(dict.fromkeys(key for key, _ in run))
            sheets.append(Sheet(cloth, tiers, tuple(item for _, item in run)))
            start += size
    return tuple(sheets)


def _register_font() -> None:
    if FONT not in getRegisteredFontNames():
        path = ROOT / "assets" / "fonts" / "Chewy-Regular.ttf"
        try:
            registerFont(TTFont(FONT, str(path)))
        except (OSError, TTFError) as exc:
            raise DeckError(f"Cannot load bundled font {path}: {exc}") from exc


def name_size(name: str) -> float:
    missing = sorted({char for char in name if ord(char) not in getFont(FONT).face.charToGlyph})
    if missing:
        raise DeckError(f"'{name}': the card font has no glyph for {' '.join(missing)}")
    size = NAME_SIZE
    while stringWidth(name, FONT, size) > CARD_WIDTH - 2 * NAME_MARGIN:
        size -= 0.25
        if size < MIN_NAME_SIZE:
            raise DeckError(f"'{name}' does not fit on a card at {MIN_NAME_SIZE:g} pt; shorten it")
    return size


@cache
def art_jpeg(path: Path) -> bytes:
    """Crop an illustration to its subject and move it onto the shared cream."""
    try:
        with Image.open(path) as source:
            img = source.convert("RGB")
    except OSError as exc:
        raise DeckError(f"Cannot read illustration {path}: {exc}") from exc
    corners = [
        img.crop((x, y, x + 24, y + 24)).resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
        for x in (8, img.width - 32)
        for y in (8, img.height - 32)
    ]
    paper = tuple(sorted(corner[i] for corner in corners)[len(corners) // 2] for i in range(3))
    diff = ImageChops.difference(img, Image.new("RGB", img.size, paper)).convert("L")
    bounds = diff.point(lambda v: 255 if v > 60 else 0).getbbox()
    if bounds is None:
        raise DeckError(f"{path}: no illustration found on the paper")
    left, top, right, bottom = bounds
    side = max(right - left, bottom - top) * 1.06
    cx, cy = (left + right) / 2, (top + bottom) / 2
    box = (round(cx - side / 2), round(cy - side / 2), round(cx + side / 2), round(cy + side / 2))
    img, diff = img.crop(box), diff.crop(box)
    # Flatten the paper texture, then remap the paper to the shared cream, so the art sits
    # seamlessly on the card and neighbors on a sheet match.
    soft = diff.point(lambda v: 0 if v < 22 else 255 if v > 48 else (v - 22) * 255 // 26)
    img = Image.composite(img, Image.new("RGB", img.size, paper), soft)
    img = Image.merge(
        "RGB",
        [
            band.point(lambda v, k=target / max(source, 1): min(255, round(v * k)))
            for band, target, source in zip(img.split(), CREAM, paper)
        ],
    )
    img = img.resize((ART_PIXELS, ART_PIXELS), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, "JPEG", quality=90, subsampling=0)
    return buffer.getvalue()


def check_deck(deck: Deck, art: Path) -> int:
    """Validate every name and illustration before anything is written."""
    _register_font()
    for tier in deck.tiers:
        for item in tier.ingredients:
            name_size(item.name)
            path = art / f"{item.id}.png"
            if not path.is_file():
                raise DeckError(f"No illustration for '{item.id}': expected {path}")
            art_jpeg(path)
    return sum(tier.copies * len(tier.ingredients) for tier in deck.tiers)


def slot_origin(slot: int) -> tuple[float, float]:
    row, column = divmod(slot, COLUMNS)
    return GRID_X + column * CARD_WIDTH, GRID_Y + (ROWS - 1 - row) * CARD_HEIGHT


def _draw_card(canvas: Canvas, item: Ingredient, art: Path) -> None:
    image = ImageReader(BytesIO(art_jpeg(art / f"{item.id}.png")))
    canvas.drawImage(
        image, (CARD_WIDTH - ART_SIZE) / 2, CARD_HEIGHT - ART_TOP - ART_SIZE, ART_SIZE, ART_SIZE
    )
    canvas.setFillColor(INK)
    canvas.setFont(FONT, name_size(item.name))
    canvas.drawCentredString(CARD_WIDTH / 2, NAME_BASELINE, item.name)


def _draw_cut_guides(canvas: Canvas) -> None:
    canvas.setStrokeColor(INK)
    canvas.setLineWidth(0.5)
    for column in range(COLUMNS + 1):
        x = GRID_X + column * CARD_WIDTH
        canvas.line(x, GRID_Y - GUIDE_NEAR, x, GRID_Y - GUIDE_FAR)
        canvas.line(x, GRID_Y + GRID_HEIGHT + GUIDE_NEAR, x, GRID_Y + GRID_HEIGHT + GUIDE_FAR)
    for row in range(ROWS + 1):
        y = GRID_Y + row * CARD_HEIGHT
        canvas.line(GRID_X - GUIDE_NEAR, y, GRID_X - GUIDE_FAR, y)
        canvas.line(GRID_X + GRID_WIDTH + GUIDE_NEAR, y, GRID_X + GRID_WIDTH + GUIDE_FAR, y)


def _draw_front(canvas: Canvas, sheet: Sheet, number: int, count: int, art: Path) -> None:
    canvas.setFillColorRGB(*(value / 255 for value in CREAM))
    canvas.rect(
        GRID_X - FRONT_BLEED,
        GRID_Y - FRONT_BLEED,
        GRID_WIDTH + 2 * FRONT_BLEED,
        GRID_HEIGHT + 2 * FRONT_BLEED,
        stroke=0,
        fill=1,
    )
    for slot, item in enumerate(sheet.cards):
        canvas.saveState()
        canvas.translate(*slot_origin(slot))
        _draw_card(canvas, item, art)
        canvas.restoreState()
    _draw_cut_guides(canvas)
    titles = " and ".join(TIERS[tier].title for tier in sheet.tiers)
    canvas.setFillColor(INK)
    canvas.setFont(FONT, CAPTION_SIZE)
    canvas.drawCentredString(
        PAGE_WIDTH / 2,
        GRID_Y - 10 * mm,
        f"Sheet {number} of {count}: {titles}, {sheet.cloth} back. Print at 100%, "
        "double-sided. Cut straight from guide to guide.",
    )


def _grid(lo: float, hi: float, pitch: float, phase: float) -> list[float]:
    first, last = math.floor((lo - phase) / pitch) - 1, math.ceil((hi - phase) / pitch) + 1
    return [phase + k * pitch for k in range(first, last + 1)]


def _wash(color: colors.Color, layers: int) -> colors.Color:
    """The opaque color of `layers` translucent washes over linen."""
    cover = 1 - (1 - WASH) ** layers
    return colors.Color(
        *(base + (ink - base) * cover for base, ink in zip(LINEN.rgb(), color.rgb()))
    )


def draw_cloth(
    canvas: Canvas, color: colors.Color, x0: float, y0: float, x1: float, y1: float
) -> None:
    """Fill a rectangle given in card coordinates; the pattern stays anchored to the cards."""
    vertical, ys = canvas.beginPath(), _grid(y0, y1, STEP, 0.0)
    shifts = [AMPLITUDE * math.sin(2 * math.pi * (y - CARD_HEIGHT / 2) / REPEAT_Y) for y in ys]
    for xc in _grid(x0, x1, REPEAT_X, CARD_WIDTH / 2):
        vertical.moveTo(xc - REPEAT_X / 4 + shifts[0], ys[0])
        for y, shift in zip(ys[1:], shifts[1:]):
            vertical.lineTo(xc - REPEAT_X / 4 + shift, y)
        for y, shift in zip(reversed(ys), reversed(shifts)):
            vertical.lineTo(xc + REPEAT_X / 4 + shift, y)
        vertical.close()
    horizontal, xs = canvas.beginPath(), _grid(x0, x1, STEP, 0.0)
    shifts = [AMPLITUDE * math.sin(2 * math.pi * (x - CARD_WIDTH / 2) / REPEAT_X) for x in xs]
    for yc in _grid(y0, y1, REPEAT_Y, CARD_HEIGHT / 2):
        horizontal.moveTo(xs[0], yc - REPEAT_Y / 4 + shifts[0])
        for x, shift in zip(xs[1:], shifts[1:]):
            horizontal.lineTo(x, yc - REPEAT_Y / 4 + shift)
        for x, shift in zip(reversed(xs), reversed(shifts)):
            horizontal.lineTo(x, yc + REPEAT_Y / 4 + shift)
        horizontal.close()
    canvas.saveState()
    clip = canvas.beginPath()
    clip.rect(x0, y0, x1 - x0, y1 - y0)
    canvas.clipPath(clip, stroke=0, fill=0)
    canvas.setFillColor(LINEN)
    canvas.rect(x0, y0, x1 - x0, y1 - y0, stroke=0, fill=1)
    # Opaque colors instead of transparency: one wash on each band, two where they cross.
    canvas.setFillColor(_wash(color, 1))
    canvas.drawPath(vertical, stroke=0, fill=1)
    canvas.drawPath(horizontal, stroke=0, fill=1)
    canvas.clipPath(horizontal, stroke=0, fill=0)
    canvas.setFillColor(_wash(color, 2))
    canvas.drawPath(vertical, stroke=0, fill=1)
    canvas.restoreState()


def _draw_back(canvas: Canvas, sheet: Sheet) -> None:
    # Each cloth is drawn once as a form and reused by every sheet with that back.
    form = f"cloth-{sheet.cloth}"
    if not canvas.hasForm(form):
        canvas.beginForm(form)
        # The grid is centered, so after any flip the crossings still sit behind the card centers.
        canvas.translate(GRID_X, GRID_Y)
        draw_cloth(
            canvas,
            CLOTHS[sheet.cloth],
            -BACK_OVERFLOW,
            -BACK_OVERFLOW,
            GRID_WIDTH + BACK_OVERFLOW,
            GRID_HEIGHT + BACK_OVERFLOW,
        )
        canvas.endForm()
    canvas.doForm(form)


def write_pdfs(deck: Deck, art: Path, output: Path) -> tuple[Path, ...]:
    sheets = layout_sheets(deck)
    output.mkdir(parents=True, exist_ok=True)
    destinations = tuple(output / filename for filename in FILENAMES)
    # Render the whole set before replacing existing PDFs.
    with tempfile.TemporaryDirectory(prefix=".rising-stakes-", dir=output) as temporary:
        staged = []
        for filename, faces in zip(FILENAMES, (("front",), ("back",), ("front", "back"))):
            path = Path(temporary) / filename
            canvas = Canvas(str(path), pagesize=A4, pageCompression=1, invariant=1)
            canvas.setTitle(f"{deck.name} - {', '.join(faces)}")
            canvas.setAuthor(deck.name)
            canvas.setCreator("Rising Stakes card generator")
            for number, sheet in enumerate(sheets, start=1):
                for face in faces:
                    if face == "front":
                        _draw_front(canvas, sheet, number, len(sheets), art)
                    else:
                        _draw_back(canvas, sheet)
                    canvas.showPage()
            canvas.save()
            staged.append(path)
        for source, destination in zip(staged, destinations):
            source.replace(destination)
    return destinations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cards", type=Path, default=ROOT / "cards" / "ingredients.yaml", help="Deck YAML file"
    )
    parser.add_argument(
        "--art", type=Path, default=ROOT / "art", help="Directory of <id>.png illustrations"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "print", help="PDF output directory")
    parser.add_argument(
        "--check", action="store_true", help="Validate names and art without writing PDFs"
    )
    args = parser.parse_args(argv)
    try:
        deck = load_deck(args.cards)
        cards = check_deck(deck, args.art)
        if args.check:
            print(f"Validated {cards} printable cards.")
            return 0
        paths = write_pdfs(deck, args.art, args.output)
    except (DeckError, OSError) as exc:
        parser.error(str(exc))
    for path in paths:
        print(path)
    sheets = len(layout_sheets(deck))
    print(
        f"{cards} cards on {sheets} sheets. Print the duplex PDF on A4 at 100%, double-sided; "
        "either flip works."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
