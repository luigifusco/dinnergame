# Rising Stakes

**The dough rises. So do the stakes.**

Everyone bakes their own focaccia, topped with ingredient cards won in
minigames, gambled, or traded. The [concept draft](FOCACCIA_PLAN.md) has the
rules, and the [ingredient list](INGREDIENTS.md) has the deck, the portions, and
the shopping list.

## Print the cards

The [print directory](print) contains the 80 ingredient cards of the autumn
deck, ready to print:

| File | Purpose |
|---|---|
| `rising-stakes-duplex.pdf` | Automatic double-sided printing: front 1, back 1, front 2, back 2. |
| `rising-stakes-fronts.pdf` | Front sheets only, for manual double-sided printing. |
| `rising-stakes-backs.pdf` | Matching back sheets in the same order as the fronts. |

| Setting | Value |
|---|---|
| Paper | A4, portrait, opaque card stock |
| Card size | Poker, 63 x 88 mm |
| Layout | Three by three, edge to edge: eight cards and one blank spare per sheet |
| Sheets | Ten: six Common (red back), three Fine (green), one Luxury (blue) |
| Duplex setting | Either flip; the back doesn't need to line up |
| Scaling | Actual size / 100%, not "fit to page" |

1. Print pages 1-2 of `rising-stakes-duplex.pdf` as a trial, and check that a
   card measures 63 mm across.
2. Print the rest on opaque card stock. On thin paper, the art shows through
   the back and gives the card away.
3. Cut straight from guide to guide. The guides are only in the margins, so cut
   every line in one direction first, keep the strips and the margin offcuts in
   place, or lay them back, and then cut across them.

The caption under each front gives its sheet number, tier, and back color, so
manually printed sheets are easy to match. The
[layout notes](FOCACCIA_PLAN.md#printing) explain the design, and
[sheet.png](mockups/sheet.png) previews the first sheet.

## Generate the PDFs

Use Python 3.10 or newer. From this directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\generate_cards.py
```

This regenerates all three PDFs in `print`. They're tracked in Git, so the deck
can be printed without setting up Python; regenerate them after changing the
cards, the art, or the rendering code. Add `--check` to validate the cards and
art without writing anything.

## Edit the cards

`cards\ingredients.yaml` lists the ingredients by tier, with the number of
copies of each:

```yaml
name: Rising Stakes
tiers:
  common:
    copies: 4
    ingredients:
      cherry-tomatoes: Cherry tomatoes
```

- The tiers are `common`, `fine`, and `luxury`. They print in that order, each
  on its own sheets with its own back.
- Each id uses lowercase letters, digits, and single hyphens, and names its
  illustration, `art\<id>.png`. The name is printed under the art.
- Keep the [ingredient list](INGREDIENTS.md) in step: labels and portions live
  there, not on the cards.

Names shrink to fit, down to 14 pt. Longer names, missing illustrations,
characters the font lacks, duplicate ids, and unknown fields are errors, reported
before anything is written.

Illustrations are square linocut-style PNGs on plain cream paper, with an empty
margin around the subject. The generator finds the subject, crops to it,
flattens the paper texture, and remaps the paper to one shared cream.

The playful **Chewy** font is bundled in `assets\fonts` and embedded in the
PDFs. The unmodified font comes from
[Google Fonts](https://github.com/google/fonts/tree/main/apache/chewy) under the
Apache License 2.0, included as `assets\fonts\LICENSE.txt`.

## Development

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests cover the deck's sheet layout and art, input validation, and the
PDFs: duplex page pairing, matching paper behind the art, and reproducible
output.
