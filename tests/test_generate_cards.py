from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

import pypdfium2 as pdfium
import yaml

from scripts.generate_cards import (
    CARD_HEIGHT,
    CARD_WIDTH,
    CARDS_PER_SHEET,
    FILENAMES,
    PAGE_HEIGHT,
    PAGE_WIDTH,
    ROOT,
    Card,
    Deck,
    DeckError,
    load_deck,
    prepare_deck,
    slot_origin,
    write_pdfs,
)


def text_in_slot(document: pdfium.PdfDocument, page_number: int, x: float, y: float) -> str:
    with closing(document[page_number]) as page, closing(page.get_textpage()) as text:
        return " ".join(text.get_text_bounded(x, y, x + CARD_WIDTH, y + CARD_HEIGHT).split())


def page_text(document: pdfium.PdfDocument, page_number: int) -> str:
    with closing(document[page_number]) as page, closing(page.get_textpage()) as text:
        return text.get_text_range()


class CardGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="sideplot-test-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    def write_deck(self, entries: list[dict[str, object]], name: str = "Sideplot") -> Path:
        path = self.directory / "cards.yaml"
        path.write_text(
            yaml.safe_dump({"name": name, "cards": entries}, allow_unicode=True),
            encoding="utf-8",
        )
        return path

    def entry(self, **overrides: object) -> dict[str, object]:
        return {
            "id": "test-card",
            "type": "running",
            "title": "A quiet task",
            "text": "Bring up an ordinary topic naturally.",
            **overrides,
        }

    def test_editable_text_and_copies_survive_loading(self) -> None:
        path = self.directory / "cards.yaml"
        path.write_text(
            "name: Sideplot\ncards:\n"
            "  - id: coffee\n"
            "    type: running\n"
            '    title: "Caff\u00e8 & <biscuits>"\n'
            "    text: >-\n"
            "      Mention tea & coffee.\n"
            '      Say "<br/>" literally.\n'
            "    copies: 2\n",
            encoding="utf-8",
        )
        deck = load_deck(path)
        self.assertEqual(deck.cards[0].text, 'Mention tea & coffee. Say "<br/>" literally.')
        prepared = prepare_deck(deck)
        self.assertEqual(len(prepared.cards), 2)
        paths = write_pdfs(prepared, self.directory / "pdfs")
        with pdfium.PdfDocument(paths[0]) as document:
            text = page_text(document, 0)
            self.assertIn("Caff\u00e8 & <biscuits>", text)
            self.assertIn("<br/>", text)

    def test_invalid_card_fields_fail_explicitly(self) -> None:
        cases = (
            ({"type": "missions"}, "'type'"),
            ({"copies": 0}, "'copies'"),
            ({"copies": True}, "'copies'"),
            ({"copies": "2"}, "'copies'"),
            ({"title": ""}, "'title'"),
            ({"text": 42}, "'text'"),
            ({"text": "A task \U0001f600"}, "unsupported characters"),
            ({"id": "Spaces Here"}, "single hyphens"),
            ({"instruction": "Typo"}, "unknown field"),
        )
        for overrides, message in cases:
            with self.subTest(overrides=overrides):
                path = self.write_deck([self.entry(**overrides)])
                with self.assertRaisesRegex(DeckError, message):
                    load_deck(path)

    def test_duplicate_ids_keys_and_empty_decks_are_rejected(self) -> None:
        path = self.write_deck([self.entry(), self.entry()])
        with self.assertRaisesRegex(DeckError, "duplicate card id"):
            load_deck(path)
        path.write_text("name: First\nname: Second\ncards: []\n", encoding="utf-8")
        with self.assertRaisesRegex(DeckError, "duplicate YAML key"):
            load_deck(path)
        path = self.write_deck([])
        with self.assertRaisesRegex(DeckError, "non-empty list"):
            load_deck(path)

    def test_deck_name_must_be_single_line(self) -> None:
        path = self.write_deck([self.entry()], "Side\nplot")
        with self.assertRaisesRegex(DeckError, "name"):
            load_deck(path)

    def test_back_slots_reflect_in_the_physical_sheet(self) -> None:
        for slot in range(CARDS_PER_SHEET):
            front_x, front_y = slot_origin(slot)
            with self.subTest(slot=slot, flip="long-edge"):
                back_x, back_y = slot_origin(slot, "back", "long-edge")
                self.assertAlmostEqual(front_x + back_x + CARD_WIDTH, PAGE_WIDTH)
                self.assertAlmostEqual(front_y, back_y)
            with self.subTest(slot=slot, flip="short-edge"):
                back_x, back_y = slot_origin(slot, "back", "short-edge")
                self.assertAlmostEqual(front_x, back_x)
                self.assertAlmostEqual(front_y + back_y + CARD_HEIGHT, PAGE_HEIGHT)

    def test_mixed_types_partial_sheets_and_duplex_page_order(self) -> None:
        cards = tuple(
            Card(
                f"card-{index}",
                "running" if index % 2 == 0 else "mission",
                f"Unique task {index}",
                "Keep this task secret.",
            )
            for index in range(CARDS_PER_SHEET + 1)
        )
        prepared = prepare_deck(Deck("Sideplot", cards))
        for flip in ("long-edge", "short-edge"):
            with self.subTest(flip=flip):
                paths = write_pdfs(prepared, self.directory / flip, flip)
                with (
                    pdfium.PdfDocument(paths[0]) as fronts,
                    pdfium.PdfDocument(paths[1]) as backs,
                    pdfium.PdfDocument(paths[2]) as duplex,
                ):
                    self.assertEqual((len(fronts), len(backs), len(duplex)), (2, 2, 4))
                    for page_number in range(4):
                        with closing(duplex[page_number]) as page:
                            width, height = page.get_size()
                        self.assertAlmostEqual(width, PAGE_WIDTH, places=3)
                        self.assertAlmostEqual(height, PAGE_HEIGHT, places=3)
                    for sheet in range(2):
                        self.assertEqual(page_text(duplex, 2 * sheet), page_text(fronts, sheet))
                        self.assertEqual(page_text(duplex, 2 * sheet + 1), page_text(backs, sheet))
                    for index, card in enumerate(cards):
                        sheet, slot = divmod(index, CARDS_PER_SHEET)
                        front_text = text_in_slot(fronts, sheet, *slot_origin(slot))
                        back_text = text_in_slot(backs, sheet, *slot_origin(slot, "back", flip))
                        label = "RUNNING BIT" if card.kind == "running" else "MISSION"
                        self.assertEqual(front_text, f"{label} {card.title} {card.text}")
                        self.assertEqual(back_text, label)
                    for slot in range(1, CARDS_PER_SHEET):
                        self.assertEqual(text_in_slot(fronts, 1, *slot_origin(slot)), "")
                        self.assertEqual(
                            text_in_slot(backs, 1, *slot_origin(slot, "back", flip)), ""
                        )

    def test_generated_pdfs_are_reproducible(self) -> None:
        prepared = prepare_deck(
            Deck("Sideplot", (Card("test", "mission", "A task", "Ask about soup."),))
        )
        first = write_pdfs(prepared, self.directory / "first")
        second = write_pdfs(prepared, self.directory / "second")
        for original, regenerated in zip(first, second, strict=True):
            self.assertEqual(original.read_bytes(), regenerated.read_bytes())

    def test_playful_fonts_are_embedded_for_portable_printing(self) -> None:
        prepared = prepare_deck(
            Deck("Sideplot", (Card("test", "mission", "A task", "Ask about soup."),))
        )
        for path in write_pdfs(prepared, self.directory / "fonts"):
            with self.subTest(pdf=path.name):
                data = path.read_bytes()
                self.assertIn(b"+BalsamiqSans-Regular", data)
                self.assertIn(b"+BalsamiqSans-Bold", data)
                self.assertGreaterEqual(data.count(b"/FontFile2"), 2)

    def test_filter_rejects_an_empty_selection(self) -> None:
        deck = load_deck(self.write_deck([self.entry()]))
        with self.assertRaisesRegex(DeckError, "No cards match"):
            prepare_deck(deck, "mission")

    def test_overflow_exits_unsuccessfully_without_replacing_pdfs(self) -> None:
        path = self.write_deck([self.entry(text="A very long instruction. " * 200)])
        output = self.directory / "existing"
        output.mkdir()
        for filename in FILENAMES:
            (output / filename).write_bytes(b"existing file")
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "generate_cards.py"),
                "--cards",
                str(path),
                "--output",
                str(output),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("test-card", result.stderr)
        self.assertIn("does not fit", result.stderr)
        for filename in FILENAMES:
            self.assertEqual((output / filename).read_bytes(), b"existing file")

    def test_check_does_not_create_output(self) -> None:
        path = self.write_deck([self.entry()])
        output = self.directory / "not-created"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "generate_cards.py"),
                "--cards",
                str(path),
                "--output",
                str(output),
                "--check",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
