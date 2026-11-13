# Sheets

Each sheet under `/sheets`. Fields:

- `name`: what formulas use to refer to it (`Budget!E7`, or `'Q1 Budget'!E7` when the
  name has spaces).
- `rows`: how many rows the sheet has. Columns always go from A to Z.
- `cells`: the cells that aren't empty; see `doc/sheets/_/cells/_/README.md`.
