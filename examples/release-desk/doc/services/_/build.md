# build

Build the service's latest commit (its `head`) and run its tests. Takes several seconds.

Call: `{"action": "build", "path": "/services/<service>"}`

Busy: a new build under `/services/<service>/builds`, which appears at once, busy, with
progress (`"Running tests a41c9e2"`, 2 of 4 steps) and a `cancel` call. Its marker says
`"by": "<your receipt id>"`, which is how you find its id. It has no `last`, because it
didn't exist before. Several builds can run at once.

When it settles, the ping lists the build; observe it to see whether it `passed`.
