# A JSON protocol between AI agents and software

Software built for people shows them a screen. Software built for agents should show
them its state. This document describes how: a protocol in which software describes
itself as a JSON tree, lists what can be done to each part, documents each action in a
short Markdown file, and reports every change it makes. It is independent of any
particular application.

Part 1 gives the principles. Part 2 gives the rules that follow from them. Part 3 lists
every message shape.

---

## Part 1. Principles

### 1. Represent state, not screens

Windows, layouts, focus, scrolling, filters and spinners exist because a person can only
look at a few things at once. An agent has no such limit, and is good at finding one
item in a large amount of text. So the software describes its data and what can be done
to it, and nothing about how a person would see it. The agent decides what to look at.

### 2. The agent's context is the scarce resource

Everything the agent receives stays in its context window. Every byte must earn its
place:

- Messages are compact JSON.
- Nothing the agent already knows is sent back to it: no echo of its own call, no path
  that the position in the tree already gives.
- A fact that is always true is stated once, in documentation the agent reads when it
  needs it, never repeated in every message.
- Large things are never sent whole by default; the agent asks for what it needs.

### 3. The software is mechanical; the agent does the thinking

The software never guesses what is relevant. It follows fixed rules (size limits,
folding, overflow) that any program can implement and that the agent can predict. Where
judgement is needed, the agent supplies it, by choosing what to observe, what to expand
and what to fold.

### 4. Identity is stable

Every item has an id, and its path from the root is its address. Paths don't change when
other items are added, removed or reordered. Order, where it matters, is data (a list of
ids), not position. A reference from one item to another is that item's id.

Some domains really are positional, such as the cells of a grid. They may use positions
as ids, at a known cost: inserting or removing a position renames everything after it.

### 5. Disclose progressively

The tree says what can be done to each node, by name only. What an action does, its
arguments, its effects and its errors live in a short document for that action, read
only when the agent is about to use it. Facts about a kind of item (fields left out when
they have their default value, fields the software computes) live in one document for
that kind of item. A general document covers what every call shares, and is read first.

### 6. Asking and changing are different things

A **query** reads and changes nothing. It can be made at any moment, even while the
software is in the middle of something, and is answered at once with whatever is true
right now.

A **submission** asks the software to change something. Every submission goes through the
same three steps, whatever happens to it: a receipt, a busy period, and a ping when the
software reaches its next well-defined state. A refused submission is no exception: its
receipt carries the reason, its busy period lasts no time, and its ping reports that
nothing changed.

### 7. Unsettled state is data

While software works, part of its state has no well-defined value. A person sees a
spinner; an agent is told, precisely, which nodes are busy and what their last
well-defined value was. Progress is reported only when the software can genuinely count
its work, never estimated. Work that can be stopped says how to stop it.

### 8. Nothing changes silently

The tree changes only when a submission settles, and every change is reported in that
submission's ping. Busy markers cover nodes that already exist; they never add one.
Work that creates something long-running is therefore staged first, as an ordinary
submission whose ping announces the new item, and started second, so the agent can find
and watch the item before the work begins.

### 9. What is always true belongs in the documentation

Which nodes an action makes busy, whether it asks for confirmation, who may confirm it:
these are facts about the action, true every time. They are written in the action's
document, not repeated in every message about it.

### 10. Errors are feedback; error values are state

When a submission can't be carried out, the reason is feedback to whoever sent it, and
never enters the tree. When the domain itself has an error value (a formula that can't
be computed, a job that failed), that value is part of the state, and lives in the tree
like any other.

### 11. Three ways to hear about change

- **The receipt** answers the caller's own submission.
- **Listening** is optional and chosen path by path: busy events and pings for the parts of
  the tree an agent cares about, caused by anyone.
- **The alert channel** is mandatory and single: one per running software instance. Every
  client is on it. It is silent almost always, and goes off only when the software does
  what a frozen dialog would do on a person's screen: a submission waits for a yes or no,
  or the whole software stops.

### 12. People stay in the loop where it matters

A submission that shouldn't go ahead without a second look waits for confirmation. The
software can say who may give it: the agent that asked, or only a person. A confirmation
that nobody gives expires, and the submission is cancelled.

### 13. Concurrency is handled with versions, not locks

The tree has a version that counts well-defined states. An agent may make a submission
conditional on the version it last saw, and is refused if anything changed since. It can
ask for exactly what changed since a version. Supporting that takes bookkeeping, not
understanding: the software stamps what it writes.

### 14. In agent-native software, the protocol is the application

Software designed for agents has its state, actions and events defined by this protocol.
A human interface is one more client of it, with no state of its own, on equal terms
with agents.

---

## Part 2. Rules

Throughout, `<id>` stands for an item's id, and examples use made-up paths such as
`/jobs/j7`.

### 2.1 The tree

The software's state is one JSON tree. A node's **path** is the chain of keys from the
root, written `/jobs/j7/steps/s2`. Paths are never written into the tree; a node's path
is where it sits.

An item leaves out any field that has its default value. Where that happens, the item's
kind has an item document (2.3) listing each field and its default.

The software may include values it computes from other values, when that saves the agent
work. The item document says which fields are computed, and how.

**Reserved keys**, which can't be used as ids: `api`, `*`, `folded`, `overflow`, `busy`,
and on the root `app` and `alerts`.

### 2.2 Collections and arrays

A **collection** is a node whose children are items with ids, all of one kind. It always
has a `*` key, which describes every child at once and is not a child itself:

```json
"jobs": {
  "api": ["stage", "find"],
  "*": {"api": ["start", "discard"], "steps": {"*": {"api": ["skip"]}}},
  "j6": {"name": "Nightly export", "status": "done"},
  "j7": {"name": "Reindex", "status": "staged"}
}
```

`*` mirrors the shape of one child, and holds whatever is the same for every child: its
actions, and the actions and `*` of any collection inside it. These are written once
there, never repeated in each child. A collection whose children share nothing still has
`"*": {}`, so the agent can tell its children are ids.

An **array** is a plain list of values. It is always kept a legitimate JSON array (2.6).

### 2.3 Actions and documents

A node lists the names of the actions it accepts in `api`, or inherits them from the `*`
above it. Each action has a document: the doc for action `a` on node `/x/<id>/y` is
`doc/x/_/y/a.md`, the node's path with every id replaced by `_`. Actions on the root are
at `doc/<a>.md`.

An action document is short, in plain language, and covers one action:

- what it does;
- the exact call, with every argument and its rules;
- what it changes;
- which nodes it makes busy, if more than the called node;
- whether it asks for confirmation, and who may give it;
- its error codes beyond the common ones.

An **item document**, `doc/<collection path>/_/README.md`, describes one kind of item:
its fields, their defaults, and how computed fields are worked out. The agent reads it
before interpreting items of that kind.

The **general document**, `doc/README.md`, covers what every call shares. The agent reads
it first.

Built in, never listed in any `api`, documented at `doc/<action>.md`:

| Action | On | Kind |
|---|---|---|
| `observe` | any node | query |
| `view` | any node | query |
| `listen` | any node | query |
| `page` | any collection or array | query |
| `confirm` | the root | submission |
| `cancel` | the root | submission |

### 2.4 Calls

Every call is one JSON object: `{"action": "<action>", "path": "<node path>", ...arguments}`.
Queries are `observe`, `view`, `listen`, `page` and `find`. Everything else is a
submission.

### 2.5 Observing

`observe` returns the node at a path as it is now, busy markers included:

```json
{"action":"observe","path":"/jobs/j7"}
→ {"version":41,"node":{...}}
```

With `"since": <version>`, `node` holds only what changed after that version, nested under
its parents (anything not shown is unchanged), and `removed` lists paths deleted since
then. If the software no longer remembers that far back, the answer is the error
`too_old`, and the agent observes without `since`.

### 2.6 Size limits, folding and views

Every answer has a **size budget**, and every collection and array a **child limit**.
The software states its values in its general document. Two kilobytes and 100 are
reasonable defaults.

**Overflow.** A collection with more children than the limit shows the first ones, in
its own order, and a note with the exact call for the rest:

```json
"overflow":{"shown":100,"total":10000,"next":{"action":"page","path":"/jobs","after":"j100"}}
```

An array with more items than the limit keeps its first items and ends with a note, so it
stays an array: `["a","b","... 9998 more items"]`.

**Folding.** While an answer is over budget, the software replaces one node with a stub:
the smallest node whose folding alone brings the answer under budget or, if no single
node is enough, the largest node. Then it checks again. A stub still shows what can be
done there: the node's own `api`, and for a collection its children's `api` under `*`.
A child of a collection doesn't repeat an `api` that the collection's `*`, in view just
above it, already shows. An array is cut instead of folded: it keeps its first two items
and ends with a note of how many more.

```json
"jobs":{"api":["stage","find"],"*":{"api":["start","discard"]},"folded":"412 children, 38.0 KB"}
"j7":{"folded":"4 children, 0.3 KB"}
"tags":["urgent","billing","... 41 more items"]
```

**Views.** An agent can set any node to one of three views, each for itself only:

- `fold`: always the barest summary, `{"folded":"4 children"}`, or `["43 items"]` for an
  array.
- `expand`: never folded to save space, nor anything inside it or above it. Only the child
  limit still applies.
- `auto`: the default. The software folds by the rule above.

```json
{"action":"view","path":"/jobs","view":"expand"}
→ {"view":"expand"}
```

Observing a node by its own path always shows it, whatever its view.

**Paging.** `page` returns the children of a collection after a given id
(`"after":"j100"`). It is a cursor, so items added or removed meanwhile don't shift what
comes next. On an array, `after` is the number of items the agent already has
(`"after":100`).

**Finding.** A collection that could outgrow the child limit lists `find`, whatever its
current size. `find` returns the children whose fields equal the values given, and/or
whose text contains some words. Its document says which fields it searches, and may add
arguments of the software's own (a range, a date span).

### 2.7 Submissions

Every submission gets a **receipt** at once:

```json
{"receipt":"s57"}
{"receipt":"s54","feedback":{"error":"limit_reached","message":"The queue holds at most 20 jobs. Remove one first."}}
```

The receipt doesn't repeat the call or list what went busy; the action's document says
what it makes busy, and the agent can observe to see it.

From the moment the software receives the submission, the called node, and whatever the
action's document says it affects, is **busy** (2.8).

When the software reaches its next well-defined state, it sends a **ping**:

```json
{"ping":"s57","version":43,"changed":["/jobs/j7/status"],"removed":["/jobs/j6"]}
```

The ping names what changed, not the new values; the agent observes with `since` to see
them. Empty lists are left out. A list stops at the child limit and then gives the full
count as `changed_total` or `removed_total`. A refused submission's ping has nothing
changed, and the version stays the same.

If the next state is ready before anything has been sent, the caller gets receipt and
ping as one message, with the ping inside: `{"receipt":"s58","ping":{"version":44,...}}`.
With `"wait": true`, a submission always gets them as one message. When the submission
needs confirmation (2.10), there is nothing to wait for, so its receipt comes back at once.

With `"version": <n>`, a submission is refused with `stale` if the tree has moved past
version n.

**Feedback** is `{"error":"<code>","message":"..."}` for something that went wrong, or
just `{"message":"..."}`. The message is written for the agent, and says what to do next
where possible. Every submission can get the errors `unknown_action`, `bad_args`,
`not_found`, `stale` and `busy`.

### 2.8 Busy nodes

A busy node has no well-defined value yet. Observing it gives its last well-defined value,
marked:

```json
"j7":{"busy":{"by":"s57",
              "progress":{"done":44,"total":100,"message":"Copying files: 44 of 100"},
              "cancel":{"action":"cancel","path":"/","submission":"s57"},
              "last":{"name":"Reindex","status":"staged"}}}
```

- `progress` appears only when the software can count its work. `total` may be left out
  when it isn't known. Time remaining is never estimated. Progress changes nothing in the
  tree: it doesn't change the version and sends no ping.
- `cancel` appears when the work can be stopped.
- While anything is busy, the root lists the busy paths under `busy`, and a folded stub
  says how many busy nodes it hides.
- A submission on a busy node, or on a node inside one, is refused with `busy`. The
  software doesn't queue it; the agent listens for the ping and resubmits.

### 2.9 Staging long work

The tree changes only when a submission settles, and busy markers cover only nodes that
already exist. So work that creates something long-running takes two submissions:

1. **`stage`** creates the work item in a well-defined state, such as
   `"status":"staged"`. It settles at once, and its ping announces the new path:
   ```json
   {"action":"stage","path":"/jobs","name":"Reindex"}
   → {"receipt":"s56","ping":{"version":42,"changed":["/jobs/j7"]}}
   ```
   The agent now knows the id. It can observe the item, listen to it, change it, or discard
   it, before anything runs.
2. **`start`** on the staged item begins the work. Only now does the item go busy:
   ```json
   {"action":"start","path":"/jobs/j7"}
   → {"receipt":"s57"}
   ```

A confirmation belongs to `start`, never to `stage`: staging is always safe. Work on nodes
that already exist needs no staging; it just makes those nodes busy.

### 2.10 Alerts and confirmations

Every running software instance has one **alert channel**. Every client is on it from its
first call, and can't leave it. It carries nothing but alerts, and the end of a whole-app
freeze.

**A submission that needs confirming** makes its nodes busy as usual, and the software
sends this on the alert channel, to every client:

```json
{"alert":{"by":"s57","message":"Starting this deletes 3,112 files. This can't be undone.",
          "answer_by":"person","expires_in":300,
          "confirm":{"action":"confirm","path":"/","submission":"s57"},
          "cancel":{"action":"cancel","path":"/","submission":"s57"}}}
```

- `answer_by` is `caller` (the agent that made the submission may answer) or `person`
  (only a person, through the software's own interface). Anyone else's answer is refused
  with `not_yours`.
- `expires_in` is the number of seconds left. If nobody answers in time, the submission is
  cancelled.
- `confirm` and `cancel` are submissions that change nothing themselves; they get a receipt
  and an empty ping at once. The original submission then settles, and its ping reports
  what happened. After `cancel` or expiry, that ping says nothing changed.
- `cancel` also stops running work whose busy marker offers it.
- While it's open, the alert is also listed at the root under `alerts`, for any agent that
  joins late.

**An alert about the whole software** (restarting, out of licence, closing with unsaved
work) makes the whole tree busy (`"busy":["/"]`), and has a message but no answer:
`{"alert":{"by":"app","message":"Restarting for an update."}}`. Every submission
meanwhile is refused with `busy`. When it ends, the alert channel says so:
`{"ping":"app","version":43}`.

Alerts aren't data. Like busy markers, they appear and disappear without changing the
version.

### 2.11 Listening

`{"action":"listen","path":"/jobs"}` subscribes to every busy event and ping that touches
a path under `/jobs`, whoever caused it: another agent, a person, a timer, an outside
system. The answer is `{"listening":true}`.

A **busy event** names the submission, the action and the called node. The action's
document says what else it makes busy:

```json
{"busy":"s57","action":"start","path":"/jobs/j7"}
```

An agent doesn't get busy events for its own submissions, because it already has the
receipts. It gets the pings for its own submissions whether it listens or not. A
submission that settles at once sends listeners only its ping.

How messages travel (a socket, a stream, a long poll) is up to the software. Software that
can't push still marks busy nodes, so an agent can poll with `observe`.

### 2.12 Versions and change tracking

The version counts well-defined states. It goes up at each ping that changed something,
and never while nodes are busy. Every query answer and every ping carries it.

To answer `since`, the software stamps every node it writes, and every node above it,
with the new version, and keeps a marker for every node it deletes. It throws markers
away after a while, and answers `too_old` for versions older than what it kept.

---

## Part 3. Message reference

| Message | Sent to | Shape |
|---|---|---|
| Query answer | the caller | `{"version":41,"node":{...}}` |
| Query answer with `since` | the caller | `{"version":43,"node":{...changed parts...},"removed":[...]}` |
| `view` answer | the caller | `{"view":"expand"}` |
| `listen` answer | the caller | `{"listening":true}` |
| Query error | the caller | `{"error":"not_found","message":"..."}` |
| Receipt | the caller | `{"receipt":"s57"}`, with `"feedback"` and/or an inner `"ping"` |
| Busy event | listeners on an affected path, except the caller | `{"busy":"s57","action":"start","path":"/jobs/j7"}` |
| Ping | the caller, and listeners on an affected path | `{"ping":"s57","version":43,"changed":[...],"removed":[...]}`, with `"feedback"` |
| Alert | every client, on the alert channel | `{"alert":{"by":"s57","message":"...","answer_by":"person","expires_in":300,"confirm":{...},"cancel":{...}}}` |
| End of a whole-app alert | every client, on the alert channel | `{"ping":"app","version":43}` |

| Inside the tree | Shape |
|---|---|
| Collection | `{"api":[...],"*":{"api":[...]},"<id>":{...},...}` |
| Overflow note | `"overflow":{"shown":100,"total":10000,"next":{...call...}}` |
| Stub, folded by the software | `{"api":[...],"*":{"api":[...]},"folded":"412 children, 38.0 KB"}` |
| Stub, folded by the agent | `{"folded":"412 children"}` |
| Array, cut | `["a","b","... 9998 more items"]` |
| Array, folded by the agent | `["10000 items"]` |
| Busy node | `{"busy":{"by":"s57","progress":{...},"cancel":{...},"last":{...}}}` |
| Root lists | `"busy":["/jobs/j7"]`, `"alerts":[{...}]` |

---

## Open questions

- **Small values in pings.** A ping names changed paths but not their values, so the agent
  usually observes once more after acting. Including values under a small size would often
  save that call.
- **Mixed collections.** `*` assumes every child is the same kind. A collection that mixes
  kinds, such as files and folders, needs either a per-item `api` that overrides the
  shared one, or one `*` per kind.
- **Bulk renames under positional ids.** Inserting one position renames everything after
  it, and the ping lists every renamed path. Naming the nearest common ancestor instead,
  once a list passes the limit, would be simpler for both sides.
- **Staged items nobody starts.** Whether they expire, and how they are discarded, is left
  to each piece of software and its documents for now.
- **Long single values.** A large string, such as a document's text, can't be cut like an
  array without changing its type. Representing it as an array of lines works, but isn't
  required yet.
- **Values that change continuously,** such as a playback position or a sensor reading.
  Each change would be a new state, a version bump and a ping. They probably need a marker
  like `progress`: readable by observing, outside versions and pings.
- **Permissions.** With several users or roles, `api` should list only what the caller may
  do.
- **Content that isn't text,** such as images or audio. The tree can hold a reference and a
  description; how is not yet specified.
- **Who writes the documents.** Software could ship them, or a tool could generate them from
  the software's code.
