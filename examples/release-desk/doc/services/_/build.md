# build

Build the service's latest commit (its `head`) and run its tests. Takes several seconds.

Call: `{"action": "build", "path": "/services/<service>"}`

The receipt's `busy` gives the new build's path, for example
`/services/storefront/builds/b6`. The build appears there at once, busy, with progress
(`"Running tests a41c9e2"`, 2 of 4 steps) and a `cancel` call. It has no `last`, because
it didn't exist before. Several builds can run at once.

When it settles, the ping lists the build; observe it to see whether it `passed`.
