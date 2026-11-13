# delete

Delete an archived card for good. Cannot be undone.

Call: `{"action": "delete", "path": "/cards/<card id>"}`

Asks for confirmation first: an alert goes out on the alert channel, and the card is
busy until someone answers (see `doc/confirm.md`). Here `answer_by` is `caller`: you may confirm it
yourself, after checking it's what was asked.

Changes, once confirmed: removes the card.

Errors:
- `not_archived`: archive it first.
