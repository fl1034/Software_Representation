# comment

Post a comment on a card as `/me`, dated `/today`. Comments can't be edited or deleted.

Call: `{"action": "comment", "path": "/cards/<card id>", "text": "<text>"}`
- `text`: non-empty.

Changes: adds `/cards/<card id>/comments/<new comment id>`.

Errors:
- `empty_text`
- `card_archived`: restore the card first.
