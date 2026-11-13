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

## The format

### 1. The app is a JSON tree of its data

Only data the app actually has: no buttons, no screens. All messages are compact JSON,
with no indentation or spaces between tokens.

Each item has a stable id, and its **path** is the chain of keys from the root:
`/cards/k4/checklist/k4-i2`. Paths aren't written into the tree; a node's path is
where it sits. Paths never change when other items are added, removed or moved.
Where order matters, it is kept as a list of ids (a column's `"cards": ["k4", "k5"]`),
so moving an item doesn't change its path.

References between items are ids that point elsewhere in the tree
(`"assignee": "u2"` means `/members/u2`).

### 2. Collections

A **collection** is a node whose children are ids rather than fixed fields. It always
has a `"*"` key, which describes every child at once and is not a child itself:

```json
"columns": {
  "api": ["add"],
  "*": { "api": ["rename", "set_limit", "delete", "add_card", "archive_all"] },
  "c1": { "name": "Backlog", "limit": null, "cards": ["k1", "k2", "k3"] }
}
```

`*` mirrors the shape of one child, and holds whatever is the same for every child:
its `api`, and the `api` and `*` of any collection inside it (`/cards/*/checklist/*`).
Those are written once there, never repeated in each child. A collection whose
children share nothing still has `"*": {}`, so the agent can tell its children are ids.

### 3. Actions are listed in the tree and described in docs

A node the agent can act on lists the names of its actions in `api`. Each action has
its own small Markdown doc. The doc for action `a` on `/x/<id>/y` is `doc/x/_/y/a.md`:
the node's path, with ids replaced by `_`. Each doc covers one action in a few lines:
what it does, the exact JSON call, its arguments, what it changes and its error codes.
The agent opens a doc only when it is about to use that action.

Some things are true of every app, so they're never listed in any `api`:
`observe`, `view` and `listen` on the root, `page` on every collection, and `confirm`
and `cancel` on the root for answering alerts (see 6). Their docs are
`doc/observe.md`, `doc/view.md`, `doc/listen.md`, `doc/page.md`, `doc/confirm.md` and
`doc/cancel.md`.

`doc/README.md` covers what every call shares: queries and submissions, receipts and
pings, common errors. The agent reads it first.

### 4. Item docs: defaults and computed fields

To save space, an item leaves out any field that has its default value: most cards
have no checklist, so they don't write `"checklist": {}`. Some fields are computed by
the app rather than set by anyone (a card's `overdue`). A collection whose items do
either has an item doc, `doc/<collection>/_/README.md`, listing each field, its
default and how computed fields are worked out. The agent reads it before
interpreting the items. These facts never change, so they live in a doc read once
rather than in every observation.

### 5. Queries and submissions

A call is one JSON object: `{ "action": "<action>", "path": "<node path>", ...arguments }`.
There are two kinds.

**Queries** read the tree and change nothing: `observe`, `page`, `find`, `view` and
`listen`. An observation is just that: it can be made at any time, even while parts of
the tree are busy. It answers at once with what's in the tree right now, busy markers
included, and never waits for anything to settle. Answers don't repeat the call.

**Submissions** are every other action, anything that may change the tree. Every
submission goes through the same steps, whatever happens to it:

1. **Receipt.** The app answers at once with an id for the submission. This is the
   first chance for feedback.
2. **Busy.** From the moment the app receives the submission, the called node, and
   anything else the app's logic says the submission affects, is busy: for now it has
   no well-defined value.
3. **Ping.** When the next well-defined state arrives, the app sends a ping naming the
   submission, the new version, and the paths that changed or were removed. This is
   the second chance for feedback.

A submission the app can't carry out (a full column, an unknown member, a bad argument)
is no exception. The receipt carries the error, the busy period lasts no time at all,
and the ping reports that nothing changed. Errors are feedback, never part of the tree.

Both moments are public. When nodes go busy, the app tells the caller in its receipt,
and tells everyone listening on any of those paths with a busy event carrying the same
submission id and paths. When they settle, the ping goes to the caller and to everyone
listening, whether anyone is listening or not. So every agent can see when part of the
tree stops having a well-defined value, not only the one that caused it.

If the next state is ready before anything has been sent, the busy period was never
visible: the caller gets receipt and ping as one message, with the ping inside the
receipt, and listeners get only the ping.

```json
{"action":"archive_all","path":"/columns/c4"}
→ {"receipt":"s57","busy":["/columns/c4","/cards/k8"]}
   at the same moment, to anyone listening on those paths:
  {"busy":"s57","paths":["/columns/c4","/cards/k8"]}
   ... later, to the caller and anyone listening on those paths:
  {"ping":"s57","version":43,"changed":["/columns/c4/cards","/cards/k8/archived"]}

{"action":"move","path":"/cards/k6","column":"c3"}
→ {"receipt":"s54","feedback":{"error":"column_full","message":"Review is at its limit of 2 cards (k7, k4)."},"ping":{"version":40}}
```

Receipts don't repeat the call: the receipt answers the call just sent, and its id is
what the busy event and the ping refer to. Empty lists (`changed`, `removed`, `busy`,
`paths`) are left out. A list of paths stops at 100 and then gives the full count as
`changed_total`, `removed_total`, `busy_total` or `paths_total`; the agent observes for
the rest.

A ping names what changed, not the new values. To see them, observe with `since`
(see 7), or observe the changed paths.

**Feedback** is `{"error": "<code>", "message": "..."}` for something that went wrong,
or just `{"message": "..."}`. Messages are written for the agent and say what to do
next where possible.

**Busy nodes.** Observing a busy node returns its last well-defined value, labelled:

```json
"c4":{"busy":{"by":"s57","last":{"name":"Done","limit":null,"cards":["k8"]}}}
```

A submission that creates something that takes time (a build, an export) makes the new
node appear at once, busy, with no `last`, since it had no value before. The receipt's
`busy` list gives its path, so the caller knows the new id straight away.

When running work can be stopped, its busy marker offers the call that stops it:
`"cancel":{"action":"cancel","path":"/","submission":"s15"}`. The built-in `cancel`
(see 6) then stops the work, and the submission settles with whatever the app records for
stopped work (a cancelled build, say). Who may cancel is up to the app; its doc for
`cancel` says.

A busy marker may also carry `progress`, when the app genuinely knows how far along it
is. It counts real units of work, with an optional message for the agent:
`"progress":{"done":44,"total":100,"message":"Archiving cards: 44 of 100"}`.
`total` may be left out when it isn't known. The app never estimates time remaining or
makes up a percentage; an app that can't count leaves `progress` out. Progress is not a
well-defined state: it doesn't change the version and sends no ping. The agent sees it
only by observing.

While anything is busy, the root lists it (`"busy":["/columns/c4","/cards/k8"]`), and a
folded stub says how many busy nodes it hides. A submission on a busy node gets a
receipt with feedback `busy` naming the submission it is waiting on, then a ping with
nothing changed. The app doesn't queue it; the agent can listen and resubmit.

**Waiting and listening.** `{"action":"listen","path":"/cards"}` subscribes to every
busy event and ping that touches a path under `/cards`, including those caused by other
people, other agents or timers. An agent doesn't get a busy event for its own
submission; its receipt already says the same. To wait for its own submission, an agent adds `"wait": true`; the app
then holds the receipt until the ping and sends them as one message. How events travel
(a socket, a stream, a long poll) is up to the app. An app that can't push still marks
busy nodes, so the agent can poll with `observe`.

### 6. Alerts and confirmations

A person is warned with a dialog that blocks the screen. Here a warning is a sticker on
the tree, and what it blocks is shown the usual way: as busy nodes.

**A submission that needs confirming.** Some submissions shouldn't go ahead without a
second look, such as deleting something for good. The app makes the affected paths busy
as for any submission, and puts an alert at the root, where everyone observing sees it:

```json
"alerts":[{"by":"s88","message":"Deleting Q1 Budget breaks 5 formulas on Summary: they would show #REF!. This can't be undone.",
           "answer_by":"caller","expires_in":300,
           "confirm":{"action":"confirm","path":"/","submission":"s88"},
           "cancel":{"action":"cancel","path":"/","submission":"s88"}}]
```

- The caller's receipt carries the alert, and so does the busy event listeners get. A
  submission sent with `"wait": true` gets its receipt at once with the alert: there is
  nothing to wait for until someone answers.
- `confirm` and `cancel` are built in on the root, and not listed in any `api`. (`cancel`
  also stops running work whose busy marker offers it; see 5.) They are submissions that
  change nothing themselves: answering lets the original submission
  settle, and its ping reports what happened. After `cancel`, that ping says nothing
  changed.
- `answer_by` says who may answer: `caller` (the agent that submitted it) or `person`
  (only a person, through the app's own interface). This is how an app puts a person in
  the loop for dangerous actions. Anyone else's answer is refused with the error
  `not_yours`.
- `expires_in` is how many seconds are left. If nobody answers in time, the submission
  is cancelled and its ping says nothing changed.
- Only the affected paths are busy. Everyone else carries on working; on a shared app,
  one agent's pending delete doesn't freeze the others.

**An alert about the whole app.** Some warnings concern everything: the app is
restarting for an update, a licence has expired, a person is closing it with unsaved
work. Then the whole tree goes busy at once and the alert has no answer, only a message:

```json
"busy":["/"],
"alerts":[{"by":"app","message":"Restarting for an update. Back in about a minute."}]
```

Every submission meanwhile gets the error `busy`. When the alert ends, the app sends a
ping with `"app"` in place of a submission id: `{"ping":"app","version":43}`.

Alerts aren't data: like busy markers, they appear and disappear without changing the
version.

### 7. `observe`, folding and views

```json
{"action":"observe","path":"/cards/k4"}
→ {"version":41,"node":{...}}
```

`observe` returns the node at a path, as of the latest well-defined state. Each answer
has a size budget. While an answer is over budget, the app replaces a node with a stub:
the smallest node whose folding alone brings the answer under budget, or, if no single
node is enough, the largest node, and then it checks again. That way it hides as little
as it can. A stub the app makes on its own still shows what can be done there: the
node's own `api`, and for a collection its children's `api` under `*`:

```json
"cards":{"api":["find"],"*":{"api":["rename","move","archive"]},"folded":"9 children, 1.6 KB"}
```

When a single child of a collection is folded and the collection's `*` is in view just
above it, the child's stub doesn't repeat that `api`: `"k7":{"folded":"5 children, 0.2 KB"}`.

**Arrays stay arrays.** A plain array (a list of values, as opposed to a collection of
items with ids) is never replaced by an object. When the app cuts one short, it keeps the
first items and ends with a note of how many are left out; when the agent folds one, it
becomes a one-item array:

```json
"names":["item1","item2","... 2701 more items"]      cut by the app
"names":["2703 items"]                                folded by the agent
```

An array never shows more than 100 items, like a collection; to fit the budget the app
may cut it down to its first two. `page` gets the rest (see 8).

The rule is mechanical: the app doesn't guess what the agent needs. To see a folded
node, the agent observes its path.

**Views: the agent chooses.** On top of the app's own folding, the agent can set any
node to one of three views:

```json
{"action":"view","path":"/cards","view":"expand"}
→ {"view":"expand"}
```

- `fold`: shown as the barest summary, `{"folded":"4 children"}` (or `["4 items"]` for an
  array), wherever it appears in an observation.
- `expand`: shown in full. The app never folds it or anything inside it to save space;
  only the overflow limit (see 8) still applies. Nodes above it aren't folded either,
  so it stays in sight.
- `auto`: the default. The app decides, following the rule above.

A view is a query like `observe`: it changes nothing in the tree, can be set at any
moment, and goes through no receipt or ping. Views belong to the agent that sets them;
other agents never see them. The answer only confirms the view; the agent observes when
it wants to see the result. Observing a node by its own path always shows it, whatever
its view; `fold` only governs how it appears inside other observations.

**`since`** returns only what changed after a given version:

```json
{"action":"observe","path":"/","since":42}
→ {"version":43,"node":{"columns":{"c4":{"cards":[]}},"cards":{"k8":{"archived":"c4"}}}}
```

`node` holds only the changed parts, nested under their parents; anything not shown is
unchanged. `removed` lists paths deleted since then, and is left out when empty.

This takes no understanding of side effects from the app, only bookkeeping. Whenever
it writes a value, it stamps that node and every node above it with the new version.
Whenever it deletes one, it keeps a deletion marker for a while. `since` follows the
stamps down to whatever was written. Once deletion markers older than a version have
been thrown away, `since` for that version fails with `too_old`, and the agent
observes without it.

### 8. Long collections: `overflow`, `page` and `find`

A collection never shows more than 100 children. When it has more, it shows the first
100 and a note with the exact call for the next batch:

```json
"overflow":{"shown":100,"total":10000,"next":{"action":"page","path":"/cards","after":"k100"}}
```

The note appears only when children are actually left out.

- `page` is built in on every collection. It returns the children after a given id, in
  the collection's order. It uses a cursor (`"after": "k100"`), not a page number, so
  items added or removed meanwhile don't shift what comes next. It also works on an array
  that was cut short; there `after` is the number of items the agent already has
  (`"after": 100`), since array items have no ids.
- `find` returns only the children whose fields equal the values given, and/or whose
  text contains some words. Deliberately simple: exact matches plus a text search.
  A collection that could grow past 100 always lists `find` in its `api`, whatever its
  current size. Its doc says which fields it searches; an app may add its own
  arguments there (a spreadsheet might search a range of cells).

Both answer in the same shape as `observe`. The child limit applies first, then
folding keeps the answer under the size budget.

### 9. Versions

The tree's `version` counts well-defined states: it goes up at each ping that changed
something, and never while nodes are busy. Every query answer and ping carries it.
A submission may include `"version": <n>`. If the tree has moved past version n, the
receipt carries `stale` and nothing changes. This guards against acting on an outdated
view of the tree, whoever changed it.

### Reserved keys

`api`, `*`, `folded`, `overflow`, `busy`, and on the root `app` and `alerts`. They can't be
used as ids.

## Examples

The first three examples are apps built first, with a representation written afterwards:
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

- **Who writes the docs?** Here they're written by hand. An app could ship them, or a
  tool could generate them from the app's code.
- **Pings for bulk changes.** Inserting one row in a spreadsheet renames every cell
  below it, so the ping lists every one of them. The app could name their common
  ancestor instead (`"changed": ["/sheets/s1/cells"]`) when a list would pass the cap.
  See `examples/spreadsheet/NOTES.md`.
- **Small values in pings.** A ping names changed paths but not their values, so the
  agent usually observes once more after acting. Including values under a small size
  would often save that call.
- **Not yet tested with a real agent.** Give an agent only `doc/` and the queries,
  connect it to the app, and compare its token use with a screenshot-driven run.
