# find

Get only some cells of a sheet. Same answer as `observe`, with only the matching cells.

Call: `{"action": "find", "path": "/sheets/<sheet id>/cells", "range": "A1:F10", "text": "<words>"}`
- `range`: optional. Only cells inside it, like `A8:F8` for one row or `B1:B100` for a column.
- `text`: optional. Case-insensitive; matches a cell's text, number, formula or error.

Up to 100 cells per answer, with an `overflow` note whose `next` gets the rest.
