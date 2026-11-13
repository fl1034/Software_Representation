# set

Write one or more cells in one submission: all of them or none.

Call: `{"action": "set", "path": "/sheets/<sheet id>/cells", "cells": {"C3": 500, "E3": "=SUM(B3:D3)"}}`
- `cells`: cell id to new content. A number, text, or a formula (text starting with `=`).
  `null` or `""` empties the cell.

Busy: the written cells and every formula that depends on them, on any sheet.

Changes: every cell whose content or value changed.

Errors:
- `bad_args`: a cell id outside the sheet; the message names it.
