# assign

Assign a card to a member, or unassign it.

Call: `{"action": "assign", "path": "/cards/<card id>", "assignee": "u2"}`
- `assignee`: an id from `/members`, or `null`.

Reply lists its changes: sets `assignee`.

Errors:
- `unknown_member`: the message lists valid ids.
- `card_archived`: restore the card first.
