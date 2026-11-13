# observe

Read any node of the tree. A query: changes nothing, answers at once.

Call: `{"action": "observe", "path": "<path>"}`, for example `/` or `/sheets/s1/cells/C3`.

Answer: `{"version": <n>, "node": <the node>}`. Busy nodes show their last
well-defined value, marked `busy` (see `README.md`).

Answers stay under 2 KB. To fit, the app replaces large nodes with
`{"api": [...], "folded": "<n> children, <size>"}`; observe that node's path to see it.
To control this yourself, see `view.md`.

A collection never shows more than 100 children. If it has more, it ends with
`"overflow": {"shown": 100, "total": <n>, "next": <call>}`: send `next` for the rest.

**Only what changed:** add `"since": <version>`. Then `node` holds only the parts
changed after that version, nested under their parents (anything not shown is
unchanged), and `"removed"` lists paths deleted since then. Fails with `too_old`
if the app no longer remembers that far back; observe without `since` instead.
