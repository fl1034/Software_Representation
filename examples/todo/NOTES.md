# To-do list example

`app.html` is an ordinary to-do app, built before the format was designed.
The rest describes it in the format from the repo's `README.md`:

- `state.json`: the full tree, about 0.4 KB. It fits in one `observe` reply.
- `doc/`: one Markdown file per action.
- `exchange.json`: a sample session.

## Left out on purpose

The filter (All / Active / Done), the "items left" count, the confirm dialog
and the undo toast. They're presentation. The agent can count or filter the
list itself.

## Behaviour that differs from the UI

- Renaming to an empty title returns `empty_title`. The UI silently keeps the old title.
- `clear_done` doesn't ask for confirmation; `undo` is the safety net.
- `clear_done` with nothing done returns `nothing_done`. The UI disables the button.
