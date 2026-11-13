# confirm

Let a submission that is waiting for confirmation go ahead. Built in on the root.

Call: `{"action": "confirm", "path": "/", "submission": "<submission id>"}`. The alert gives
you this call ready to send, under `confirm`.

It changes nothing itself, so its receipt and ping come at once with nothing changed.
The confirmed submission then settles, and its ping says what it changed.

Errors:
- `not_found`: no open alert for that submission (it was answered, or it expired).
- `not_yours`: the alert's `answer_by` is `person`, or you aren't the caller. Tell the
  person, who answers in the app.
