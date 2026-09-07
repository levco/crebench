"""Resume first-call authentication rejections without discarding their evidence."""
import concurrent.futures,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from crebench.run_work_v2 import run_one,BASE,MODELS,SYSTEM
from crebench.run_pilot import credential,now
from crebench.run_workflow import Budget,digest,save
OUT=ROOT/'experiments/2026-09-07-cre-work-v2';RECOVERY=OUT/'credential-resumption'
plan=json.loads((OUT/'plan.json').read_text())
for file,expected in plan['sha256'].items():
 if digest(ROOT/file)!=expected:raise ValueError('Frozen file changed: '+file)
# Only first-call 401s with no usage and no returned model may be administratively resumed.
for result in OUT.glob('api/**/attempt-*/result.json'):
 d=json.loads(result.read_text())
 if d.get('http_status')!=401 or d.get('usage') or d.get('returned_model'):raise ValueError('Non-auth response in original interrupted phase')
RECOVERY.mkdir(exist_ok=True)
for name in ('plan.json','catalog.json'):
 target=RECOVERY/name
 if not target.exists():target.write_bytes((OUT/name).read_bytes())
save(RECOVERY/'resumption.json',{'at':now(),'reason':'Existing OIDC credential expired; first-call HTTP 401s. No model answers returned. Same frozen inputs, prompts, models and graders.','original_http_401_count':len(list(OUT.glob('api/**/attempt-*/result.json'))),'billing_treatment':'No inference observed for rejected unauthenticated requests; cost remains unreported. Prior-project headroom retains unknown-cost contingency. Original request reservations released only for this administrative retry.','runner_sha256':digest(__file__)})
budget=Budget(plan['api_budget_usd'],RECOVERY);token=credential(ROOT/'.env.local');catalog={m['id']:m for m in json.loads((OUT/'catalog.json').read_text())['data']}
# Stop the entire dispatch on auth/billing interruption rather than flooding the queue.
for trial in range(1,2):
 for cid in plan['cases']:
  if budget.reserved>=budget.limit-1:break
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
   jobs=[pool.submit(run_one,BASE/'cases'/cid,RECOVERY/'api'/f'trial-{trial}'/m.replace('/','--')/cid,m,trial,token,budget,catalog[m]['pricing'],plan) for m in MODELS]
   statuses=[job.result() for job in jobs]
  save(RECOVERY/'budget-status.json',{'at':now(),'api_observed_usd':budget.actual,'api_conservatively_reserved_usd':budget.reserved,'api_limit_usd':budget.limit})
  if 'infrastructure_error' in statuses:print('Dispatch paused on infrastructure error',flush=True);break
