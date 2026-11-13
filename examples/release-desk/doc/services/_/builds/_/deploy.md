# deploy

Roll a build out to an environment. Takes a few seconds; the environment's entry for that
service is busy meanwhile, with progress.

Call: `{"action": "deploy", "path": "/services/<service>/builds/<build id>", "env": "staging"}`
- `env`: `staging` or `production`.

**Production asks a person first.** The receipt carries an alert with `answer_by: person`:
you can't confirm it yourself. Tell the person it's waiting; they approve or reject it in
the app. If they approve, the rollout starts; either way, the deploy's ping says what
happened. Deploys to staging start at once.

Changes: `/environments/<env>/running/<service>`, and a new entry in `/deploys`.

Errors:
- `build_failed`: only builds that passed can be deployed.
- `not_on_staging`: production only takes builds that have been deployed to staging.
- `already_running`: the environment already runs this build.
