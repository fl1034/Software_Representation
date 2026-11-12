# find

Get only the tasks that match. Same reply as `observe`, with only the matches.

Call: `{"action": "find", "path": "/tasks", "where": {"done": false}, "text": "<words>"}`
- `where`: optional. Each field must equal the value given; for a list field
  (like `labels`) the list must contain it. Fields left out of a record count as their default.
  Fields: `title`, `done`.
- `text`: optional. Case-insensitive; matches if any text field contains it.

Up to 100 matches per reply. If there are more, the reply has an `overflow` note whose
`next` gets the rest.
