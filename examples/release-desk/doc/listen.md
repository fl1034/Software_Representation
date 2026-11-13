# listen

Hear about changes under a path, whoever makes them: you, other people, other agents.
A query: changes nothing.

Call: `{"action": "listen", "path": "<path>"}`, for example `/` for everything.

Answer: `{"listening": true}`. From then on you get, for every submission that touches a
path under it:
- a **busy event** when a submission makes nodes under it stop having a well-defined
  value: `{"busy": "<submission id>", "action": "<action>", "path": "<called node>"}`. The
  action's doc says which nodes it makes busy;
- a **ping** when they settle: `{"ping": "<submission id>", "version": <n>, "changed": [<paths>], "removed": [<paths>]}`.

A submission that settles at once sends only the ping. For your own submissions you get
the receipt instead of the busy event, and the ping whether you listen or not.

Alerts don't come through `listen`: they come on the alert channel, which you are always
on (see `README.md`).
