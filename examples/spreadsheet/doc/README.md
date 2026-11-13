# Household Budget

You see the app as a JSON tree. Start with `observe` on `/` (see `observe.md`).
All messages are compact JSON.

**Acting.** A node with `"api": [...]` lists what you can do to it. The doc for an
action is at `doc/<node path>/<action>.md`, with ids replaced by `_`: the doc for
`rename` on `/sheets/s1` is `doc/sheets/_/rename.md`. A `"*"` describes every child of its node
(the node is a **collection**); it is not a child itself. Built in, and not listed in
any `api`: `observe`, `view` and `listen` on the root, `page` on every collection.

**Items.** Before reading a collection's items, read `doc/<collection>/_/README.md` if it
exists: it says what fields an item leaves out when they have their default value, and
which fields the app computes.

**Calls** are JSON: `{"action": "<action>", "path": "<node path>", ...arguments}`.

**Queries** (`observe`, `view`, `page`, `find`, `listen`) change nothing and answer at
once with what's in the tree, at any time, even while parts of it are busy.

**Submissions** are every other action. Each one gets:
1. a **receipt** at once: `{"receipt": "<id>"}`, plus `"busy": [<paths>]` for nodes that
   are now busy and `"feedback"` if there's something to say;
2. a **ping** once the workbook reaches its next well-defined state:
   `{"ping": "<id>", "version": <n>, "changed": [<paths>], "removed": [<paths>]}`, plus
   `"feedback"` if there's something to say. Empty lists are left out. A list stops at
   100 paths and then gives the full count as `changed_total` or `removed_total`.
   Observe with `since` to see new values.

If the workbook is ready at once, receipt and ping come as one message, with the ping
inside the receipt. Add `"wait": true` to any submission to always get them as one.

A submission that can't be carried out gets its error as feedback in the receipt:
`{"error": "<code>", "message": "<what to do>"}`. Its ping then has nothing changed.

Add `"version": <n>` to a submission to have it refused with `stale` if the workbook
has changed since version n.

**Busy nodes** have no well-defined value yet. They show their last value as
`{"busy": {"by": "<submission id>", "last": <value>}}`, and the root lists them under
`"busy"`. A busy marker may include `"progress": {"done": <n>, "total": <n>, "message": "..."}`
when the app can count its work (`total` may be missing); progress sends no ping.
Submissions on a busy node get the error `busy`; listen for its ping and retry.
If you listen (see `listen.md`), you're told when other submissions make nodes busy.

**Alerts.** A submission that needs confirming makes its paths busy and puts an alert on
the root, under `"alerts"`; your receipt carries it too. It says what will happen, who may
answer (`answer_by`: `caller` or `person`), how many seconds are left (`expires_in`), and
gives the `confirm` and `cancel` calls ready to send (see `confirm.md`, `cancel.md`).
An alert about the whole app has only a message, and makes everything busy (`"busy": ["/"]`)
until it ends.

Errors any submission can get: `unknown_action`, `bad_args`, `not_found`, `stale`, `busy`.
Each action's doc lists its other errors.
