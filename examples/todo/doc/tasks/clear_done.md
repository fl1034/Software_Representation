# clear_done

Delete every task that is done. Can be undone (see `undo.md`).

Call: `{"action": "clear_done", "path": "/tasks"}`

Reply lists its changes: removes each done task.

Errors:
- `nothing_done`
