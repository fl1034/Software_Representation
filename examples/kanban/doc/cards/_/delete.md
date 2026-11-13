# delete

Delete an archived card for good. Cannot be undone.

Call: `{"action": "delete", "path": "/cards/<card id>"}`

Reply lists its changes: removes the card.

Errors:
- `not_archived`: archive it first.
