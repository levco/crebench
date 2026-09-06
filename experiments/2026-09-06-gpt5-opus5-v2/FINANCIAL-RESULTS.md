# Financial pilot: corrected scoring

One public fictional case. Every retained response is included. Formatting is diagnostic; financial and source-reference checks are separate.

| Model | Run | Financial checks | Reference checks | Seconds | Cost (USD) |
|---|---|---|---|---|---|
| openai/gpt-5 | r1-1 | 25/30 | 27/27 | 46.628 | $0.050894 |
| anthropic/claude-opus-5 | r1-2 | 29/30 | 27/27 | 14.889 | $0.071175 |
| openai/gpt-5 | r2-1 | 29/30 | 27/27 | 42.117 | $0.041078 |
| anthropic/claude-opus-5 | r2-2 | 28/30 | 27/27 | 15.241 | $0.071175 |
| openai/gpt-5 | r3-1 | 29/30 | 27/27 | 52.753 | $0.048718 |
| anthropic/claude-opus-5 | r3-2 | 29/30 | 27/27 | 13.93 | $0.071175 |

Cost is gateway-reported inference usage for each retained call, in USD. It excludes platform subscriptions, human work, hosting, and unmetered product tools. A reported zero is not an estimate of total service cost; missing usage is shown as Not recorded. Exact amounts remain in the machine-readable report.

## Financial failures

- r1-1 (openai/gpt-5): operating_expenses, noi, dscr_limit, debt_yield_limit, conflicts.exact_set
- r1-2 (anthropic/claude-opus-5): conflicts.exact_set
- r2-1 (openai/gpt-5): conflicts.exact_set
- r2-2 (anthropic/claude-opus-5): annual_in_place_rent, conflicts.exact_set
- r3-1 (openai/gpt-5): conflicts.exact_set
- r3-2 (anthropic/claude-opus-5): conflicts.exact_set

## Interpretation

The 30 financial checks are 27 values, one exact conflict-set check and two consistency checks. They are correlated checks on one case, not 30 independent transactions. The 27 reference checks measure the supplied canonical references, not evidence discovery. No statistical ranking is supported by three repetitions on one case.

All raw responses and original execution outcomes remain unchanged. The supplemental scorer removes presentation wrappers and recognizes equivalent constraint labels. It never computes missing answers or replaces incorrect numbers. The scoring correction was developed after inspecting earlier responses and applies to all runs; it was not preregistered before their generation.

See [the correction policy](../../docs/scoring-correction-2026-09-06.md) and [the machine-readable report](financial-v2.json) for normalization logs, exact failed checks and hashes.
