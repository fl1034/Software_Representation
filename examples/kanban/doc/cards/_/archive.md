# archive

Take a card off the board without deleting it.

Call: `{"action": "archive", "path": "/cards/<card id>"}`

Reply lists its changes: sets the column's `cards`, and sets the card's `archived` to the id of the column it was in.

Errors:
- `card_archived`: already archived.
