# add_checklist_item

Add an item to the end of a card's checklist. It starts not done.

Call: `{"action": "add_checklist_item", "path": "/cards/<card id>", "text": "<text>"}`
- `text`: non-empty.

Reply lists its changes: adds `/cards/<card id>/checklist/<new item id>`.

Errors:
- `empty_text`
- `card_archived`: restore the card first.
