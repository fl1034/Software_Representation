# set_labels

Replace a card's labels with the ones given.

Call: `{"action": "set_labels", "path": "/cards/<card id>", "labels": ["l1", "l2"]}`
- `labels`: ids from `/labels`; `[]` removes all.

Changes: sets `labels`.

Errors:
- `unknown_label`
- `card_archived`: restore the card first.
