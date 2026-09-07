"""Administrative continuation after HTTP 402, preserving context and turn limits."""
import base64,hashlib,json,sys,time,concurrent.futures,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from crebench.run_work_v2 import run_one,BASE,MODELS,TOOLS
from crebench.work_v2_tools import WorkContext
from crebench.run_workflow import Budget,model_call,save,digest
from crebench.run_pilot import credential,now
from crebench.workflow_tools import parse_json
from crebench.grade_work_v2 import grade
OUT=ROOT/'experiments/2026-09-07-cre-work-v2';REC=OUT/'credential-resumption'
plan=json.loads((OUT/'plan.json').read_text());catalog={m['id']:m for m in json.loads((OUT/'catalog.json').read_text())['data']}
for p,h in plan['sha256'].items():
 if digest(ROOT/p)!=h:raise ValueError('Frozen inputs changed: '+p)
budget=Budget(plan['api_budget_usd'],REC)
# A 402 refused inference; retain the refusal record and release its request
# reservation for continuation. Unknown transport charges remain reserved.
released=0
for p in REC.glob('**/turn-*/attempt-*/result.json'):
 if json.loads(p.read_text()).get('http_status')==402:
  released+=json.loads(p.with_name('started.json').read_text())['request_reservation_usd']
budget.reserved-=released;token=credential(ROOT/'.env.local')
save(REC/'funding-resumption.json',{'at':now(),'reason':'User authorized $100 gateway credit purchase; same cumulative $200 token authorization and $40 workflow allocation.','request_reservations_released_for_http402':released,'runner_sha256':digest(__file__),'selection':'All billing-interrupted runs, original order. No answered content discarded; rejected request context hash checked. No extra successful turns allowed.'})

def resume(run):
 last=json.loads((run/'result.json').read_text())
 if last['status']!='infrastructure_error':return last['status']
 stage=last['stages_recorded'][-1];old=json.loads((run/f'result-{stage}.json').read_text())
 failures=[p for p in run.glob('turn-*/attempt-*/result.json') if json.loads(p.read_text()).get('http_status')==402]
 if not failures:return 'infrastructure_error'
 failed=sorted(failures)[-1];request=json.loads(failed.with_name('request.json').read_text())
 for m in request['messages']:
  if isinstance(m.get('content'),list):
   for p in m['content']:
    if p.get('type')=='image_url' and p['image_url']['url'].startswith('artifact://'):
     p['image_url']['url']='data:image/png;base64,'+base64.b64encode((run/p['image_url']['url'].removeprefix('artifact://')).read_bytes()).decode()
 wire=hashlib.sha256(json.dumps(request,allow_nan=False).encode()).hexdigest()
 assert wire==json.loads(failed.with_name('started.json').read_text())['wire_sha256'],'Interrupted request changed'
 cont=run/'funding-continuation';cont.mkdir(exist_ok=False);(cont/'input-views').mkdir()
 for p in run.glob('*.json'):
  if p.name.startswith(('result','grade','artifact-audit')) or p.name=='conversation.json':shutil.copyfile(p,cont/('before-'+p.name))
 case=BASE/'cases'/old['case_id'];ctx=WorkContext(case,run);ctx.versions=old['artifact_versions'].copy()
 if old.get('latest_workbook'):
  ctx.latest_workbook=run/old['latest_workbook'];ctx.latest_spec=ctx.latest_workbook.with_suffix('.json')
  cached=run/'recalculated'/ctx.latest_workbook.stem/ctx.latest_workbook.name;ctx.latest_cached=cached if cached.exists() else None
 messages=request['messages'];turn_global=int(failed.parent.parent.name.split('-')[1]);final_status=None
 for st in ['initial','revision'][['initial','revision'].index(stage):]:
  ctx.stage=st;ctx.done=False;begin=time.monotonic();prior=old if st==stage else {};attempts=list(prior.get('attempts',[]));count=prior.get('tool_calls',0);reminded=any(m.get('role')=='user' and str(m.get('content','')).startswith('Complete the requested files and call submit_analysis.') for m in messages)
  if st==stage:
   started=json.loads((run/f'stage-{st}-started.json').read_text())['at'];first_turn=sum(json.loads(p.read_text())['at']>=started for p in run.glob('turn-*/attempt-1/started.json'))
  else:
   first_turn=1;messages.append({'role':'user','content':(case/'revision.md').read_text()+'\n\nAvailable files: '+', '.join(x['name'] for x in ctx.call('list_files',{})['files'])});save(run/'stage-revision-started.json',{'at':now(),'prior_versions':ctx.versions.copy(),'brief_sha256':digest(case/'revision.md')})
  status='turn_limit'
  for turn in range(first_turn,plan['max_turns_per_stage']+1):
   if time.monotonic()-begin+prior.get('elapsed_seconds',0)>1800:status='time_limit';break
   request={'model':old['model'],'messages':messages,'max_tokens':plan['max_output_tokens'],'stream':False,'tools':TOOLS,'tool_choice':'auto'}
   try:response,info=model_call(request,cont,turn_global,token,budget,catalog[old['model']]['pricing'])
   except ValueError:status='budget_stop';break
   attempts+=info
   if response is None:status='infrastructure_error';break
   msg=response['choices'][0]['message'];calls=msg.get('tool_calls') or [];messages.append({'role':'assistant','content':msg.get('content'),**({'tool_calls':calls} if calls else {})})
   if msg.get('content'):(cont/f'turn-{turn_global:02d}'/'answer.txt').write_text(msg['content'])
   if not calls:
    if not reminded:messages.append({'role':'user','content':'Complete the requested files and call submit_analysis. Record actual blockers; do not claim files without creating them.'});reminded=True
    else:status='incomplete';break
   for i,call in enumerate(calls,1):
    count+=1;name=call['function']['name'];raw=call['function']['arguments'];record={'name':name,'arguments_raw':raw,'call_id':call['id']}
    try:
     if count>plan['max_tools_per_stage']:raise ValueError('Stage tool-call limit')
     args=parse_json(raw);output=ctx.call(name,args);record.update(arguments=args,result=output,status='ok')
    except Exception as exc:output={'error':str(exc)};record.update(result=output,status='error')
    save(cont/f'turn-{turn_global:02d}'/f'tool-{i:02d}.json',record);messages.append({'role':'tool','tool_call_id':call['id'],'content':json.dumps(output,allow_nan=False,default=str)})
   if ctx.images:
    messages.append({'role':'user','content':[{'type':'text','text':'Requested PDF page images in tool-request order; see preceding results for filenames/pages.'}]+[{'type':'image_url','image_url':{'url':'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()}} for p in ctx.images]});ctx.images=[]
   print(json.dumps({'resumed':old['case_id'],'model':old['model'],'stage':st,'turn':turn,'spent':budget.actual}),flush=True);turn_global+=1
   if ctx.done:status='completed';break
   if count>=plan['max_tools_per_stage']:status='tool_limit';break
  known=[a.get('usage',{}).get('cost') for a in attempts if isinstance(a.get('usage',{}).get('cost'),(float,int))]
  r={**old,'stage':st,'status':status,'completed_at':now(),'elapsed_seconds':time.monotonic()-begin+prior.get('elapsed_seconds',0),'attempts':attempts,'known_partial_cost_usd':sum(known),'cost_usd':sum(known) if len(known)==len(attempts) else None,'tool_calls':count,'model_calls_including_retries':len(attempts),'artifact_versions':ctx.versions.copy(),'latest_workbook':str(ctx.latest_workbook.relative_to(run)) if ctx.latest_workbook else None,'latest_memo':f'artifacts/memorandum-v{ctx.versions["memo"]}.pdf' if ctx.versions['memo'] else None,'administrative_resumption':'HTTP402 credit interruption; original result in funding-continuation/before-result files'}
  save(run/f'result-{st}.json',r);ap=run/f'analysis-{st}.json';save(run/f'grade-{st}.json',grade(case,json.loads(ap.read_text()) if ap.exists() else {},st))
  audit=run/f'artifact-audit-{st}.json'
  if audit.exists():audit.unlink() # Derived audit is preserved above; recheck delivered versions.
  final_status=status
  if status!='completed':break
 save(cont/'conversation.json',messages);save(run/'result.json',{**last,'status':final_status,'stages_recorded':[s for s in ['initial','revision'] if (run/f'result-{s}.json').exists()]});return final_status

for cid in plan['cases']:
 for model in MODELS:
  run=REC/'api/trial-1'/model.replace('/','--')/cid
  result=resume(run) if run.exists() else run_one(BASE/'cases'/cid,run,model,1,token,budget,catalog[model]['pricing'],plan)
  save(REC/'budget-status.json',{'at':now(),'api_observed_usd':budget.actual,'api_conservatively_reserved_usd':budget.reserved,'api_limit_usd':budget.limit})
  if result in ('infrastructure_error','budget_stop'):sys.exit(0)
