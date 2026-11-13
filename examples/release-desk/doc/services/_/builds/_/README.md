# Builds

Each build under `/services/<service>/builds`, oldest first. Fields:

- `commit`, `message`, `author`: the commit that was built.
- `status`: `passed`, `failed` or `cancelled`. While running, the build is busy instead.
- `failed_test`: the first test that failed. Only when `status` is `failed`.
- `duration_s`: how long it took, in seconds.
