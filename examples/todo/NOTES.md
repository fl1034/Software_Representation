# To-do app: first attempt at a representation

`app.html` was built first, as an ordinary app, without the JSON in mind.
The three JSON files were then written by hand to describe it:

| File | What it shows |
|---|---|
| `snapshot-main.json` | Filter on "Active", a duplicate-title error, an undo toast counting down |
| `snapshot-confirm.json` | The "Clear done" confirmation dialog open over the list |
| `exchange.json` | An action sent by the agent and the app's diff reply, plus failure and stale cases |

## Choices made, and why

1. **Stable ids, not coordinates.** `task:3` stays `task:3` when the list re-renders,
   gets filtered or gets reordered. The agent acts by `target` + `action`.
2. **Item actions are declared once per list.** Each task row has a checkbox and a
   delete button. Repeating them per item would cost tokens and add nothing, so
   `tasks.item` says what *every* item can do and the items carry only data.
   This is the main token saving, and it grows with list length.
3. **Hidden affordances are named.** Rename is a double-click with no visible button.
   A screenshot can't show it, so it becomes an action, with `ui_hint` saying
   how a human would do it.
4. **What's off-screen is still accounted for.** `shown: 2, total: 4, limited_by: "filter"`
   tells the agent tasks are hidden and why. The duplicate error points at
   "Buy milk", which the filter hides. An agent reading only what's visible would be
   confused; this one knows to look.
5. **Consequences are stated before acting.** `confirm`, `undo_window_ms` and `danger`
   tell the agent whether an action is reversible and whether it will be asked to confirm.
   `clear_done` says it also deletes *hidden* done tasks, which a careful
   agent would want to know.
6. **Time is explicit.** The toast's `expires_in_ms` turns "there's an Undo button"
   into "there's an Undo button for about 4 more seconds".
7. **Modals collapse the background.** When the dialog is open, everything behind it
   is inert, so `snapshot-confirm.json` replaces the whole tree with a one-line
   `summary` and an `expand` hook. The agent sees only what it can act on.
8. **Constraints come before errors.** `max_length`, `unique` etc. let the agent avoid an
   invalid submit instead of discovering it.
9. **Replies are diffs, with a sequence number.** `seq` lets the app reject actions
   based on an outdated view (`stale`), and diffs keep follow-up turns small.
10. **`actions` is a list or a map.** A plain list (`["type", "clear"]`) for standard
    actions, a map when there's something worth saying. Saves tokens for the common case.

## Problems this exposed

- **Who writes `does` and `summary`?** They're the most useful fields and the ones no
  automatic adapter could produce from a DOM or accessibility tree. Either apps opt in
  (like ARIA), or an LLM writes them once per app and they get cached, or we accept
  thinner snapshots from adapters.
- **UI vs. data.** I described the *UI* (what a user can see and do), not the app's data
  model. Exposing the model (all four tasks, always) would be simpler for the agent,
  but then it's an API, not a view, and the agent can't tell what the human sees.
  I think both have a place; this format should probably stay UI-faithful and allow
  an optional `data` section.
- **Semantic vs. physical actions.** `rename` is semantic; underneath it's double-click,
  type, Enter. The format assumes the runtime can perform semantic actions. A pure
  observer (adapter that can only click and type) would need `ui_hint` to be
  machine-readable, not prose.
- **Roles are ad hoc.** `choice`, `status`, `toolbar` were picked on the spot. We'll
  need a small fixed vocabulary, probably borrowed from ARIA and trimmed down.
- **Visual-only meaning was dropped.** Strike-through on done tasks became
  `done: true`; that's the point. But some apps encode meaning purely in color or
  layout (a red row, a chart), and this example didn't test that.
- **Not measured yet.** I haven't compared token counts against a screenshot or a raw
  DOM/accessibility dump, or tested whether an agent can actually drive the app
  from these files alone.
