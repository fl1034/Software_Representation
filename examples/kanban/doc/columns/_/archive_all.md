# archive_all

Archive every card in a column, for example to clear out "Done" at the end of a sprint.
Archived cards can be restored one by one (see `doc/cards/_/restore.md`).

Call: `{"action": "archive_all", "path": "/columns/<column id>"}`

Reply: confirmation only, with no list of changes. To see what changed, observe with
`since` set to the version you had before the call.

Errors:
- `column_empty`
