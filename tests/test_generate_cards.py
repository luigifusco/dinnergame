from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from ctypes import byref, c_float, c_int
from pathlib import Path

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
import yaml
from reportlab.lib.units import mm

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

    def group(self, kind: str, *identifiers: str) -> dict[str, object]:
        return {
            "type": kind,
            "theme": "INTERNAL AUTHORING THEME",
            "cards": [
                {"id": identifier, "title": f"Task {identifier}", "text": "Keep this task secret."}
                for identifier in identifiers
            ],
        }

    def write_collection(self, groups: dict[Path, dict[str, object]]) -> Path:
        root = self.directory / "library"
        root.mkdir(exist_ok=True)
        (root / "deck.yaml").write_text("name: Sideplot\n", encoding="utf-8")
        for relative, group in groups.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump(group), encoding="utf-8")
        return root

    def test_nested_groups_inherit_type_sort_stably_and_do_not_print_themes(self) -> None:
        first = self.group("running", "first")
        first.pop("theme")
        root = self.write_collection(
            {
                Path("mission") / "words.yml": self.group("mission", "third"),
                Path("running") / "nested" / "b.yaml": self.group("running", "second"),
                Path("running") / "a.yaml": first,
            }
        )
        (root / "notes.txt").write_text("Not a card file.", encoding="utf-8")
        deck = load_deck(root)
        self.assertEqual(
            [(card.id, card.kind) for card in deck.cards],
            [("first", "running"), ("second", "running"), ("third", "mission")],
        )
        paths = write_pdfs(prepare_deck(deck), self.directory / "nested-pdfs")
        with pdfium.PdfDocument(paths[0]) as fronts, pdfium.PdfDocument(paths[1]) as backs:
            for document in (fronts, backs):
                self.assertNotIn("INTERNAL AUTHORING THEME", page_text(document, 0))
            for slot, card in enumerate(deck.cards):
                label = "RUNNING BIT" if card.kind == "running" else "MISSION"
                self.assertEqual(
                    text_in_slot(fronts, 0, *slot_origin(slot)),
                    f"{label} {card.title} {card.text}",
                )
                self.assertEqual(text_in_slot(backs, 0, *slot_origin(slot, "back")), label)

    def test_duplicate_ids_across_files_report_both_sources(self) -> None:
        root = self.write_collection(
            {
                Path("first.yaml"): self.group("running", "duplicate"),
                Path("nested") / "second.yaml": self.group("mission", "duplicate"),
            }
        )
        with self.assertRaisesRegex(DeckError, "duplicate card id") as error:
            load_deck(root)
        self.assertIn("first.yaml", str(error.exception))
        self.assertIn("second.yaml", str(error.exception))

    def test_invalid_group_headers_and_card_type_overrides_are_rejected(self) -> None:
        cases = (
            ({"type": "missions"}, "'type'"),
            ({"theme": ""}, "'theme'"),
            ({"themes": "Misspelled field"}, "unknown field"),
            ({"cards": []}, "non-empty list"),
            ({"cards": [self.entry()]}, "unknown field"),
        )
        for overrides, message in cases:
            with self.subTest(overrides=overrides):
                group = self.group("running", "first")
                group.update(overrides)
                root = self.write_collection({Path("running.yaml"): group})
                with self.assertRaisesRegex(DeckError, message) as error:
                    load_deck(root)
                self.assertIn("running.yaml", str(error.exception))

    def test_collection_requires_metadata_and_at_least_one_card_file(self) -> None:
        root = self.directory / "empty"
        root.mkdir()
        with self.assertRaisesRegex(DeckError, "deck.yaml"):
            load_deck(root)
        (root / "deck.yaml").write_text("name: Sideplot\n", encoding="utf-8")
        with self.assertRaisesRegex(DeckError, "no card files"):
            load_deck(root)

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

    def test_sixteen_compact_cards_fit_with_readable_text_and_contained_artwork(self) -> None:
        cards = tuple(
            Card(
                f"compact-{index}",
                "running" if index % 2 == 0 else "mission",
                f"An unusually long task title {index}",
                "Get another player to explain a hobby, then ask a second player to add "
                "an example without changing the subject.",
            )
            for index in range(16)
        )
        prepared = prepare_deck(Deck("Sideplot", cards))
        paths = write_pdfs(prepared, self.directory / "compact")
        with (
            pdfium.PdfDocument(paths[0]) as fronts,
            pdfium.PdfDocument(paths[1]) as backs,
            pdfium.PdfDocument(paths[2]) as duplex,
        ):
            self.assertEqual((len(fronts), len(backs), len(duplex)), (1, 1, 2))
            for slot, item in enumerate(prepared.cards):
                label = "RUNNING BIT" if item.card.kind == "running" else "MISSION"
                self.assertEqual(
                    text_in_slot(fronts, 0, *slot_origin(slot)),
                    f"{label} {item.card.title} {item.card.text}",
                )
                self.assertGreaterEqual(item.text.style.fontSize, 9)

            backgrounds, medallions = [], []
            with closing(backs[0]) as page:
                for obj in page.get_objects(filter=[pdfium_c.FPDF_PAGEOBJ_PATH]):
                    fill, stroke = c_int(), c_int()
                    self.assertTrue(
                        pdfium_c.FPDFPath_GetDrawMode(obj.raw, byref(fill), byref(stroke))
                    )
                    if not fill.value:
                        continue
                    # The bounds helper has different names in pypdfium2 4 and 5.
                    left, bottom, right, top = c_float(), c_float(), c_float(), c_float()
                    self.assertTrue(
                        pdfium_c.FPDFPageObj_GetBounds(
                            obj.raw, byref(left), byref(bottom), byref(right), byref(top)
                        )
                    )
                    bounds = (left.value, bottom.value, right.value, top.value)
                    if stroke.value:
                        medallions.append(bounds)
                    else:
                        backgrounds.append(bounds)
            self.assertEqual(len(backgrounds), 16)
            self.assertEqual(len(medallions), 16)
            for slot, (background, medallion) in enumerate(
                zip(backgrounds, medallions, strict=True)
            ):
                with self.subTest(slot=slot):
                    x, y = slot_origin(slot, "back")
                    expected = (x + 2 * mm, y + 2 * mm, x + 86 * mm, y + 29.5 * mm)
                    for actual, target in zip(background, expected, strict=True):
                        self.assertAlmostEqual(actual, target, places=3)
                    self.assertGreaterEqual(medallion[0], background[0])
                    self.assertGreaterEqual(medallion[1], background[1])
                    self.assertLessEqual(medallion[2], background[2])
                    self.assertLessEqual(medallion[3], background[3])

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
