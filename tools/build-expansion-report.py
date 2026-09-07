"""Generate the executive report from the disclosed matched cohort."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/2026-09-07-cre-work-v2'
D=json.loads((OUT/'results.json').read_text());matched=D['matched_rows']
C=json.loads((OUT/'cost-ledger.json').read_text())
lines=['# CRE Work v2: diagnostic results','',
'This is a partial diagnostic release, funded and published by Lev. It is not a practitioner-qualified ranking. All new public packets are synthetic: 20 packets, four shared authoring families, zero authentic customer deals.',
'',f"Recorded workflow stages: {len(D['rows'])}; completed: {sum(r['status']=='completed' for r in D['rows'])}; proposed full matrix: 720. The principal comparison contains {len(D['matched_keys'])} matched stages from {len({k[0] for k in D['matched_keys']})} packets, one trial per stage. Initial and revised stages are correlated, not independent transactions.",
'','| System | Ingestion | Financial calculations | Risk flags | Correct sensitivity scenarios | Inference cost |','| --- | --- | --- | --- | --- | --- |']
for c in D['conditions']:
 rs=[r for r in matched if r['model']==c['model']]
 if not rs:continue
 cells=[c['label']]
 for g in ['ingestion','financial','judgment']:
  n=sum(r['scores'][g]['passed'] for r in rs);den=sum(r['scores'][g]['total'] for r in rs);cells.append(f'{n}/{den} ({100*n/den:.1f}%)')
 cells.append(f"{sum(p['passed'] for r in rs for p in (r.get('audit') or {}).get('workbook',{}).get('perturbations',[]))}/{3*len(rs)}")
 cost=sum(r['cost_usd'] if r['cost_usd'] is not None else r['known_partial_cost_usd'] or 0 for r in rs)
 cells.append(('≥ ' if any(r['cost_usd'] is None for r in rs) else '')+f'${cost:.2f}'+(' estimated' if c['model']=='lev/native' else ''))
 lines.append('| '+' | '.join(cells)+' |')
lines+=['','Interpretation: compare each column independently. Input accuracy, financial calculations, workbook behavior and cost measure different things. Financial errors can propagate through several dependent outputs; their count is not a count of independent failures. The scoring tolerance is not a practitioner materiality judgment.',
'','## What the Lev results expose','',
'The following values come from unaltered Lev answers and the source-derived reference. Initial GPR was independently re-summed from the actual certified XLSX cells for office, retail and industrial; their reference totals agree. Retail also has an executed $350/month Suite 001 amendment. The instructions explicitly keep stabilized GPR separate from that in-place amendment.',
'','| Packet / stage | Field | Reference | Lev answer | Difference |','| --- | --- | --- | --- | --- |']
for r in D['rows']:
 if r['model']!='lev/native':continue
 checks=json.loads((ROOT/r['run_path']/f"grade-{r['stage']}-v1.1.json").read_text())['checks']
 for k in ['annual_in_place_rent','unit_001_monthly_rent','gross_potential_rent','uw_noi','maximum_loan','total_area_sf']:
  x=next(v for v in checks if v['field']==k)
  if x['passed'] or not isinstance(x['actual'],(int,float)):continue
  lines.append(f"| {r['case_id']} / {r['stage']} | {k} | {x['expected']:,.2f} | {x['actual']:,.2f} | {x['actual']-x['expected']:+,.2f} |")
lines+=['','Lev produced original XLSX and PDF files for all four native packets and their revisions. In retail it corrected an initial area-total error during revision, while retaining the erroneous amendment interpretation. Inspect the original files and field grades to distinguish input selection, arithmetic and artifact behavior. Do not infer that formula-connected files have correct starting assumptions.',
'','## Consumer product and lender checks','',
'Claude Chat used its native tools and displayed Opus 5 High setting on one initial packet and its revision. Its small comparison is displayed separately; it does not restrict the broader Lev/API chart to that one packet. Per-task consumer inference cost is unmeasured. ChatGPT product access was unavailable in the inspected session.',
'',f"The lender evidence track has {len(D['lender_rows'])} recorded runs. It tests a fixed set of eight dated program-evidence probes. Category, source-ID and no-invented-approval checks are automated; they are not full professional explanation scores. The category mismatches involve missing DSCR; the explanations still identify the missing financial information. Native lender-directory ranking remains unmeasured.",
'','## Live research','',
f"There are {len(D['discovery_rows'])} recorded model/brief cells across six research briefs. Completion is separate from source verification. See [source audit](../2026-09-07-live-discovery-v1/SOURCE-AUDIT.md) for supported facts and defects: announcement dates presented as execution dates, a contact-name/email mismatch in a Lev row, a Lev office loan retained despite an acknowledged extension from 2027 to 2029, and a scheduled rent reported without its free-rent concession in a GPT-5 row. Those findings remain visible for both products and APIs. Full returned-set precision and pooled recall remain unmeasured.",
'','## Cost and execution integrity','',
'The cumulative inference-token authorization remains $200: $110 reserved for prior work, $37 workflow APIs, $26 discovery APIs, $2 lender APIs and $25 native products. A one-time $100 gateway credit purchase cost $112.36 including processing fee and tax; auto-reload was off. Funding is separate from inference consumption. Native costs are matched trace estimates, API costs use reported usage, and missing usage remains unknown or a lower bound. Search/data services, subscriptions, indexing and human effort are not included in an all-in price.',
'', f"This expansion records ${C['expansion_reported_api_plus_native_estimate_usd']:.2f} of API-reported inference plus native main-trace estimates. This excludes the prior project reservation and the unmeasured components above. Inspect the [attempt-level cost ledger](cost-ledger.json).",
'', 'The original credential and balance errors remain recorded. Recovery continued saved conversations with their remaining frozen turn/tool limits; it did not feed reference answers or silently replace bad outputs. Budget stops and missing repetitions are not treated as completed work. The native research brief requests the same search allowance, but the native product is not mechanically capped by the public harness; actual tool parity is not established.',
'','## Remaining qualification','',
'Complete the frozen cohort and repeat trials when funding and access allow; qualify references with two independent CRE reviewers; measure actual correction time and cross-file agreement; audit every research result; run dedicated native lender matching; and qualify authentic, rights-cleared deal packets. Coded original-file review packets and blank score sheets are generated by `tools/build-cre-review-packet.py`. No completed human acceptance or inter-reviewer agreement is claimed.',
'','Scoring v1.1 excludes three ambiguous ratio/capacity fields uniformly, fixes the revised occupancy-risk key and accepts equivalent citation objects. Original v1 grades and all unaltered answers are retained. Citation-location existence does not establish semantic support. See [scoring erratum](SCORING-ERRATUM.md), [rubric](../../benchmarks/cre-work-v2/RUBRIC.md) and [review protocol](../../benchmarks/cre-work-v2/REVIEW-PACKET.md).','']
(OUT/'REPORT.md').write_text('\n'.join(lines));print(OUT/'REPORT.md')
