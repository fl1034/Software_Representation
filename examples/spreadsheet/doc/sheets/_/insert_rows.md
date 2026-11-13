# insert_rows

Insert empty rows. The rows from `at` down move down by `count`, so their cells get new
ids (`A4` becomes `A5`). Every formula that refers to a moved cell, on any sheet, is
rewritten to follow it, and ranges that span the insertion grow.

Call: `{"action": "insert_rows", "path": "/sheets/<sheet id>", "at": 4, "count": 1}`
- `at`: the row number the new rows take, from 1 to `rows` + 1.
- `count`: optional, default 1, at most 1000.

Changes: the sheet's `rows`; every moved cell (old ids removed, new ids changed);
rewritten formula cells.
