# Tasks

You see the app as a JSON tree. Start with `observe` on `/` (see `observe.md`).

**Acting.** A node with `"api": [...]` lists what you can do to it. The doc for an
action is at `doc/<node path>/<action>.md`, with ids replaced by `_` (actions on the root: `doc/<action>.md`):
the doc for `rename` on `/tasks/3` is `doc/tasks/_/rename.md`.
A `"*"` key describes every child of its node; it is not a child itself.

**Calls** are JSON: `{"action": "<action>", "path": "<node path>", ...arguments}`.

**Queries** (`observe`, `view`, `page`, `find`, `listen`) change nothing and answer at once
with what's in the tree, at any time, even while parts of it are busy.

**Submissions** are every other action. Each one gets:
1. a **receipt** at once: `{"receipt": "<id>", "path": "<path>", "action": "<action>"}`,
   with `"feedback"` if there's something to say, and `"busy": [<paths>]` listing the
   nodes that are now busy;
2. a **ping** once the list reaches its next well-defined state:
   `{"ping": "<id>", "version": <n>, "changed": [<paths>], "removed": [<paths>]}`,
   with `"feedback"` if there's something to say. Observe with `since` to see new values.

If the list is ready at once, receipt and ping come as one message, with the ping
inside the receipt. Add `"wait": true` to any submission to always get them as one.

A submission that can't be carried out gets its error as feedback in the receipt:
`{"error": "<code>", "message": "<what to do>"}`. Its ping then has nothing changed.

Add `"version": <n>` to a submission to have it refused with `stale` if the list
has changed since version n.

**Busy nodes** have no well-defined value yet. They show their last value as
`{"busy": {"by": "<submission id>", "last": <value>}}`, and the root lists them under
`"busy"`. Submissions on a busy node get the error `busy`; listen for its ping and retry.
A busy marker may include `"progress": {"done": <n>, "total": <n>, "message": "..."}` when the
app can count its work (`total` may be missing). Progress sends no ping; observe to see it.

Long lists come back in batches of 100. `page` (see `page.md`) works on every
collection, meaning every node with a `"*"`, without being listed in its `api`.

Errors any submission can get: `unknown_action`, `bad_args`, `not_found`, `stale`, `busy`.
Each action's doc lists its other errors.
