# observe

Read any node of the tree. Changes nothing.

Call: `{"action": "observe", "path": "<path>"}`, for example `/` or `/cards/k4`.

Reply: `{"ok": true, "version": <n>, "path": "<path>", "node": <the node>}`.

Replies stay under 2 KB. A child too large to fit is replaced by
`{"folded": "<summary>. Observe <its path>"}`; observe that path to see it.
