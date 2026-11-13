# add

Add an empty sheet with 100 rows, after the existing ones.

Call: `{"action": "add", "path": "/sheets", "name": "<name>"}`
- `name`: optional; default `Sheet<n>`. Unique ignoring case, without `'` or `!`.

Changes: adds `/sheets/<new id>`.

Errors:
- `name_taken`, `bad_name`
