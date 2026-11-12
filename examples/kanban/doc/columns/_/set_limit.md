# set_limit

Set or remove the most cards a column may hold.

Call: `{"action": "set_limit", "path": "/columns/<column id>", "limit": 3}`
- `limit`: at least 1 and at least the number of cards already in the column, or `null` for no limit.

Changes: sets `limit`.

Errors:
- `limit_too_low`
