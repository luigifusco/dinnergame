from __future__ import annotations

import tempfile
import unittest
from contextlib import closing
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw
from reportlab.lib.units import mm

from scripts.generate_cards import (
    CARD_HEIGHT,
    CARD_WIDTH,
    CREAM,
    PAGE_HEIGHT,
    ROOT,
    DeckError,
    check_deck,
    layout_sheets,
    load_deck,
    slot_origin,
    write_pdfs,
)

SMALL_DECK = """\
name: Test
tiers:
  common:
    copies: 2
    ingredients:
{common}
  luxury:
    copies: 1
    ingredients:
      gold: Gold leaf
"""


def make_deck(folder: Path, text: str) -> Path:
    path = folder / "deck.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def make_art(folder: Path, *identifiers: str) -> Path:
    art = folder / "art"
    art.mkdir()
    for identifier in identifiers:
        # A paper deliberately different from the card's cream.
        image = Image.new("RGB", (300, 300), (236, 226, 198))
        ImageDraw.Draw(image).ellipse((80, 80, 220, 220), fill=(190, 40, 40), outline=0, width=8)
        image.save(art / f"{identifier}.png")
    return art


def slot_text(document: pdfium.PdfDocument, page: int, slot: int) -> str:
    x, y = slot_origin(slot)
    with closing(document[page]) as pdf_page, closing(pdf_page.get_textpage()) as text:
        return " ".join(text.get_text_bounded(x, y, x + CARD_WIDTH, y + CARD_HEIGHT).split())


class LibraryTests(unittest.TestCase):
    def test_library_prints_each_ingredient_once(self) -> None:
        deck = load_deck(ROOT / "cards" / "ingredients.yaml")
        sheets = layout_sheets(deck)
        self.assertEqual([len(sheet.cards) for sheet in sheets], [9, 9, 9, 9, 8])
        identifiers = [card.id for sheet in sheets for card in sheet.cards]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(check_deck(deck, ROOT / "art"), 44)

    def test_rejects_cards_that_cannot_print(self) -> None:
        cases = {
            "duplicate id": "name: T\ntiers:\n  common: {copies: 1, ingredients: {basil: Basil}}\n"
            "  fine: {copies: 1, ingredients: {basil: Basil}}\n",
            "duplicate YAML key": "name: T\ntiers:\n  common:\n    copies: 1\n    ingredients:\n"
            "      basil: Basil\n      basil: Basil\n",
            "unknown field": "name: T\ntiers:\n  rare: {copies: 1, ingredients: {basil: Basil}}\n",
            "does not fit": "name: T\ntiers:\n  common:\n    copies: 1\n    ingredients:\n"
            "      basil: Basil from the far end of the garden\n",
            "No illustration": "name: T\ntiers:\n  common: {copies: 1, ingredients: {mint: Mint}}",
        }
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            art = make_art(folder, "basil")
            for message, text in cases.items():
                with self.subTest(message), self.assertRaisesRegex(DeckError, message):
                    check_deck(load_deck(make_deck(folder, text)), art)


class PdfTests(unittest.TestCase):
    def test_duplex_pdf_pairs_each_front_with_its_back_reproducibly(self) -> None:
        identifiers = [f"item-{number}" for number in range(6)]
        common = "\n".join(f"      {item}: Item {item[-1]}" for item in identifiers)
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            deck = load_deck(make_deck(folder, SMALL_DECK.format(common=common)))
            art = make_art(folder, *identifiers, "gold")
            paths = write_pdfs(deck, art, folder / "print")
            first = [path.read_bytes() for path in paths]
            write_pdfs(deck, art, folder / "print")
            self.assertEqual(first, [path.read_bytes() for path in paths])

            with closing(pdfium.PdfDocument(paths[-1])) as document:
                self.assertEqual(len(document), 2)
                self.assertEqual(slot_text(document, 0, 0), "Item 0")
                self.assertEqual(slot_text(document, 0, 5), "Item 5")
                self.assertEqual(slot_text(document, 0, 6), "Gold leaf")
                self.assertEqual(slot_text(document, 0, 7), "")
                with closing(document[1]) as pdf_page:
                    with closing(pdf_page.get_textpage()) as text:
                        self.assertEqual(text.get_text_range().strip(), "")

                with closing(document[0]) as pdf_page:
                    scale = 4 / mm
                    image = pdf_page.render(scale=scale).to_pil().convert("RGB")
                x, y = slot_origin(0)
                # Just inside the illustration's corner, the art's paper matches the card.
                pixel = image.getpixel(
                    (
                        round((x + 6 * mm) * scale),
                        round((PAGE_HEIGHT - y - CARD_HEIGHT + 8 * mm) * scale),
                    )
                )
                for channel, expected in zip(pixel, CREAM):
                    self.assertAlmostEqual(channel, expected, delta=3)


if __name__ == "__main__":
    unittest.main()
