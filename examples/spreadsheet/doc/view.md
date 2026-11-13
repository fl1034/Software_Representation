# view

Choose how a node is shown to you in observations from now on. A query: changes
nothing in the app, works at any time, and only affects what you see.

Call: `{"action": "view", "path": "<path>", "view": "expand"}`
- `view`: one of
  - `fold`: always shown as the barest summary, like `{"folded": "4 children"}`, or
    `["4 items"]` for an array.
  - `expand`: always shown in full. Never folded to save space; collections still
    stop at 100 children with an `overflow` note.
  - `auto`: the default. The app folds what it must to stay under 2 KB, keeping
    `api` visible.

Answer: `{"view": "<view>"}`. Observe to see the result.

Observing a node by its own path always shows it, whatever its view.
