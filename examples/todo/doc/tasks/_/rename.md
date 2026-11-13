# rename

Change a task's title.

Call: `{"action": "rename", "path": "/tasks/<task id>", "title": "<title>"}`
- `title`: non-empty, at most 120 characters, not equal (ignoring case) to another task's title.

Changes: sets `title`.

Errors:
- `empty_title`, `title_too_long`, `duplicate_title`
