# Cells

The cells of one sheet, under `/sheets/<sheet id>/cells`. Empty cells are left out.

**Ids are positions:** `A1` to `Z<rows>`. Unlike other ids, they change when rows are
inserted or deleted above them. Cells are listed, and paged, in row order: A1, B1, ..., A2.

**Values:**
- A plain cell is its value: a number (`410`) or text (`"Groceries"`).
- A formula cell is `{"f": "<formula>", "v": <value>}`. `v` is computed by the app.
- A formula that fails is `{"f": "<formula>", "e": "<error>"}`, where the error is one of
  `#DIV/0!`, `#REF!` (refers to a deleted cell or sheet), `#VALUE!` (text where a number
  is needed), `#NAME?` (unknown function), `#CYCLE!` (refers to itself, directly or not)
  or `#ERROR!` (can't be read). This is the cell's value, not a failed submission.

**Formulas** start with `=`: numbers, `+ - * / ^`, parentheses, cell references (`B3`),
ranges (`B2:B6`), references to other sheets (`Budget!E7`, `'Q1 Budget'!E7`), and the
functions `SUM`, `AVERAGE`, `MIN`, `MAX`, `COUNT` (these skip text and empty cells),
`ROUND(x, digits)` and `ABS`. An empty cell counts as 0 in arithmetic.

Changing a cell makes it and every formula that depends on it, on any sheet, busy until
recalculation finishes.
