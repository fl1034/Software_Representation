# find

Get only the builds that match. Same answer as `observe`. Running builds are left out.

Call: `{"action": "find", "path": "/services/<service>/builds", "where": {"status": "failed"}, "text": "<words>"}`
- `where`: optional; fields must equal the values given. Fields: `commit`, `author`, `status`.
- `text`: optional; case-insensitive, in the commit message, author or failed test.
