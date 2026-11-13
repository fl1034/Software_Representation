# clear

Empty every cell in a range.

Call: `{"action": "clear", "path": "/sheets/<sheet id>/cells", "range": "B2:D6"}`
- `range`: a cell (`B9`) or a range (`B2:D6`).

Busy and changes: as for `set`. Cleared cells are listed under `removed`.
