# undo

Bring back the tasks removed by the last `delete` or `clear_done`, in their old positions. Only works within 6 seconds of that call.

Call: `{"action": "undo", "path": "/tasks"}`

Reply lists its changes: adds each restored task back.

Errors:
- `nothing_to_undo`
- `undo_expired`
