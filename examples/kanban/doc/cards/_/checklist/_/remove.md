# remove

Remove a checklist item.

Call: `{"action": "remove", "path": "/cards/<card id>/checklist/<item id>"}`

Reply lists its changes: removes the item.

Errors:
- `card_archived`: restore the card first.
