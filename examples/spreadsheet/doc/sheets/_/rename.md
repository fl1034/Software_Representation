# rename

Rename a sheet. Formulas anywhere that refer to it by name are rewritten to the new name;
their values don't change.

Call: `{"action": "rename", "path": "/sheets/<sheet id>", "name": "<name>"}`
- `name`: unique ignoring case, without `'` or `!`.

Changes: the sheet's `name`, and every formula cell that named it.

Errors:
- `name_taken`, `bad_name`
