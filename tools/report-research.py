"""Build the executive research summary from the scored run matrix."""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / 'experiments/2026-09-07-research-v1'
data = json.loads((EXP / 'results.json').read_text())

def pc(n, d):
    return f'{100*n/d:.1f}% ({n}/{d})' if d else 'Not applicable'

def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |'] + ['| ' + ' | '.join(str(v) for v in row) + ' |' for row in rows])

native = data['summary'][0]
completed = sum(r['status'] == 'completed' for r in data['runs'])
rows = data['summary']
api = sum(r['cost_total_usd'] for r in rows if r['track'] != 'lev_native')
text = f'''# CRE Bench: comp and lead research

120/120 planned conditions attempted; {completed} returned answers and one exhausted its transport retries, across 24 original synthetic cases. Lev owns, funds and publishes this diagnostic. Independent CRE practitioner qualification has not occurred.

Lev returned {native['verified']}/{native['target']} fully verified requested shortlist entries ({100*native['verified']/native['target']:.1f}%). It also returned {native['returned']-native['eligible']} ineligible entries, so shortlist yield alone overstates list quality. Its screening accuracy was {pc(native['screening']['passed'],native['screening']['total'])}, and it correctly abstained on {native['abstention']['passed']}/{native['abstention']['total']} zero-match cases. Native inference was estimated at ${native['cost_total_usd']:.2f}; this is not a Lev subscription or customer price.

The failed condition was GPT-5 direct on `rent-comps-elm`: both 300-second requests timed out. Its three target slots and twenty decisions remain unanswered in aggregate success denominators. It is not counted as a model factual error. Charges for those two requests are unknown.

## Five-condition comparison

{table(['Condition','Completed','Verified yield','Selection precision','Screening success','Cases with material findings','Inference USD'], [[r['label'],str(r['completed'])+'/24',pc(r['verified'],r['target']),pc(r['eligible'],r['returned']),pc(r['screening']['passed'],r['screening']['total']),str(r['cases_with_material_errors'])+'/'+str(r['graded']),('>= ' if r['costs_recorded']<r['planned'] else '')+f"${r['cost_total_usd']:.4f}"+(' estimated' if r['track']=='lev_native' else ' reported')] for r in rows])}

Verified yield requires eligibility, unique entity, every requested fact, and supporting base/controlling-update identifiers. Precision includes every returned row. Screening success includes all twenty candidates per case, including unanswered decisions after infrastructure failure. GPT-5 direct answered 455/460 decisions correctly; its completion-aware result is 455/480. Zero-match cases are excluded from yield percentages and reported separately. These measures must be read together.

## Performance by task

{table(['Task','Condition','Verified / target','Screening','Material findings','Inference USD'], [[r['task'].replace('_',' '),r['label'],str(r['verified'])+'/'+str(r['target']),pc(r['screening']['passed'],r['screening']['total']),r['material_errors'],('>= ' if r['costs_recorded']<r['planned'] else '')+f"${r['cost_total_usd']:.4f}"] for r in sorted(data['tasks'],key=lambda r:(r['task'],next(i for i,s in enumerate(rows) if s['label']==r['label'])))])}

## Deliverables and evidence

{table(['Condition','Selected-fact checks','Source-ID checks','Artifact acceptance checks','No-match cases'], [[r['label'],pc(r['facts']['passed'],r['facts']['total']),pc(r['evidence']['passed'],r['evidence']['total']),pc(r['artifact_checks']['passed'],r['artifact_checks']['total']),str(r['abstention']['passed'])+'/'+str(r['abstention']['total'])] for r in rows])}

The artifact mapper was implemented during the audit after some outputs were visible; the criteria were frozen beforehand. The four artifact criteria are readable required format, matching shortlist identities and order, matching required facts with explicitly marked unknowns, and carried source identifiers. They assess consistency with the submitted answer; factual truth is separate. Direct controls have no file-creation requirement. A blank cell fails the explicit-unknown annotation requirement; it is not counted as an invented financial value. Semantically equivalent headings are mapped uniformly. Original files and earlier generated versions remain unchanged. The generic CSV serializer converted explicit model-supplied JSON nulls into blank cells: {sum(r['harness_induced_null_annotations'] for r in rows)} field annotations across {sum(r['cases_with_harness_null_loss'] for r in rows)} runs are attributed to the benchmark harness. These delivery-check failures are not model factual errors; each attribution links the original tool input.

## What Lev needs to improve

1. **Apply the as-of filter to every base record.** Native runs often honored future amendments but missed future publication dates on ordinary source records. The accepted shortlist and all candidate decisions need the same evidence cutoff.
2. **Keep parent identity separate from transaction evidence.** The Dogwood sponsor answer attributed a different transaction amount/date to its selected parent record. Parent resolution must preserve the exact acquisition and source relationship used to qualify the prospect.
3. **Honor the requested deliverable and missing-data notation.** Some prospect tasks returned XLSX instead of CSV. Some original files exported unknown emails or balances as blanks. Require an explicit unknown convention and validate the chosen format before delivery.

These are findings from the retained native runs, not fixes applied to Lev or to its outputs. The existing financing release also identifies memo, citation and workbook issues; its original results are unchanged.

## Cost

Reported API inference: **at least ${api:.4f}**; two timeout charges are unknown. Estimated Lev inference: **${native['cost_total_usd']:.4f}**. Every attempt is retained; unreported charges are not treated as zero. Native costs sum matched generation and embedding events; duplicate run-summary events are excluded. Session naming, hosting, subscriptions, operator time and non-inference overhead are outside the measured scope. Product credits are not converted to dollars. Token costs from earlier development and financing cohorts are separate and must not be presented as research execution costs.

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
'''
(EXP / 'REPORT.md').write_text(text)
print(EXP / 'REPORT.md')
