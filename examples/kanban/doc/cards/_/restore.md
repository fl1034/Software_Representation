# restore

Put an archived card back at the bottom of the column it came from, or of the first column if that one was deleted.

Call: `{"action": "restore", "path": "/cards/<card id>"}`

Changes: sets `archived` to `false` and sets the column's `cards`.

Errors:
- `not_archived`
- `column_full`
