# Native product calibration protocol

A product pilot tests the customer's workflow with original files. It is separate
from the API track that supplies extracted text. Lev owns and publishes CRE Bench;
Lev's own pilot is not an independent evaluation.

## What to preserve

- Exact original sources and any adapted copies, with hashes and transformation log.
- Task brief, product account configuration, visible version information and time.
- Upload admission, document classification and extraction completion separately.
- First-pass facts before corrections, including selected sources and conflicts.
- First assistant response, follow-ups, generated artifacts and human interventions.
- Visible error messages, user actions, wall time and credit observations.

Do not give the product the answer key. Input facts belong in the task brief;
expected derived answers do not. Source and artifact downloads must be retained
privately until account identifiers, access tokens and unrelated content are removed.

## Measure each stage separately

| Stage | Observable result | Failure interpretation |
|---|---|---|
| File admission | Every supplied file appears and is readable | Unsupported format or upload failure |
| Index / structured facts | Correct, traceable fields become available | Missing fields, failed extraction or incorrect facts |
| Financial analysis | Correct values, calculations and reconciliation | Missing answer, arithmetic/classification mistake or unsupported claim |
| Underwriting | A downloadable workbook recalculates correctly | No artifact, hardcoded formulas, wrong assumptions or calculation failures |
| OM | A downloadable document has grounded claims and usable pages | No artifact, unsupported claims, omitted facts or rendering failures |

Keep stage completion and conditional content quality distinct. A failure to
produce an artifact counts against workflow completion, while its unobservable
content quality remains unscored. Do not score an empty Index as financially
incorrect values. Report retries and recovery outcomes next to the first attempt.

## Artifact briefs

For underwriting, specify asset class, loan/transaction type, date, source periods,
scenario assumptions, desired output, missing-data rules and whether template
defaults are permitted. Evaluate requested custom sizing separately from a product's
standard lender template. A disclosed default can still fail a required constraint.

For an OM, specify audience, sections, source-only rules, known omissions and export
format. Record required outline approval. Inspect exported pages and numeric claims;
a chat message claiming an OM was generated is not evidence of a usable OM.

## Calibration limits

One public fictional packet can expose workflow defects and grader weaknesses. It
cannot establish performance on customers' documents or support a leaderboard.
File variants share one underlying case and remain in the same evaluation split.
Independent CRE review and broader document coverage are required before scoring
qualified cases. Any protocol change after observing responses applies only to a
new version; the original responses and outcomes remain available.
