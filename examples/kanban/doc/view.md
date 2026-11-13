# view

Choose how a node is shown to you in observations from now on. A query: changes
nothing in the app, works at any time, and only affects what you see.

Call: `{"action": "view", "path": "<path>", "view": "expand"}`
- `view`: one of
  - `fold`: always shown as the barest summary, like `{"folded": "4 children"}`.
  - `expand`: always shown in full. Never folded to save space; long lists are still
    cut at 100 with an `overflow` note.
  - `auto`: the default. The app folds what it must to stay under 2 KB, keeping
    `path` and `api` visible.

Answer: `{"path": "<path>", "version": <n>, "view": "<view>", "node": <the node as it will now appear>}`.

Observing a node by its own path always shows it, whatever its view.
