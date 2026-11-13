# cancel

Stop a submission that is waiting for confirmation. Built in on the root.

Call: `{"action": "cancel", "path": "/", "submission": "<submission id>"}`. The alert (on the alert
channel, and at the root) gives you this call ready to send, under `cancel`.

Its receipt and ping come at once with nothing changed. The cancelled submission's ping
then says nothing changed either, and its paths are no longer busy.

Errors:
- `not_found`: no open alert for that submission (it was answered, or it expired).
- `not_yours`: the alert's `answer_by` is `person`, or you aren't the caller.
