# delete_rows

Delete rows. The rows below move up by `count`, so their cells get new ids. Formulas that
pointed at a deleted cell show `#REF!`; ranges that lose rows shrink.

Call: `{"action": "delete_rows", "path": "/sheets/<sheet id>", "at": 4, "count": 1}`
- `at`: the first row to delete.
- `count`: optional, default 1. At least one row must remain.

Changes: the sheet's `rows`; deleted and moved cells; rewritten formula cells.

Errors:
- `last_row`
