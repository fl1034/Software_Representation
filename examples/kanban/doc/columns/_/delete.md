# delete

Delete a column. It must be empty, and the board must keep at least one column.

Call: `{"action": "delete", "path": "/columns/<column id>"}`

Reply lists its changes: removes the column.

Errors:
- `column_not_empty`
- `last_column`
