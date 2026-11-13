# rename

Change a card's title.

Call: `{"action": "rename", "path": "/cards/<card id>", "title": "<title>"}`
- `title`: non-empty, at most 200 characters.

Reply lists its changes: sets `title`.

Errors:
- `empty_title`, `title_too_long`
- `card_archived`: restore the card first.
