# add

Add a task at the end of the list. It starts not done.

Call: `{"action": "add", "path": "/tasks", "title": "<title>"}`
- `title`: non-empty, at most 120 characters, not equal (ignoring case) to another task's title.

Changes: adds `/tasks/<new id>`.

Errors:
- `empty_title`, `title_too_long`
- `duplicate_title`: the message gives the path of the existing task.
