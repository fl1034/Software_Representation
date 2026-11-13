# observe

Read any node of the tree. Changes nothing.

Call: `{"action": "observe", "path": "<path>"}`, for example `/` or `/cards/k4`.

Reply: `{"ok": true, "path": "<path>", "action": "observe", "version": <n>, "node": <the node>}`.

Replies stay under 2 KB. A child too large to fit is replaced by
`{"folded": "<summary>. Observe <its path>"}`; observe that path to see it.

A node never lists more than 100 children. If it has more, the reply ends with
`"overflow": {"message": "...", "next": <call>}`: send `next` to get the following ones.

**Only what changed:** add `"since": <version>`. Then `node` holds only the parts
changed after that version, nested under their parents (anything not shown is
unchanged), and `"removed"` lists paths deleted since then. Fails with `too_old`
if the app no longer remembers that far back; observe without `since` instead.
