# set_description

Replace a card's description.

Call: `{"action": "set_description", "path": "/cards/<card id>", "description": "<text>"}`
- `description`: any text; empty clears it.

Reply lists its changes: sets `description`.

Errors:
- `card_archived`: restore the card first.
