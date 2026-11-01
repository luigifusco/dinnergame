"""Generate landscape Sideplot cards on duplex-aligned A4 sheets."""

from __future__ import annotations

import argparse
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from xml.sax.saxutils import escape

import yaml
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import getRegisteredFontNames, registerFont
from reportlab.pdfbase.ttfonts import TTFError, TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
FONT_REGULAR = "BalsamiqSans"
FONT_BOLD = "BalsamiqSans-Bold"
PAGE_WIDTH, PAGE_HEIGHT = A4
CARD_WIDTH, CARD_HEIGHT = 88 * mm, 63 * mm
GUTTER = 5 * mm
COLUMNS, ROWS = 2, 4
CARDS_PER_SHEET = COLUMNS * ROWS
CONTENT_WIDTH = CARD_WIDTH - 10 * mm
CONTENT_TOP = CARD_HEIGHT - 13 * mm
CONTENT_BOTTOM = 5 * mm
TEXT_GAP = 3 * mm
FILENAMES = ("sideplot-fronts.pdf", "sideplot-backs.pdf", "sideplot-duplex.pdf")

CardKind = Literal["running", "mission"]
FlipMode = Literal["long-edge", "short-edge"]
Face = Literal["front", "back"]


class DeckError(ValueError):
    """A card definition cannot be printed safely."""


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise yaml.constructor.ConstructorError(
                None, None, "YAML keys must be strings", key_node.start_mark
            )
        if key in result:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate YAML key: {key}", key_node.start_mark
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)


@dataclass(frozen=True)
class Card:
    id: str
    kind: CardKind
    title: str
    text: str
    copies: int = 1


@dataclass(frozen=True)
class Deck:
    name: str
    cards: tuple[Card, ...]


@dataclass(frozen=True)
class PreparedCard:
    card: Card
    title: Paragraph
    text: Paragraph
    title_height: float
    text_height: float


@dataclass(frozen=True)
class PreparedDeck:
    name: str
    cards: tuple[PreparedCard, ...]


@dataclass(frozen=True)
class Palette:
    ink: colors.Color
    paper: colors.Color
    pattern: colors.Color


PALETTES: dict[CardKind, Palette] = {
    "running": Palette(
        colors.HexColor("#20584B"), colors.HexColor("#EEF4EC"), colors.HexColor("#C3D7C6")
    ),
    "mission": Palette(
        colors.HexColor("#8B4F23"), colors.HexColor("#FCF2DF"), colors.HexColor("#EAD2A9")
    ),
}
LABELS: dict[CardKind, str] = {"running": "RUNNING BIT", "mission": "MISSION"}


def _check_fields(data: dict[str, object], allowed: set[str], context: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise DeckError(f"{context}: unknown field(s): {', '.join(sorted(unknown))}")


def _read_text(data: dict[str, object], field: str, context: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise DeckError(f"{context}: '{field}' must be non-empty text")
    value = value.strip()
    if any(not char.isprintable() and char != "\n" for char in value):
        raise DeckError(f"{context}: '{field}' contains an unsupported control character")
    try:
        value.encode("cp1252")
    except UnicodeEncodeError as exc:
        raise DeckError(
            f"{context}: '{field}' contains unsupported characters. "
            "The PDF fonts support Western European text, not emoji or other scripts."
        ) from exc
    return value


def load_deck(path: Path) -> Deck:
    try:
        data = yaml.load(path.read_text(encoding="utf-8-sig"), Loader=UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise DeckError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise DeckError("The deck must be a YAML mapping with 'name' and 'cards'")
    _check_fields(data, {"name", "cards"}, "Deck")
    name = _read_text(data, "name", "Deck")
    if "\n" in name:
        raise DeckError("Deck: 'name' must be a single line")
    entries = data.get("cards")
    if not isinstance(entries, list) or not entries:
        raise DeckError("Deck: 'cards' must be a non-empty list")
    cards: list[Card] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        context = f"Card {index}"
        if not isinstance(entry, dict):
            raise DeckError(f"{context}: expected a mapping")
        _check_fields(entry, {"id", "type", "title", "text", "copies"}, context)
        identifier = _read_text(entry, "id", context)
        context = f"Card '{identifier}'"
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier):
            raise DeckError(
                f"{context}: use lowercase letters, digits and single hyphens for the id"
            )
        if identifier in seen:
            raise DeckError(f"{context}: duplicate card id")
        seen.add(identifier)
        kind: CardKind
        if entry.get("type") == "running":
            kind = "running"
        elif entry.get("type") == "mission":
            kind = "mission"
        else:
            raise DeckError(f"{context}: 'type' must be 'running' or 'mission'")
        copies = entry.get("copies", 1)
        if type(copies) is not int or copies < 1:
            raise DeckError(f"{context}: 'copies' must be a positive integer")
        cards.append(
            Card(
                identifier,
                kind,
                _read_text(entry, "title", context),
                _read_text(entry, "text", context),
                copies,
            )
        )
    return Deck(name, tuple(cards))


def _register_fonts() -> None:
    for name, filename in (
        (FONT_REGULAR, "BalsamiqSans-Regular.ttf"),
        (FONT_BOLD, "BalsamiqSans-Bold.ttf"),
    ):
        if name not in getRegisteredFontNames():
            path = ROOT / "assets" / "fonts" / filename
            try:
                registerFont(TTFont(name, str(path)))
            except (OSError, TTFError) as exc:
                raise DeckError(f"Cannot load bundled font {path}: {exc}") from exc


def _fit_card(card: Card) -> PreparedCard:
    for title_size, text_size in ((20, 11), (19, 10.5), (18, 10), (17, 9.5), (16, 9)):
        title = Paragraph(
            escape(card.title).replace("\n", "<br/>"),
            ParagraphStyle(
                "card-title",
                fontName=FONT_BOLD,
                fontSize=title_size,
                leading=title_size * 1.1,
                textColor=colors.HexColor("#22342F"),
            ),
        )
        text = Paragraph(
            escape(card.text).replace("\n", "<br/>"),
            ParagraphStyle(
                "card-text",
                fontName=FONT_REGULAR,
                fontSize=text_size,
                leading=text_size * 1.32,
                textColor=colors.HexColor("#303936"),
            ),
        )
        _, title_height = title.wrap(CONTENT_WIDTH, PAGE_HEIGHT)
        _, text_height = text.wrap(CONTENT_WIDTH, PAGE_HEIGHT)
        if title_height + TEXT_GAP + text_height <= CONTENT_TOP - CONTENT_BOTTOM:
            return PreparedCard(card, title, text, title_height, text_height)
    raise DeckError(
        f"Card '{card.id}' does not fit at a readable size (minimum 9 pt body text). "
        "Shorten its title or text."
    )


def prepare_deck(deck: Deck, kind: CardKind | None = None) -> PreparedDeck:
    _register_fonts()
    cards = []
    for card in deck.cards:
        if kind is None or card.kind == kind:
            prepared = _fit_card(card)
            cards.extend([prepared] * card.copies)
    if not cards:
        raise DeckError(f"No cards match type '{kind}'")
    return PreparedDeck(deck.name, tuple(cards))


def slot_origin(
    slot: int, face: Face = "front", flip: FlipMode = "long-edge"
) -> tuple[float, float]:
    row, column = divmod(slot, COLUMNS)
    if face == "back":
        if flip == "long-edge":
            column = COLUMNS - 1 - column
        else:
            row = ROWS - 1 - row
    grid_width = COLUMNS * CARD_WIDTH + (COLUMNS - 1) * GUTTER
    grid_height = ROWS * CARD_HEIGHT + (ROWS - 1) * GUTTER
    # Reflect slots in the full sheet, never in the shortened last batch.
    x = (PAGE_WIDTH - grid_width) / 2 + column * (CARD_WIDTH + GUTTER)
    y = (PAGE_HEIGHT - grid_height) / 2 + (ROWS - 1 - row) * (CARD_HEIGHT + GUTTER)
    return x, y


def _diamond(canvas: Canvas, x: float, y: float, rx: float, ry: float, fill: int = 0) -> None:
    path = canvas.beginPath()
    path.moveTo(x, y + ry)
    path.lineTo(x + rx, y)
    path.lineTo(x, y - ry)
    path.lineTo(x - rx, y)
    path.close()
    canvas.drawPath(path, stroke=1, fill=fill)


def _draw_front(canvas: Canvas, item: PreparedCard) -> None:
    palette = PALETTES[item.card.kind]
    canvas.setFillColor(palette.ink)
    canvas.setFont(FONT_BOLD, 8.5)
    canvas.drawString(5 * mm, CARD_HEIGHT - 8 * mm, LABELS[item.card.kind])
    title_y = CONTENT_TOP - item.title_height
    item.title.drawOn(canvas, 5 * mm, title_y)
    item.text.drawOn(canvas, 5 * mm, title_y - TEXT_GAP - item.text_height)


def _draw_back(canvas: Canvas, kind: CardKind) -> None:
    palette = PALETTES[kind]
    inset = 2 * mm
    canvas.setFillColor(palette.paper)
    canvas.rect(inset, inset, CARD_WIDTH - 2 * inset, CARD_HEIGHT - 2 * inset, stroke=0, fill=1)
    canvas.saveState()
    clip = canvas.beginPath()
    clip.rect(inset, inset, CARD_WIDTH - 2 * inset, CARD_HEIGHT - 2 * inset)
    canvas.clipPath(clip, stroke=0)
    canvas.setStrokeColor(palette.pattern)
    canvas.setLineWidth(0.55)
    step = 18 * mm
    for row in range(-1, int(CARD_HEIGHT // step) + 2):
        for column in range(-1, int(CARD_WIDTH // step) + 2):
            x = column * step + (row % 2) * step / 2
            y = row * step
            if kind == "running":
                canvas.circle(x, y, 5 * mm)
            else:
                _diamond(canvas, x, y, 5 * mm, 5 * mm)
    canvas.restoreState()
    canvas.setStrokeColor(palette.ink)
    canvas.setFillColor(palette.paper)
    canvas.setLineWidth(0.7)
    canvas.rect(inset, inset, CARD_WIDTH - 2 * inset, CARD_HEIGHT - 2 * inset)
    cx, cy = CARD_WIDTH / 2, CARD_HEIGHT / 2
    if kind == "running":
        canvas.circle(cx, cy, 20 * mm, fill=1)
    else:
        _diamond(canvas, cx, cy, 29 * mm, 20 * mm, fill=1)
    canvas.setFillColor(palette.ink)
    canvas.setFont(FONT_BOLD, 14)
    canvas.drawCentredString(cx, cy - 1.7 * mm, LABELS[kind])


def _draw_crop_marks(canvas: Canvas) -> None:
    gap, length = 0.6 * mm, 1.5 * mm
    canvas.setStrokeColor(colors.HexColor("#87928C"))
    canvas.setLineWidth(0.3)
    for x, direction_x in ((0, -1), (CARD_WIDTH, 1)):
        for y, direction_y in ((0, -1), (CARD_HEIGHT, 1)):
            canvas.line(x + direction_x * gap, y, x + direction_x * (gap + length), y)
            canvas.line(x, y + direction_y * gap, x, y + direction_y * (gap + length))


def _draw_sheet(
    canvas: Canvas,
    sheet: tuple[PreparedCard, ...],
    sheet_number: int,
    sheet_count: int,
    face: Face,
    flip: FlipMode,
) -> None:
    for slot, item in enumerate(sheet):
        canvas.saveState()
        canvas.translate(*slot_origin(slot, face, flip))
        if face == "front":
            _draw_front(canvas, item)
        else:
            _draw_back(canvas, item.card.kind)
        _draw_crop_marks(canvas)
        canvas.restoreState()
    canvas.setFillColor(colors.HexColor("#52625A"))
    canvas.setStrokeColor(colors.HexColor("#52625A"))
    canvas.setFont(FONT_REGULAR, 6)
    canvas.drawString(
        14.5 * mm,
        7 * mm,
        f"{face.upper()} | Sheet {sheet_number}/{sheet_count} | {flip} duplex",
    )
    scale_x = PAGE_WIDTH - 64.5 * mm
    canvas.setLineWidth(0.4)
    canvas.line(scale_x, 7 * mm, scale_x + 50 * mm, 7 * mm)
    for x in (scale_x, scale_x + 50 * mm):
        canvas.line(x, 6 * mm, x, 8 * mm)
    canvas.drawCentredString(scale_x + 25 * mm, 9 * mm, "50 mm - print at 100%")
    canvas.showPage()


def write_pdfs(deck: PreparedDeck, output: Path, flip: FlipMode = "long-edge") -> tuple[Path, ...]:
    sheets = tuple(
        deck.cards[start : start + CARDS_PER_SHEET]
        for start in range(0, len(deck.cards), CARDS_PER_SHEET)
    )
    output.mkdir(parents=True, exist_ok=True)
    destinations = tuple(output / filename for filename in FILENAMES)
    # Render the whole set before replacing existing PDFs.
    with tempfile.TemporaryDirectory(prefix=".sideplot-", dir=output) as temporary:
        staged = []
        face_sets: tuple[tuple[Face, ...], ...] = (("front",), ("back",), ("front", "back"))
        for filename, faces in zip(FILENAMES, face_sets, strict=True):
            path = Path(temporary) / filename
            canvas = Canvas(str(path), pagesize=A4, pageCompression=1, invariant=1)
            canvas.setTitle(f"{deck.name} - {', '.join(faces)}")
            canvas.setAuthor(deck.name)
            canvas.setCreator("Sideplot card generator")
            for number, sheet in enumerate(sheets, start=1):
                for face in faces:
                    _draw_sheet(canvas, sheet, number, len(sheets), face, flip)
            canvas.save()
            staged.append(path)
        for source, destination in zip(staged, destinations, strict=True):
            source.replace(destination)
    return destinations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cards", type=Path, default=ROOT / "cards.yaml", help="YAML deck file")
    parser.add_argument("--output", type=Path, default=ROOT / "print", help="PDF output directory")
    parser.add_argument("--kind", choices=("all", "running", "mission"), default="all")
    parser.add_argument("--flip", choices=("long-edge", "short-edge"), default="long-edge")
    parser.add_argument(
        "--check", action="store_true", help="Validate text and fit without writing PDFs"
    )
    args = parser.parse_args(argv)
    try:
        kind = None if args.kind == "all" else args.kind
        deck = prepare_deck(load_deck(args.cards), kind)
        if args.check:
            print(f"Validated {len(deck.cards)} printable cards.")
            return 0
        paths = write_pdfs(deck, args.output, args.flip)
    except (DeckError, OSError) as exc:
        parser.error(str(exc))
    for path in paths:
        print(path)
    print(
        f"{len(deck.cards)} cards. Print the duplex PDF on portrait A4 at 100%, "
        f"double-sided, flip on the {args.flip.replace('-', ' ')}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
