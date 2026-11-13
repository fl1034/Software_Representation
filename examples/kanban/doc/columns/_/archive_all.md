# archive_all

Archive every card in a column, for example to clear out "Done" at the end of a sprint.
Archived cards can be restored one by one (see `doc/cards/_/restore.md`).

Call: `{"action": "archive_all", "path": "/columns/<column id>"}`

Can take a while on a big column. Until the ping, the column and every card in it are busy.

Changes: the column's `cards`, and each card's `archived`.

Errors:
- `column_empty`
