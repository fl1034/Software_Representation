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
the exact JSON call, its arguments, what it changes and its error codes. The agent
opens a doc only when it is about to use that action, so it never pays for
documentation it doesn't need.

`doc/README.md` covers what every call shares: queries and submissions, receipts
and pings, common errors, folding and versions. The root node points to it with `"docs"`.

### 4. Repeated children are described once

The reserved key `"*"` describes every child of a node whose children are ids (a
**collection**, see 8): its path pattern, its actions, and anything else shared.
It can nest (`/cards/*/checklist/*`).

### 5. Shared facts sit on `*`

- `defaults`: values of fields a child leaves out. Most cards have no checklist;
  they omit it instead of writing `"checklist": {}`.
- `derived`: fields the app computes, with a one-line rule.

### 6. Queries and submissions

A call is one JSON object. There are two kinds.

**Queries** read the tree and change nothing: `observe`, `page`, `find`, `view` to
choose how nodes are shown, and `listen` to subscribe to pings. An observation is just that: it can be made at any time, even
while parts of the tree are busy. It answers at once with what's in the tree right
now, busy markers included, and never waits for anything to settle (see 7 and 8).

**Submissions** are every other action, anything that may change the tree.
Every submission goes through the same steps, whatever happens to it:

1. **Receipt.** The app answers at once and gives the submission an id. This is the
   first chance for feedback.
2. **Busy.** From the moment the app receives the submission, the called node, and
   anything else the app's logic says the submission affects, is busy: for now it has
   no well-defined value.
3. **Ping.** When the next well-defined state arrives, the app sends a ping naming the
   submission, the new version, and every path that changed or was removed. This is
   the second chance for feedback.

A submission the app can't carry out (a full column, an unknown member, a bad argument)
is no exception. The receipt carries the error, the busy period lasts no time at all,
and the ping reports that nothing changed: `changed` is empty and the version stays
the same. Errors are feedback, never part of the tree.

The app sends the receipt and the ping whether anyone is listening or not. If the
next state is ready before the receipt goes out, it sends both as one message.

```json
{ "action": "archive_all", "path": "/columns/c4" }
→ { "receipt": "s57", "path": "/columns/c4", "action": "archive_all", "busy": ["/columns/c4", "/cards/k8"] }
   ... later, to anyone listening on those paths:
  { "ping": "s57", "version": 43, "changed": ["/columns/c4/cards", "/cards/k8/archived"], "removed": [] }

{ "action": "move", "path": "/cards/k6", "column": "c3" }
→ { "receipt": "s54", "path": "/cards/k6", "action": "move",
    "feedback": { "error": "column_full", "message": "Review is at its limit of 2 cards (k7, k4)." },
    "ping": { "version": 40, "changed": [], "removed": [] } }
```

A ping names what changed, not the new values. To see them, observe with `since`
(see 7), or observe the changed paths.

**Feedback** is `{ "error": "<code>", "message": "..." }` for something that went
wrong, or just `{ "message": "..." }`. Messages are written for the agent and say
what to do next where possible.

**Busy nodes.** Observing a busy node returns its last well-defined value, labelled:

```json
"c4": { "busy": { "by": "s57", "last": { "name": "Done", "limit": null, "cards": ["k8"] } } }
```

A busy marker may also carry `progress`, when the app genuinely knows how far along it
is. It counts real units of work, with an optional message for the agent:

```json
"c4": { "busy": { "by": "s57", "progress": { "done": 44, "total": 100, "message": "Archiving cards: 44 of 100" },
                  "last": { "name": "Done", "limit": null, "cards": ["k8", "..."] } } }
```

`total` may be left out when it isn't known (`{ "done": 44 }`). The app never estimates
time remaining or makes up a percentage; an app that can't count leaves `progress` out.
Progress is not a well-defined state: it doesn't change the version and sends no ping.
The agent sees it only by observing.

While anything is busy, the root lists it (`"busy": ["/columns/c4", "/cards/k8"]`), and
a folded stub says how many busy nodes it hides. A submission on a busy node gets a
receipt with feedback `busy` naming the submission it is waiting on, then a ping with
nothing changed. The app doesn't queue it; the agent can listen and resubmit.

**Waiting and listening.** `{ "action": "listen", "path": "/cards" }` subscribes to
every ping that touches a path under `/cards`, including those caused by other people,
other agents or timers. To wait for its own submission, an agent adds `"wait": true`;
the app then holds the receipt until the ping and sends them as one message.
How pings travel (a socket, a stream, a long poll) is up to the app. An app that
can't push still marks busy nodes, so the agent can poll with `observe`.

### 7. `observe` and folding

Every app has three built-in queries on the root: `observe`, `view` (below) and
`listen` (see 6), and one on every collection: `page` (see 8).

```json
{ "action": "observe", "path": "/cards/k4" }
→ { "path": "/cards/k4", "version": 41, "node": { ... } }
```

It returns the node at that path, as of the latest well-defined state. Each reply has a size budget. While a reply is over
budget, the app replaces the largest node in it with a stub that says how to see it.
A stub the app makes on its own always keeps the node's `path` and `api`, so the agent
can still see what it could do there:

```json
"cards": { "path": "/cards", "api": ["find"], "folded": "9 children, 1.9 KB. Observe /cards" }
```

The rule is mechanical: the app doesn't guess what the agent needs.

**Views: the agent chooses.** On top of the app's own folding, the agent can set any
node to one of three views:

```json
{ "action": "view", "path": "/cards", "view": "expand" }
```

- `fold`: shown as the barest summary, `{ "folded": "4 children" }`, wherever it appears
  in an observation.
- `expand`: shown in full. The app never folds it or anything inside it to save space;
  only the overflow limit (see 8) still applies. Nodes above it aren't folded either,
  so it stays in sight.
- `auto`: the default. The app decides, following the rule above.

A view is a query like `observe`: it changes nothing in the tree, can be set at any
moment, and goes through no receipt or ping. Views belong to the agent that sets them;
other agents never see them. The answer shows the node the way it will now appear.
Observing a node by its own path always shows it, whatever its view; `fold` only
governs how it appears inside other observations.

**`since`** returns only what changed after a given version:

```json
{ "action": "observe", "path": "/", "since": 42 }
→ { "path": "/", "version": 43, "since": 42,
    "node": { "columns": { "c4": { "cards": [] } }, "cards": { "k8": { "archived": "c4" } } },
    "removed": [] }
```

`node` holds only the changed parts, nested under their parents; anything not shown is
unchanged. `removed` lists paths deleted since then.

This takes no understanding of side effects from the app, only bookkeeping. Whenever
it writes a value, it stamps that node and every node above it with the new version.
Whenever it deletes one, it keeps a deletion marker for a while. `since` follows the
stamps down to whatever was written. Once deletion markers older than a version have
been thrown away, `since` for that version fails with `too_old`, and the agent
observes without it.

`tools/fold.py` is a reference implementation of the queries: folding, views,
`since`, overflow, `page` and `find`, including busy nodes.

### 8. Long lists: `overflow`, `page` and `find`

A **collection** is any node whose children are ids; it always has a `*` describing them.
A collection never returns more than 100 children. Two queries help with the rest:

- `page` is built in: it works on every collection, like `observe` works everywhere,
  and isn't listed in any `api`. It returns the children after a given id, in the
  collection's order. It uses a cursor (`"after": "k100"`), not a page number, so
  items added or removed meanwhile don't shift what comes next. Its doc is `doc/page.md`.
- `find` returns only the children whose fields equal the values given, and/or whose
  text contains some words. Deliberately simple: exact matches plus a text search.
  A collection that could grow past 100 always lists `find` in its `api`, whatever
  its current size.

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

The tree's `version` counts well-defined states: it goes up at each ping that
changed something, and never while nodes are busy. A submission may include
`"version": <n>`. If the tree has moved past version n, the receipt carries `stale`
and nothing changes. This guards against acting on an outdated view of the tree,
whoever changed it.

### Reserved keys

`path`, `api`, `*`, `defaults`, `derived`, `folded`, `overflow`, `busy`, and on the root
`app`, `version` and `docs`. They can't be used as ids.

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

With views: `/cards` expanded and `/labels` folded:

```bash
python3 tools/fold.py examples/kanban/state.json / --view /cards=expand --view /labels=fold
```

## Open questions

- **Who writes the docs?** Here they're written by hand. An app could ship them, or a
  tool could generate them from the app's code.
- **Not yet tested with a real agent.** Next step: give an agent only `doc/` and
  `observe`, connect it to the app, and compare its token use with a
  screenshot-driven run.
