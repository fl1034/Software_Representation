# rename

Rename a column.

Call: `{"action": "rename", "path": "/columns/<column id>", "name": "<name>"}`
- `name`: non-empty.

Changes: sets `name`.

Errors:
- `empty_name`
