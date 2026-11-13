# Kanban board example

`app.html` is a kanban board, built before the format was designed: columns
with optional card limits, cards with labels, an assignee, a due date, a
checklist and comments, plus archive, restore and permanent delete.

- `state.json`: the full tree, about 2.1 KB. At a 2 KB budget, `observe /`
  folds `/columns`, the smallest node that is enough.
- `doc/`: one Markdown file per action, plus the app README and the cards item doc,
  26 files, about 0.4 KB each.
- `exchange.json`: an agent closing out a bug card, then hitting a card limit and a
  change made by someone else, clearing out Done with a slow `archive_all`,
  searching with `find`, and an overflowing list.

## What this example tested

- **Order separate from identity.** Cards live in `/cards`, and each column holds
  the order as a list of card ids. A move changes two lists; no card's path changes.
- **Nested `*`.** Checklist items have their own actions: `/cards/*/checklist/*`.
- **Item doc.** Most cards have no description, checklist or comments, and omit them.
  `overdue` is computed by the app. Both are explained once, in `doc/cards/_/README.md`.
- **References.** Assignees and labels are ids under `/members` and `/labels`.
- **Read-only branches.** Members and labels have no `api`; comments can only be paged.
- **Receipt, busy, ping.** Most actions settle at once, so receipt and ping arrive as one
  message. The sample session treats `archive_all` as slow: the receipt lists the busy
  nodes, an observation in between shows them marked busy, a move on a busy card is
  refused, and the ping arrives later. (In `app.html` it is instant too.)
- **Views.** The agent expands `/cards` and folds `/labels`. The app still folds
  `/columns` on its own to stay under budget, keeping its `api` visible, while the
  agent's own fold of `/labels` is bare.
- **Pings from others.** The agent listens on `/` and hears Priya's change as a ping,
  instead of discovering it through a `stale` error.

## Left out on purpose

Filters and search, which card is open, unsaved edits, label colours, avatars,
drag and drop. All of it exists to help a person look at the board.

## Behaviour that differs from the UI

- `archived` is `false` or the id of the column the card came from.
- `delete` on a card that isn't archived returns `not_archived`. The UI only offers
  "Delete forever" inside the archive.
- `set_labels` replaces the whole list. The UI toggles one label at a time.

## Size

The sample session's 21 messages total 6.8 KB. Before the compaction pass (no paths in
the tree, no echoes, item docs, compact JSON) the same session was 9.5 KB compact, or
16 KB indented. Part of today's figure is a better folding rule: the opening view now
folds only `/columns`, the smallest node that keeps it under budget, so the agent sees
every card at once instead of a stub for all of them.
