# Financial reasoning pilot — September 6, 2026

Protocol prepared and committed before model execution. This is a real model API
experiment on one **public synthetic development case**, not a production leaderboard.

Three repetitions each of GPT-5.6 Sol, Claude Sonnet 5 and Gemini 3.8 Flash, selected
as a small cross-provider pilot, not a claim to exhaustive or matched-price coverage.
Run order is round-robin. Every run gets the identical six-file packet as text;
answer keys and the worked reference answer are excluded. No tools, retries,
response repair or requested model fallbacks. Strict JSON parsing; fenced answers
fail the output contract. Temperature and reasoning remain provider defaults and
are not assumed to represent equal compute. Gateway provider routing is automatic.
Model aliases may change. Preserve returned identifiers and complete response JSON.

`plan.json` binds the packet, case manifest, grader and runner by SHA-256. Requests
are committed before execution. Each attempt writes a start record before sending;
interrupted attempts cannot silently retry. HTTP, parse and output-limit failures
remain visible. Stop on authentication, billing or access errors. No credit purchase.

Budget: nine calls, 8,192 maximum output tokens each, no paid tools. The catalog
reservation uses prompt byte count as a loose input-token ceiling, highest standard
catalog tier rates and 2x headroom. It is below $2 at preparation time. This is an
application-side estimate, not a provider-enforced billing cap. Actual response
usage and any returned cost data are retained; estimates must be labeled separately.

Report each run's 27 field-value checks separately from the 27 supplied-reference
checks, conflict identification and two consistency checks. Count complete success
only for a complete valid response passing all 58 checks. Do not treat repetitions
or correlated checks as independent deals or publish confidence intervals implying
population accuracy. Missing runs are not passes or model-quality failures.

Limitations: one disclosed answer key, no independent practitioner qualification,
canonical references supplied by the contract, no PDF/OCR test, no generated
workbook or OM assessment, and no Lev product evaluation. Results cannot establish
which system is best for customer workflows.

Reproduce grading without an API key by reading each retained `answer.txt` and using
the frozen `crebench.grade` implementation. To run a new experiment, prepare a new
directory and use your own AI Gateway credentials; existing attempts never overwrite.

```sh
python3 -m crebench.run_pilot execute experiments/2026-09-06-financial-pilot --env-file .env.local
```

Authentication: `AI_GATEWAY_API_KEY` or `VERCEL_OIDC_TOKEN` from the environment,
or a local Vercel `.env.local` file. Credentials are never stored in experiment files.
