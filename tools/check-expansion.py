"""Fail publication on inconsistent coverage, stale artifact audits or frozen inputs."""
import hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/2026-09-07-cre-work-v2'
D=json.loads((OUT/'results.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=0
for rel in ['2026-09-07-cre-work-v2','2026-09-07-live-discovery-v1','2026-09-07-lender-qualification-v1']:
 plan=json.loads((ROOT/'experiments'/rel/'plan.json').read_text())
 for f,h in plan.get('sha256',{}).items():assert sha(ROOT/f)==h,('Frozen source changed',f);frozen+=1
seen=set()
for r in D['rows']:
 key=(r['model'],r['case_id'],r['stage'],r['trial']);assert key not in seen,key;seen.add(key)
 p=ROOT/r['run_path'];g=json.loads((p/f"grade-{r['stage']}-v1.1.json").read_text())
 assert r['scores']==g['scores'];assert sum(s['total'] for s in r['scores'].values())==38
 assert all(0<=s['passed']<=s['total'] for s in r['scores'].values())
 assert g['professional_acceptance'] is None
 for v in [r['cost_usd'],r.get('known_partial_cost_usd')]:assert v is None or (math.isfinite(v) and v>=0)
 if r['status']=='completed':
  assert r['analysis_present'];assert r['audit'] is not None,('Missing artifact audit',key)
  expected={str((ROOT/v).relative_to(p)) for v in r['artifacts'].values() if v}
  assert expected==set(r['audit']['original_hashes']),('Stale audit paths',key)
  for rel,h in r['audit']['original_hashes'].items():assert sha(p/rel)==h,('Changed original artifact',key,rel)
keys=[{(r['case_id'],r['stage'],r['trial']) for r in D['rows'] if r['model']==m and r['status']=='completed'} for m in D['primary_models']]
assert set(map(tuple,D['matched_keys']))==set.intersection(*keys)
assert len(D['matched_rows'])==len(D['matched_keys'])*len(D['primary_models'])
for c in D['conditions']:
 rows=[r for r in D['rows'] if r['model']==c['model']]
 assert c['recorded_stages']==len(rows);assert c['completed_stages']==sum(r['status']=='completed' for r in rows)
assert sum(c['target_stages'] for c in D['conditions'])==720
b=D['budget'];assert sum(b[k] for k in ['prior_reservation_usd','workflow_api_allocation_usd','discovery_api_allocation_usd','lender_api_allocation_usd','native_allocation_usd'])==b['project_token_limit_usd']==200
assert D['authentic_customer_deals']==0 and D['authoring_families']==4
assert D['professional_acceptance'] is None and D['human_minutes'] is None
print(json.dumps({'frozen_hashes_checked':frozen,'workflow_rows_checked':len(D['rows']),'matched_stages':len(D['matched_keys']),'target_stages':720,'budget_limit_usd':200}))
