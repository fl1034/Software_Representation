# set_done

Tick or untick a checklist item.

Call: `{"action": "set_done", "path": "/cards/<card id>/checklist/<item id>", "done": true}`
- `done`: `true` or `false`.

Changes: sets `done`.

Errors:
- `card_archived`: restore the card first.
