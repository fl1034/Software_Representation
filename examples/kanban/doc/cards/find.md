# find

Get only the cards that match. Same reply as `observe`, with only the matches.

Call: `{"action": "find", "path": "/cards", "where": {"assignee": "u2", "archived": false}, "text": "<words>"}`
- `where`: optional. Each field must equal the value given; for a list field
  (like `labels`) the list must contain it. Fields left out of a record count as their default.
  Fields: `title`, `description`, `labels`, `assignee`, `due`, `overdue`, `archived`.
- `text`: optional. Case-insensitive; matches if any text field contains it.

Up to 100 matches per reply. If there are more, the reply has an `overflow` note whose
`next` gets the rest.
