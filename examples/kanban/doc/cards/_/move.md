# move

Move a card to another column, or to another place in its own column.

Call: `{"action": "move", "path": "/cards/<card id>", "column": "<column id>", "position": 0}`
- `position`: 0-based, counting every card in the target column. Optional; default is last.

Reply lists its changes: sets `cards` of the old and new column, and the card's `overdue` if it changed (cards in the last column are never overdue).

Errors:
- `column_full`: the target column is at its `limit`. Moving within the same column is always allowed.
- `card_archived`: restore the card first.
