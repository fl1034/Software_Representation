# find

Get only the deploys that match. Same answer as `observe`.

Call: `{"action": "find", "path": "/deploys", "where": {"env": "production", "service": "payments"}}`
- `where`: optional; fields must equal the values given.
- `text`: optional; case-insensitive.

Each deploy is `{"service", "build", "env", "at", "by"}`: `at` is the time it finished,
`by` who asked for it (and who approved it, for production).
