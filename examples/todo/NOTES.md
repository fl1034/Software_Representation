# To-do app representation

`app.html` is an ordinary to-do app, built before any representation was designed.
`representation.json` describes it for an AI agent; `exchange.json` shows calls and replies.

## The idea

Describe what the app **is**, not what it looks like. With the UI stripped away,
this app is a list of tasks (title + done flag) that can be added to, renamed,
marked done, deleted, cleared of done tasks and undone. Layout, buttons, the filter,
the confirm dialog and the toast are presentation and are left out.

## Rules of the format

1. **The representation is a tree of the app's data.** Only nodes the agent can act on
   carry anything besides data.
2. **Every interactive node has a `path`:** its navigation path from the root, spelled
   with the actual keys of the tree (`/tasks`, `/tasks/items/3`). Task ids are stable,
   so a path keeps pointing at the same task after others are deleted.
3. **Every interactive node has an `api` section,** one entry per call, each with:
   - `call`: the exact JSON the agent sends, with `<placeholders>` for what it fills in.
     Rules on arguments live inside the placeholder
     (`<string: non-empty, ≤120 chars, unique ignoring case>`).
   - `reply`: the JSON the app sends back on success.
   - `errors`: the error codes this call can return beyond the common ones.
4. **Repeated children are documented once.** `items` holds the `path` pattern and `api`
   for every task; the tasks themselves are bare data.
5. **Replies have one shape**, defined once at the root under `reply`:
   - success: `{ "ok": true, "changes": [...] }`, where each change is
     `add`, `set` or `remove` at a path, so the agent can update its copy of the
     tree without re-reading it;
   - failure: `{ "ok": false, "error": "<code>", "message": "..." }`.
6. **No uniform schema beyond that.** Data nodes are whatever shape suits the app,
   to keep the representation small.

## Behaviour that differs from the UI

- Renaming to an empty title returns `empty_title`. The UI silently keeps the old
  title instead. An explicit error is better for an agent.
- `clear_done` deletes right away. The UI asks for confirmation first; for an agent,
  `undo` is the safety net.
- `clear_done` with nothing done returns `nothing_done`. The UI disables the button.

## Open questions

- **Order.** Tasks have a display order (undo restores a task to its old position).
  This relies on JSON object keys keeping their order. A list would be explicit
  but would make paths positional again.
- **Stale views.** If the app changes on its own (another user, a timer), a call can
  be based on an outdated tree. A version number on the tree and on each call
  would let the app refuse such calls.
- **Who writes the `api` sections?** Here they're written by hand. Apps could publish
  them themselves, or a tool could generate them from the app's code.
- **Size.** Not yet measured against a screenshot or an accessibility-tree dump.
