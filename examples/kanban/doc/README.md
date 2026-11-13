# Sprint Board

You see the app as a JSON tree. Start with `observe` on `/` (see `observe.md`).

**Acting.** A node with `"api": [...]` lists what you can do to it. The doc for an
action is at `doc/<node path>/<action>.md`, with ids replaced by `_` (actions on the root: `doc/<action>.md`):
the doc for `rename` on `/cards/k4` is `doc/cards/_/rename.md`.
A `"*"` key describes every child of its node; it is not a child itself.

**Calls** are JSON: `{"action": "<action>", "path": "<node path>", ...arguments}`.
Add `"version": <n>` to any call to have it refused with `stale` if the
board has changed since version n.

**Replies** name the element and action, and come back when the action is done:
- Success: `{"ok": true, "path": "<path>", "action": "<action>", "version": <n>}`.
  Most actions also give `"changes": [...]`, the complete list of what changed, each
  `{"op": "add" | "set" | "remove", "path": "<path>", "value": <value>}` (no `value` for
  `remove`). Apply them to your copy of the tree. An action's doc says whether it lists
  its changes; if it doesn't, observe with `since` to find out.
- Failure: `{"ok": false, "path": "<path>", "action": "<action>", "error": "<code>", "message": "<explanation>"}`.

Long lists come back in batches of 100; see `observe.md`.

Any call can fail with `unknown_action`, `bad_args`, `not_found` or `stale`.
Each action's doc lists its other errors.
