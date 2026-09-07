# Publication integration corrections

The data release is commit `cfa17d0a25b36d5cf1ddbf86e8b49bcef1bf6081`.
Its publication manifest remains an integrity snapshot of that commit's files.
Later integration fixes do not change frozen prompts, model responses, scores,
cost records or artifact bytes:

- The clean Linux CI runner lacked `soffice`. The workflow now installs
  LibreOffice Calc and checks the expansion's frozen hashes and coverage.
- The case filter now uses an external same-origin script, complying with the
  production Content Security Policy. The site checker rejects an inline
  expansion script. Local plain-HTTP testing alone did not enforce that policy.

The earlier failed CI run remains in GitHub history. The current commit's CI
status and deployed browser behavior must be checked before reporting success.
