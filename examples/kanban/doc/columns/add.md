# add

Add a column at the right end of the board.

Call: `{"action": "add", "path": "/columns", "name": "<name>", "limit": 3}`
- `name`: non-empty.
- `limit`: maximum number of cards, at least 1. Optional; leave it out or send `null` for no limit.

Changes: adds `/columns/<new id>` with no cards.

Errors:
- `empty_name`
