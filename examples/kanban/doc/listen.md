# listen

Hear about changes under a path, whoever makes them: you, other people, other agents.
A query: changes nothing.

Call: `{"action": "listen", "path": "<path>"}`, for example `/` for everything.

Answer: `{"path": "<path>", "version": <n>, "listening": true}`.

From then on you get every ping that changes or removes a path under it:
`{"ping": "<submission id>", "version": <n>, "changed": [<paths>], "removed": [<paths>]}`.

Pings for your own submissions come whether you listen or not.
