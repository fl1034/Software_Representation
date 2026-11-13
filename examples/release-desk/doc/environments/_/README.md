# Environments

`staging` and `production`. Fields:

- `url`: where it's served.
- `running`: service name to the id of the build it runs, under `/services/<service>/builds`.
  Busy while a deploy rolls out.
- `flags`: feature switches, each `{"on": true | false}`. See `flags/_/set.md`.
