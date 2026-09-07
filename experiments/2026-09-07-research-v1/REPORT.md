# CRE Bench: comp and lead research

120/120 planned conditions attempted; 119 returned answers and one exhausted its transport retries, across 24 original synthetic cases. Lev owns, funds and publishes this diagnostic. Independent CRE practitioner qualification has not occurred.

Lev returned 98/99 fully verified requested shortlist entries (99.0%). It also returned 7 ineligible entries, so shortlist yield alone overstates list quality. Its screening accuracy was 96.2% (462/480), and it correctly abstained on 4/4 zero-match cases. Native inference was estimated at $12.61; this is not a Lev subscription or customer price.

The failed condition was GPT-5 direct on `rent-comps-elm`: both 300-second requests timed out. Its three target slots and twenty decisions remain unanswered in aggregate success denominators. It is not counted as a model factual error. Charges for those two requests are unknown.

## Five-condition comparison

| Condition | Completed | Verified yield | Selection precision | Screening success | Cases with material findings | Inference USD |
| --- | --- | --- | --- | --- | --- | --- |
| Lev Agent | 24/24 | 99.0% (98/99) | 93.4% (99/106) | 96.2% (462/480) | 7/24 | $12.6123 estimated |
| GPT-5 + tools | 24/24 | 99.0% (98/99) | 98.0% (99/101) | 99.0% (475/480) | 2/24 | $6.3463 reported |
| Opus 5 + tools | 24/24 | 99.0% (98/99) | 100.0% (99/99) | 99.8% (479/480) | 1/24 | $9.3814 reported |
| GPT-5 direct | 23/24 | 94.9% (94/99) | 96.9% (95/98) | 94.8% (455/480) | 3/23 | >= $2.3173 reported |
| Opus 5 direct | 24/24 | 99.0% (98/99) | 100.0% (99/99) | 100.0% (480/480) | 0/24 | $4.4931 reported |

Verified yield requires eligibility, unique entity, every requested fact, and supporting base/controlling-update identifiers. Precision includes every returned row. Screening success includes all twenty candidates per case, including unanswered decisions after infrastructure failure. GPT-5 direct answered 455/460 decisions correctly; its completion-aware result is 455/480. Zero-match cases are excluded from yield percentages and reported separately. These measures must be read together.

## Performance by task

| Task | Condition | Verified / target | Screening | Material findings | Inference USD |
| --- | --- | --- | --- | --- | --- |
| refinance leads | Lev Agent | 26/26 | 96.7% (116/120) | 3 | $2.9417 |
| refinance leads | GPT-5 + tools | 26/26 | 99.2% (119/120) | 1 | $1.8592 |
| refinance leads | Opus 5 + tools | 26/26 | 100.0% (120/120) | 0 | $1.7107 |
| refinance leads | GPT-5 direct | 25/26 | 97.5% (117/120) | 2 | $0.5489 |
| refinance leads | Opus 5 direct | 25/26 | 100.0% (120/120) | 0 | $1.1685 |
| rent comps | Lev Agent | 23/23 | 95.0% (114/120) | 1 | $3.4470 |
| rent comps | GPT-5 + tools | 23/23 | 97.5% (117/120) | 0 | $1.9077 |
| rent comps | Opus 5 + tools | 23/23 | 99.2% (119/120) | 0 | $3.5637 |
| rent comps | GPT-5 direct | 20/23 | 83.3% (100/120) | 0 | >= $0.6437 |
| rent comps | Opus 5 direct | 23/23 | 100.0% (120/120) | 0 | $1.2156 |
| sales comps | Lev Agent | 23/23 | 96.7% (116/120) | 0 | $3.5953 |
| sales comps | GPT-5 + tools | 23/23 | 100.0% (120/120) | 0 | $1.1444 |
| sales comps | Opus 5 + tools | 23/23 | 100.0% (120/120) | 0 | $2.2688 |
| sales comps | GPT-5 direct | 23/23 | 100.0% (120/120) | 0 | $0.5339 |
| sales comps | Opus 5 direct | 23/23 | 100.0% (120/120) | 0 | $0.9394 |
| sponsor leads | Lev Agent | 26/27 | 96.7% (116/120) | 5 | $2.6283 |
| sponsor leads | GPT-5 + tools | 26/27 | 99.2% (119/120) | 1 | $1.4350 |
| sponsor leads | Opus 5 + tools | 26/27 | 100.0% (120/120) | 2 | $1.8382 |
| sponsor leads | GPT-5 direct | 26/27 | 98.3% (118/120) | 1 | $0.5908 |
| sponsor leads | Opus 5 direct | 27/27 | 100.0% (120/120) | 0 | $1.1697 |

## Deliverables and evidence

| Condition | Selected-fact checks | Source-ID checks | Artifact acceptance checks | No-match cases |
| --- | --- | --- | --- | --- |
| Lev Agent | 99.7% (646/648) | 100.0% (106/106) | 89.6% (86/96) | 4/4 |
| GPT-5 + tools | 100.0% (615/615) | 99.0% (100/101) | 90.6% (87/96) | 4/4 |
| Opus 5 + tools | 99.7% (599/601) | 99.0% (98/99) | 91.7% (88/96) | 4/4 |
| GPT-5 direct | 100.0% (600/600) | 99.0% (97/98) | Not applicable | 4/4 |
| Opus 5 direct | 100.0% (601/601) | 99.0% (98/99) | Not applicable | 4/4 |

The artifact mapper was implemented during the audit after some outputs were visible; the criteria were frozen beforehand. The four artifact criteria are readable required format, matching shortlist identities and order, matching required facts with explicitly marked unknowns, and carried source identifiers. They assess consistency with the submitted answer; factual truth is separate. Direct controls have no file-creation requirement. A blank cell fails the explicit-unknown annotation requirement; it is not counted as an invented financial value. Semantically equivalent headings are mapped uniformly. Original files and earlier generated versions remain unchanged. The generic CSV serializer converted explicit model-supplied JSON nulls into blank cells: 68 field annotations across 17 runs are attributed to the benchmark harness. These delivery-check failures are not model factual errors; each attribution links the original tool input.

## What Lev needs to improve

1. **Apply the as-of filter to every base record.** Native runs often honored future amendments but missed future publication dates on ordinary source records. The accepted shortlist and all candidate decisions need the same evidence cutoff.
2. **Keep parent identity separate from transaction evidence.** The Dogwood sponsor answer attributed a different transaction amount/date to its selected parent record. Parent resolution must preserve the exact acquisition and source relationship used to qualify the prospect.
3. **Honor the requested deliverable and missing-data notation.** Some prospect tasks returned XLSX instead of CSV. Some original files exported unknown emails or balances as blanks. Require an explicit unknown convention and validate the chosen format before delivery.

These are findings from the retained native runs, not fixes applied to Lev or to its outputs. The existing financing release also identifies memo, citation and workbook issues; its original results are unchanged.

## Cost

Reported API inference: **at least $22.5382**; two timeout charges are unknown. Estimated Lev inference: **$12.6123**. Every attempt is retained; unreported charges are not treated as zero. Native costs sum matched generation and embedding events; duplicate run-summary events are excluded. Session naming, hosting, subscriptions, operator time and non-inference overhead are outside the measured scope. Product credits are not converted to dollars. Token costs from earlier development and financing cohorts are separate and must not be presented as research execution costs.

## Versioned scoring correction

The headline uses scoring v1.1. Correctly labeled numeric wrappers and source-proven parent/SPV label annotations are mapped to the originally requested facts. The original schema left fact types open, so the v1 scalar-only comparisons were too restrictive. Original v1 grades and aggregate results are preserved. No answer, calculation, source, selection, model run or original artifact is repaired. See [the scoring erratum](SCORING-ERRATUM.md) for exact deltas and mappings.

## Interpretation and limits

This is a controlled test of qualification and analysis over supplied fictional extracts. It does not establish live comp discovery, lead database coverage, email deliverability, customer conversion, valuation accuracy, or document-ingestion performance. Six variants share each of four task templates; there are not 24 independent customer deals. One execution per case/condition cannot establish run-to-run reliability. Public cases are not a held-out evaluation.

Lev's native condition used Claude Opus 4.7 with Agent 7.9. GPT-5 and Opus 5 were each called directly and through the same generic calculation/file harness. Provider defaults were retained, so compute is not equal. Complete native packet text was verified before sending; the editor changes paragraph whitespace. The trace connector truncates long root input/output fields, so the audit combines matching trace prefixes, complete captured UI inputs/JSON, and event metadata. No retrieval was observed in the recorded native backend tools, but internal file-creation execution is absent from the available trace metadata. Native data-access equivalence is therefore unverified under the strict common-corpus protocol. Native results remain a separately identified product condition alongside the supplied-packet API controls; the comparison does not establish identical access. Internal system prompts and account context are not redistributed.

## Inspect and reproduce

- [Frozen execution protocol](../../benchmarks/research-v1/execution-protocol.md)
- [Pre-execution hashes, models and prompts](plan.json)
- [All recorded scores and audit details](results.json)
- [Run-level CSV](run-summary.csv)
- [Public grading code](../../crebench/grade_research.py)
- [Artifact inspection code](../../tools/collect-research.py)
- [Supplementary file and layout observations](ARTIFACT-REVIEW.md)
- [Charts: native/general agents](figures/research-agent-quality.svg), [direct API comparison](figures/research-direct-quality.svg), [screening](figures/research-screening.svg), [cost](figures/research-cost.svg), [case matrix](figures/research-case-matrix.svg), [material findings](figures/research-material-errors.svg)

Install `requirements-research.txt`, then run `python3 tools/collect-research.py`, `python3 tools/report-research.py` and `python3 tools/plot-research.py`. This replays public scoring and publication without paid model calls. Native import is an evidence-collection step and is not needed to replay the published results. The scored generic XLSX writer uses the Codex-bundled artifact runtime, so identical fresh file generation requires that runtime; numerical regrading and published-file inspection use public packages. Lev’s backend remains proprietary.
