# Kanban board representation

`app.html` is a kanban board, built before the representation was designed:
columns with optional card limits, cards with labels, an assignee, a due date,
a checklist and comments, plus archive, restore and permanent delete.
`representation.json` describes it for an agent; `exchange.json` shows an agent
working through a small task.

## What the to-do format needed to handle this app

**1. Entities and order live in different places.**
Nesting cards under their column would change a card's path every time it moved.
So cards live in one map, `/cards/<card id>`, and their paths never change.
Each column holds the order as a plain list of ids: `"cards": ["k4", "k5", "k6"]`.
`move` takes a column and an optional position. This also answers the to-do app's
open question about order: a list of ids is explicit, and paths stay stable.

**2. `items` was replaced by `*`.**
Two levels of `items` gave paths like `/cards/items/k4/checklist/items/k4-i2`.
Now a node's children sit directly under it, and the reserved key `*` documents
every child at once: `/cards/k4/checklist/k4-i2`. A `*` block can contain its own
nested `*` blocks (checklist items inside cards).

**3. Omitted fields have stated defaults.**
Most cards have no description, no checklist, no comments. Writing them out empty
would cost space on every card, so `*` lists `defaults` once and cards leave
out any field that matches.

**4. Derived values are included and labelled.**
`overdue` could be computed from `due`, `today` and the last column, but the
agent would have to know the rule and work it out for every card. It's cheap to
include, so it is, and `derived` says how it's computed. Replies recompute it.

**5. References point into the tree.**
`assignee: "u2"` and `labels: ["l1"]` are ids under `/members` and `/labels`.
Placeholders say where valid ids come from (`<member id from /members>`), and a
bad id gets a specific error (`unknown_member`) listing the valid ones.

**6. Read-only branches have no `api`.**
The app can't manage members or labels, so those branches are plain data.
Comments can be added but not edited, so they have no `*` block.

**7. The human's unsaved work is visible.**
`/human` shows that the person using the app has card k4 open with an unsaved
description. It isn't part of the data and the agent can't change it, but an agent
calling `set_description` on k4 now would collide with what the person is typing.

## Left out on purpose

Filters and search, label colours, avatars, the drag-and-drop mechanics and
the card-count display. They are presentation. The archived-cards list is covered
by `archived` on each card.

## Behaviour that differs from the UI

- `archived` is `false` or the id of the column the card came from, instead of two
  fields. The UI stores both.
- `delete` on a card that isn't archived returns `not_archived`. The UI only shows
  "Delete forever" inside the archive.
- `set_labels` replaces the whole list. The UI toggles one label at a time.
  For an agent, one call is simpler than several.

## Open questions

- **Who sees the agent's changes?** If the person has k4 open, should the app warn
  them, or refuse the agent's `set_description` (an `unsaved_changes` error)?
  `/human` makes the conflict visible but doesn't settle it.
- **Size.** About 10 KB, of which about 7 KB is `api` documentation that doesn't grow
  with the number of cards. A second snapshot of the same board could leave the
  `api` sections out entirely, if the agent has already seen them once.
  That would make the format two parts: a one-time manual and repeated state.
- **Position after filtering.** `position` counts all cards in the column. An agent
  that knows the person is looking at a filtered view might mean a different position.
