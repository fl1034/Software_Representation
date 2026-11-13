# Software Representation

A way for AI agents to see and operate software as JSON and small Markdown files,
instead of screenshots.

Screens exist because people can only look at a few things at once. An agent
doesn't have that limit, and it's good at finding one item in a large pile of text.
So an app here doesn't describe windows, layout, focus or filters. It describes
its data and what can be done to it. The agent decides what to look at.

The software is expected to be simple and mechanical. The agent does the thinking.
Everything the agent receives is kept as small as it can be: the point is to spare
the agent's context window.

## The protocol

The protocol is specified in [`SPEC.md`](SPEC.md): fourteen principles, the rules that
follow from them, and a reference of every message. It doesn't depend on any of the
examples below.

In short:

- The software is a JSON tree of its data. Each node lists the names of the actions it
  accepts; each action has a short Markdown document, read only when needed.
- **Queries** (`observe`, `page`, `find`, `view`, `listen`) read the tree at any moment.
  Answers have a size budget: the software folds what doesn't fit by a fixed rule, cuts
  long lists with a note of how to get the rest, and the agent can expand or fold any
  node for itself.
- **Submissions** always get a receipt, make nodes busy while the software works, and end
  with a ping listing what changed. The tree never changes without a ping; long work is
  staged before it starts.
- Every running instance has one alert channel, silent until a submission needs a yes or
  no, or the whole software stops. Confirmations can be reserved for a person.

## Examples

The examples were written while the protocol was being worked out, so each follows the
rules as they stood at the time, not all of `SPEC.md`. The first three are apps built
first, with a representation written afterwards:
the app itself (`app.html`), its tree (`state.json`), its docs (`doc/`) and a sample
session (`exchange.json`). The release desk is a live app built on the protocol.

- [`examples/todo`](examples/todo): a to-do list. Small enough that nothing folds.
- [`examples/kanban`](examples/kanban): a kanban board with columns, card limits,
  labels, members, checklists, comments and an archive.
- [`examples/spreadsheet`](examples/spreadsheet): a two-sheet budget with formulas,
  references between sheets, error values and row insert/delete. Its cells are
  addressed by position, which the other examples avoid.
- [`examples/release-desk`](examples/release-desk): built the other way round. The protocol
  came first: the app is the tree, its actions and its events, and the web page is just
  one client of it, like the agent. Builds and deploys take real time, production needs a
  person's approval, and a console shows every message the agent sends and receives.
  Open `index.html` in a browser.
- [`examples/macos/tree.json`](examples/macos/tree.json) and
  [`examples/vscode/tree.json`](examples/vscode/tree.json): a whole Mac, and VS Code
  running on it, each as a single answer to `observe /`.

`tools/fold.py` is a reference implementation of the queries (folding, views, `since`,
overflow, `page`, `find`, busy nodes) and of the bookkeeping behind receipts and pings.
In `state.json`, keys starting with `_` (the current version, item defaults) are
storage the tool never shows; a real app keeps these however it likes.

To see what `observe` returns:

```bash
python3 tools/fold.py examples/kanban/state.json /
```

Overflow, with the child limit lowered so this small board overflows:

```bash
python3 tools/fold.py examples/kanban/state.json /cards --max-children 3
```

```bash
python3 tools/fold.py examples/kanban/state.json /cards --find '{"where": {"assignee": "u2"}}'
```

With views: `/cards` expanded and `/labels` folded:

```bash
python3 tools/fold.py examples/kanban/state.json / --view /cards=expand --view /labels=fold
```

Add `--pretty` to any of these to indent the output for reading.

## Open questions

See the end of [`SPEC.md`](SPEC.md).
