# add_card

Create a card at the bottom of a column. It starts with only a title; use the card's own actions to fill it in.

Call: `{"action": "add_card", "path": "/columns/<column id>", "title": "<title>"}`
- `title`: non-empty, at most 200 characters.

Reply lists its changes: adds `/cards/<new id>` and sets the column's `cards`.

Errors:
- `empty_title`, `title_too_long`
- `column_full`: the column is at its `limit`.
