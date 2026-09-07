# CRE Bench workflow v1 — recorded results

Thirty completed workflows: six native Lev, twelve generic-agent and twelve direct API controls. All eighteen agent workflows delivered an XLSX and PDF. This is a six-case diagnostic release, not independent practitioner validation or a representative customer-deal estimate.

| System | Source facts | Financials | Workbook checks | Memo checks | Source-location evidence | Known inference / six cases |
|---|---:|---:|---:|---:|---:|---:|
| Lev Agent | 102/102 (100.0%) | 132/132 (100.0%) | 56/60 (93.3%) | 46/60 (76.7%) | 70/102 (68.6%) | $17.4548 |
| GPT-5 agent | 96/102 (94.1%) | 132/132 (100.0%) | 54/60 (90.0%) | 54/60 (90.0%) | 72/102 (70.6%) | ≥ $1.9207 |
| Opus 5 agent | 102/102 (100.0%) | 132/132 (100.0%) | 60/60 (100.0%) | 55/60 (91.7%) | 102/102 (100.0%) | ≥ $20.7773 |

## Findings that matter

- Lev ties Opus 5 on all requested source facts and financial calculations and exceeds GPT-5 on source-fact accuracy in this sample. GPT-5 miscounted occupied units and rent in Cedar Landing.
- All eighteen workbooks pass the numerical base and changed-input tests. Lev has invalid explanation formulas in four workbooks. GPT-5 omits workbook source references in all six. Opus passes all workbook acceptance checks.
- Narrative reliability is weaker than numeric agreement. Lev reverses positive downside cash into cash-in in Cedar and Juniper and has other payment, rollover and formula-description errors. Five Lev PDFs have layout defects.
- Opus has its own material miss: Market Row memo cap-stress proceeds exceed the correct limit by $274,472.61 and two-year vacant/rolling area is understated. Its workbook is correct. Juniper overstates the extra full-occupancy rent bridge; Stonebridge places a near-maturity lease expiry after maturity without support.
- GPT-5 uses output-workbook coordinates as original rent-roll citations in three cases, and its Stonebridge memo understates the cap-stressed value by $54,694.72. Its Juniper memo incorrectly leaves stressed LTV capacity unchanged.
- No overall Lev superiority claim follows. The task charts retain each system’s wins, ties and losses; no blended score hides material mistakes.

## Cost, time and operating conditions

Scored API runs have $26.74312 of known gateway-reported inference. The six native Lev chat traces estimate $17.45482275 of inference using OpenRouter model rates. Nine rejected HTTP 402 attempts did not report billing usage, so affected API totals remain known lower bounds. These values exclude unattributed setup extraction, OCR, subscriptions, storage, hosting and operator time. They are not customer prices.

Separate adapter development used $8.8112985 of reported API inference plus $2.30726525 estimated Lev inference. Earlier one-case pilots are separate cohorts. The gateway top-up was $50 in credits with a $56.35 checkout total including fee and estimated tax; purchasing credit is not inference consumption.

Native Lev used agent 7.9 with Claude Opus 4.7. Generic agents used openai/gpt-5 and anthropic/claude-opus-5 with the same bounded tools, including supplied workbook styles and PDF pagination. Provider defaults and tool access differ. Direct controls have text-only source representations and cannot inspect the image-only Stonebridge lease; their results are not native-ingestion comparisons.

The nine credit interruptions resumed their exact saved wire requests. Original consumed turns, tools, artifact versions and costs remained. Administrative credit waiting was excluded from active latency. No completed case was rerun for a better score.

## Verification and reproducibility

55 evaluator/runner tests passed. All 72 frozen file hashes remain unchanged. Public replay independently recalculated the eighteen original workbooks and their three published perturbation copies: 198/198 numerical checks passed, with four original workbooks retaining their formula-error findings. Every memo’s full text and page renders, and every main underwriting sheet, were reviewed.

All thirty runs have 17 source-location review decisions. There are 1,170 source/financial value checks and 360 artifact acceptance checks. Counts within a case are correlated; the independent case count is six.

The numerical regrader and workbook replay use public Python dependencies and LibreOffice. New artifact generation with the scored harness still requires the Codex-bundled @oai/artifact-tool runtime, unavailable from public npm when checked. That limitation is disclosed rather than claiming universal identical replay.

## Next qualification work

Independent CRE practitioner review; a larger permitted corpus with realistic heterogeneous layouts; repeated trials; a fully public generation adapter; dedicated Index ingestion and offering-memorandum tasks; complete attributable cost and setup-time measurement. The present cases use concise original fictional documents informed by privately reviewed professional materials, with no customer documents redistributed.
