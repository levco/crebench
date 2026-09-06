# Financial pilot results

Real API attempts on one public synthetic case. These are development findings, not a leaderboard.

| Requested model | Run | Status | Checks passed | Complete success | Seconds |
|---|---|---|---|---|---|
| xiaomi/mimo-v2.5 | r1-1 | invalid_json | — | False | 37.929 |
| xiaomi/mimo-v2.5 | r2-1 | invalid_json | — | False | 116.86 |
| xiaomi/mimo-v2.5 | r3-1 | invalid_json | — | False | 65.371 |
| xiaomi/mimo-v2.5-pro | r1-2 | invalid_json | — | False | 126.192 |
| xiaomi/mimo-v2.5-pro | r2-2 | invalid_json | — | False | 101.156 |
| xiaomi/mimo-v2.5-pro | r3-2 | invalid_json | — | False | 90.159 |
| inclusionai/ling-3.0-flash-sante | r1-3 | invalid_json | — | False | 18.37 |
| inclusionai/ling-3.0-flash-sante | r2-3 | invalid_json | — | False | 28.147 |
| inclusionai/ling-3.0-flash-sante | r3-3 | invalid_json | — | False | 19.01 |

## Interpretation

A single case and repeated calls do not establish accuracy on real CRE work. The 58 checks include 27 field-value checks, 27 prescribed-reference checks, one exact discrepancy-set check, two consistency checks and one format check. References are supplied in the contract, so reference compliance is not independent evidence retrieval.

All nine accessible-model attempts returned HTTP 200 but failed strict JSON parsing. Financial correctness was not scored; zero complete submissions must not be read as zero financial accuracy. This finding motivates separate format-compliance and semantic-correctness reporting in the next protocol version. The original grades remain unchanged.

No answer repairs or favorable-run selection. HTTP errors and unattempted calls are infrastructure outcomes, not financial mistakes. A truncated or invalid response is not complete success even when some values are correct.

Cost and token usage are preserved as returned by the gateway. No inference cost is invented when absent. Latency includes the gateway and network, and is not pure model generation time.

## Limits

- One public case; answer key already published
- No independent case reviewer
- CSV and JSON supplied as text; no PDF ingestion
- Source references supplied in contract
- Provider defaults and routing may differ; not equal compute
- Aliases may change over time
- No workbook, OM, or Lev product assessment
- Cost reservation is not a provider billing cap
