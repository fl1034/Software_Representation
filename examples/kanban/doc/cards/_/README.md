# Cards

Each card under `/cards`. Fields:

- `title`: text.
- `description`: text. Left out when empty.
- `labels`: ids from `/labels`. Left out when `[]`.
- `assignee`: an id from `/members`. Left out when unassigned (`null`).
- `due`: `YYYY-MM-DD`. Left out when there is no due date (`null`).
- `overdue`: computed by the app: `true` when `due` is before `/today` and the card is not
  in the last column. Left out when `false`.
- `checklist`: items `{"text", "done"}`, by id. Left out when empty.
- `comments`: `{"author", "text", "at"}`, by id. Left out when empty.
- `archived`: the id of the column the card was archived from. Left out when the card
  is on the board (`false`).
