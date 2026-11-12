# set_due

Set or clear a card's due date.

Call: `{"action": "set_due", "path": "/cards/<card id>", "due": "2026-11-30"}`
- `due`: `YYYY-MM-DD`, or `null`.

Changes: sets `due`, and `overdue` if it changed.

Errors:
- `bad_date`
- `card_archived`: restore the card first.
