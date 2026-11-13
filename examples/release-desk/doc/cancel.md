# cancel

Built in on the root. Two uses:

- **Answer an alert with no.** The submission waiting for confirmation is dropped: its
  ping says nothing changed, and its paths are no longer busy.
- **Stop running work.** A busy marker that offers `cancel` can be stopped. The
  submission then settles with whatever the app records for stopped work; a cancelled
  build is kept, with status `cancelled`.

Call: `{"action": "cancel", "path": "/", "submission": "<submission id>"}`. Alerts and busy
markers give you this call ready to send.

The cancel itself changes nothing, so its receipt and ping come at once. The cancelled
submission's own ping follows.

Errors:
- `not_found`: no open alert or cancellable work for that submission.
- `not_yours`: you didn't send it. A person can cancel anyone's work; an alert with
  `answer_by: person` can only be answered by a person.
