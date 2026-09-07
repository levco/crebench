# Scoring v1.1 erratum

Published after auditing the research-v1 outputs. The original execution protocol, prompts, inputs, answer keys, factual grader, requests, responses and original artifacts remain unchanged. No quality reruns were performed. This is a versioned rescore of the same retained outputs, not a prospectively frozen v1.1 execution.

## Why the correction is necessary

The supplied brief requested numeric units, while `facts` was an open object with no scalar-only field schema. Some answers supplied `{value: 64000, unit: "sf"}` instead of `64000`. The original grader called these materially wrong despite the correct number and unit. A source-proven parent label also included an accurate parenthetical SPV annotation. Treating these presentation differences as factual errors would misrepresent performance.

The v1.1 adapter unwraps only numeric `property_size` and `price_per_unit` objects with exactly `value` and `unit`, a finite number, and the unit required by the brief. It performs no unit conversion or numeric repair. Wrong or unknown units remain failures. It accepts two explicit parent/SPV name annotations only when both names and the executed ownership relationship are in the supplied source records. Contacts, dates, amounts, source IDs, rankings, eligibility and all other fields remain unchanged. The same adapter applies to every condition and artifact consistency check.

- [Versioned adapter](../../crebench/research_representation_v1_1.py)
- [Original grader](../../crebench/grade_research.py)
- [Original aggregate snapshot](results-v1.json)
- Each completed run preserves `grade-v1.json`; corrected `grade.json` lists every representation adjustment.

## Denominator and cost disclosure

All 120 planned conditions were attempted. GPT-5 direct on Rent Comps Elm exhausted its one allowed retry: two requests each timed out after 300 seconds. No response or usage bill was returned. Its three target slots and twenty candidate decisions remain unanswered in completion-aware headline denominators. The original snapshot excluded this ungraded condition from those denominators; v1.1 makes the full attempted denominator explicit. Conditional screening for GPT-5 direct is 455/460 answered decisions; completion-aware screening is 455/480. Material-error counts remain based only on returned answers, with the 23-answer denominator disclosed. Two timeout charges are unknown, so this condition and the aggregate API cost are lower bounds, not complete bills.

## Score changes

| Condition | Original verified / graded target | v1.1 verified / planned target | Material findings, v1 → v1.1 |
| --- | --- | --- | --- |
| Lev Agent | 98/99 | 98/99 | 9 → 9 |
| GPT-5 + tools | 98/99 | 98/99 | 2 → 2 |
| Opus 5 + tools | 88/99 | 98/99 | 18 → 2 |
| GPT-5 direct | 94/96 | 94/99 | 3 → 3 |
| Opus 5 direct | 98/99 | 98/99 | 0 → 0 |

Eligibility and source-ID judgments are unchanged. Original artifact bytes are unchanged. File inspection additionally maps equivalent headers uniformly. Generic CSV null-to-blank losses are attributed to the benchmark writer when original tool arguments prove explicit model-supplied nulls; the delivery failures remain visible and do not become model factual errors.

## Changed answer representations

- `agent/anthropic/claude-opus-5/sales-comps-cypress`: 10 mappings; original and normalized values in `grade.json`.
- `agent/anthropic/claude-opus-5/sales-comps-dogwood`: 5 mappings; original and normalized values in `grade.json`.
- `agent/anthropic/claude-opus-5/sponsor-leads-dogwood`: 1 mappings; original and normalized values in `grade.json`.

## Native execution coverage

The exact supplied packet was verified in the native UI. Matched backend tool metadata showed file delivery and expertise access without retrieval. Internal file-creation execution is not visible in that metadata, so native data-access equivalence is unverified. Native results are published as a separate product condition; they are not a confirmed common-corpus pass. This limitation does not alter their observed output scores.
