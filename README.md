# Software Representation

A way for AI agents to see and operate software as JSON and small Markdown files,
instead of screenshots.

Screens exist because people can only look at a few things at once. An agent
doesn't have that limit, and it's good at finding one item in a large pile of text.
So an app here doesn't describe windows, layout, focus or filters. It describes
its data and what can be done to it. The agent decides what to look at.

The software is expected to be simple and mechanical. The agent does the thinking.

## The format

### 1. The app is a JSON tree of its data

Only data the app actually has: no buttons, no screens. Values that could be worked
out from other data may be included when that saves the agent work, and are
labelled under `derived` (see 5).

Each item has a stable id, and its **path** is the chain of keys from the root:
`/cards/k4/checklist/k4-i2`. Paths never change when other items are added,
removed or moved. Where order matters, it is kept as a list of ids
(a column's `"cards": ["k4", "k5"]`), so moving an item doesn't change its path.

References between items are ids that point elsewhere in the tree
(`"assignee": "u2"` means `/members/u2`).

### 2. Actions are listed, not described, in the tree

A node the agent can act on carries its path and the names of its actions:

```json
"columns": { "path": "/columns", "api": ["add"], ... }
```

### 3. Each action has its own small Markdown doc

The doc for action `a` on node path `/x/<id>/y` is `doc/x/_/y/a.md`: the same
path, with ids replaced by `_`. Actions on the root are at `doc/<action>.md`.

Each doc covers one action in a few lines of plain language: what it does,
the exact JSON call, its arguments, what it changes and its errors. The agent
opens a doc only when it is about to use that action, so it never pays for
documentation it doesn't need.

`doc/README.md` covers what every call shares: call and reply shapes, common
errors, folding and versions. The root node points to it with `"docs"`.

### 4. Repeated children are described once

The reserved key `"*"` describes every child of a node: its path pattern, its
actions, and anything else shared. It can nest (`/cards/*/checklist/*`).

### 5. Shared facts sit on `*`

- `defaults`: values of fields a child leaves out. Most cards have no checklist;
  they omit it instead of writing `"checklist": {}`.
- `derived`: fields the app computes, with a one-line rule.

### 6. Calls and replies

Every call is one JSON object:

```json
{ "action": "move", "path": "/cards/k4", "column": "c3" }
```

Replies:

```json
{ "ok": true, "version": 39, "changes": [{ "op": "set", "path": "/columns/c3/cards", "value": ["k7", "k4"] }] }
{ "ok": false, "error": "column_full", "message": "Review is at its limit of 2 cards (k7, k4)." }
```

A success lists every change as `add`, `set` or `remove` at a path, so the agent can
update what it already knows without observing again. Errors have a fixed code and
a message written for the agent, which says what to do next where possible.

### 7. `observe` and folding

Every app has one built-in action on the root:

```json
{ "action": "observe", "path": "/cards/k4" }
```

It returns the node at that path. Each reply has a size budget. While a node is over
budget, the app replaces its largest child with a stub that says how to see it:

```json
"cards": { "folded": "9 children, 1.8 KB. Observe /cards" }
```

The rule is mechanical: the app doesn't guess what the agent needs.
`tools/fold.py` is a reference implementation of folding, overflow, `page` and `find`.

### 8. Long lists: `overflow`, `page` and `find`

A node never returns more than 100 children. Any collection that could grow past
that always lists `page` and `find` in its `api`, whatever its current size:

- `page`: the children after a given id, in the collection's order. It uses a cursor
  (`"after": "k100"`), not a page number, so items added or removed meanwhile
  don't shift what comes next.
- `find`: only the children whose fields equal the values given, and/or whose text
  contains some words. Deliberately simple: exact matches plus a text search.

Both reply in the same shape as `observe`. Only when a reply actually leaves children
out does it carry a note, including the exact call for the next batch:

```json
"overflow": {
  "message": "Showing 100 of 10000 children. Send `next` for more, or narrow it down with find (doc/cards/find.md).",
  "next": { "action": "page", "path": "/cards", "after": "k100" }
}
```

The child limit applies first, then folding keeps the reply under the size budget.

### 9. Versions

The tree has a `version` number that goes up with every change. Any call may
include `"version": <n>`. If the data has changed since then, the call fails with
`stale`. This covers anything else changing the data: a person, another agent,
a sync job.

### Reserved keys

`path`, `api`, `*`, `defaults`, `derived`, `folded`, `overflow`, and on the root `app`,
`version` and `docs`. They can't be used as ids.

## Examples

Each example has the app itself (`app.html`), its full tree (`state.json`), its docs
(`doc/`) and a sample session (`exchange.json`).

- [`examples/todo`](examples/todo): a to-do list. Small enough that nothing folds.
- [`examples/kanban`](examples/kanban): a kanban board with columns, card limits,
  labels, members, checklists, comments and an archive.

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

## Open questions

- **Who writes the docs?** Here they're written by hand. An app could ship them, or a
  tool could generate them from the app's code.
- **Not yet tested with a real agent.** Next step: give an agent only `doc/` and
  `observe`, connect it to the app, and compare its token use with a
  screenshot-driven run.
