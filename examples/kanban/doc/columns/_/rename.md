# rename

Rename a column.

Call: `{"action": "rename", "path": "/columns/<column id>", "name": "<name>"}`
- `name`: non-empty.

Reply lists its changes: sets `name`.

Errors:
- `empty_name`
