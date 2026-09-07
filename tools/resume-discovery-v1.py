"""Continue frozen live research after funding; preserve all previous answers."""
import json,sys,time,hashlib,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from crebench.run_discovery_v1 import OUT,PRIVATE,BRIEFS,MODELS,SYSTEM,TOOLS,bridge
from crebench.run_workflow import Budget,model_call,save,digest
from crebench.run_pilot import credential,now
from crebench.workflow_tools import parse_json
plan=json.loads((OUT/'plan.json').read_text())
for f,h in plan['sha256'].items():
 if digest(ROOT/f)!=h:raise ValueError('Frozen source changed: '+f)
budget=Budget(15,PRIVATE)
for p in PRIVATE.glob('**/turn-*/attempt-*/result.json'):
 if json.loads(p.read_text()).get('http_status')==402:budget.reserved-=json.loads(p.with_name('started.json').read_text())['request_reservation_usd']
token=credential(ROOT/'.env.local');catalog={m['id']:m for m in json.loads((OUT/'catalog.json').read_text())['data']}
save(OUT/'funding-resumption.json',{'at':now(),'allocation_usd':15,'amendment':'../2026-09-07-cre-work-v2/BUDGET-AMENDMENT-1.md','runner_sha256':digest(__file__),'resume_policy':'Keep existing messages and remaining 16-turn and 8-search/8-open limits; no answer-key feedback.'})

def execute(cid,model):
 run=PRIVATE/model.replace('/','--')/cid;record=run/'result.json';old=json.loads(record.read_text()) if record.exists() else None
 if old and old['status'] not in ('budget_stop','infrastructure_error'):return old['status']
 if old:
  work=run/'funding-continuation';work.mkdir(exist_ok=False);save(work/'before-result.json',old)
  requests=sorted(run.glob('turn-*/attempt-1/request.json'));last=requests[-1];request=json.loads(last.read_text());messages=request['messages'];first=int(last.parent.parent.name.split('-')[1]);counts=old['tool_counts'].copy()
  response_path=last.with_name('response.json')
  if response_path.exists():
   msg=json.loads(response_path.read_text())['choices'][0]['message'];calls=msg.get('tool_calls',[]);messages.append({'role':'assistant','content':msg.get('content'),**({'tool_calls':calls} if calls else {})})
   for call in calls:
    name=call['function']['name'];args=parse_json(call['function']['arguments']);matches=[]
    for p in run.glob('web-*/request.json'):
     q=json.loads(p.read_text())
     if q['tool']==name and q['arguments']==args:matches.append(p.with_name('response.json'))
    if name in counts and counts[name]>8:answer={'error':'Tool allowance exhausted'}
    elif matches:answer=json.loads(sorted(matches)[-1].read_text())
    else:raise ValueError('Cannot reconstruct prior tool response without changing context')
    messages.append({'role':'tool','tool_call_id':call['id'],'content':json.dumps(answer,ensure_ascii=False,default=str)})
   first+=1
  save(work/'resume-context.json',messages)
  attempts=[json.loads(p.read_text()) for p in sorted(run.glob('turn-*/attempt-*/result.json'))]
 else:
  run.mkdir(parents=True);work=run;messages=[{'role':'system','content':SYSTEM},{'role':'user','content':(OUT/f'{cid}.md').read_text()}];first=1;counts={'web_search':0,'web_open':0};attempts=[];save(run/'started.json',{'at':now(),'case_id':cid,'model':model,'trial':1})
 (work/'input-views').mkdir(exist_ok=True);start=time.monotonic();web_calls=0;status='turn_limit'
 for turn in range(first,17):
  try:response,info=model_call({'model':model,'messages':messages,'max_tokens':16384,'tools':TOOLS,'tool_choice':'auto','stream':False},work,turn,token,budget,catalog[model]['pricing'])
  except ValueError:status='budget_stop';save(work/'resume-context.json',messages);break
  attempts+=info
  if response is None:status='infrastructure_error';break
  msg=response['choices'][0]['message'];calls=msg.get('tool_calls',[]);messages.append({'role':'assistant','content':msg.get('content'),**({'tool_calls':calls} if calls else {})})
  if not calls:status='incomplete';break
  done=False
  for call in calls:
   name=call['function']['name']
   try:
    args=parse_json(call['function']['arguments'])
    if name=='submit_results':save(run/'answer.json',args);answer={'submitted':True};done=True
    elif name in counts:
     counts[name]+=1
     if counts[name]>8:answer={'error':'Tool allowance exhausted'}
     else:web_calls+=1;answer=bridge(work,name,args,web_calls)
    else:answer={'error':'Unavailable tool'}
   except Exception as exc:answer={'error':str(exc)}
   save(work/f'turn-{turn:02d}'/(call['id']+'.tool.json'),{'name':name,'arguments':args,'result':answer})
   messages.append({'role':'tool','tool_call_id':call['id'],'content':json.dumps(answer,ensure_ascii=False,default=str)})
  if done:status='completed';break
 known=[a['usage']['cost'] for a in attempts if isinstance(a.get('usage',{}).get('cost'),(float,int))]
 result={'case_id':cid,'model':model,'trial':1,'status':status,'elapsed_seconds':time.monotonic()-start+(old or {}).get('elapsed_seconds',0),'known_partial_cost_usd':sum(known),'inference_cost_usd':sum(known) if len(known)==len(attempts) else None,'search_service_cost_usd':None,'tool_counts':counts,'verification_status':'pending source audit','operator_semantic_corrections':0,'administrative_continuation':bool(old)}
 save(run/'result.json',result);save(OUT/'runs'/model.replace('/','--')/cid/'result.json',result);save(work/'conversation.json',messages)
 save(OUT/'budget-status.json',{'api_observed_usd':budget.actual,'reserved_usd':budget.reserved,'limit_usd':15});return status

for cid,_ in BRIEFS:
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  statuses=list(pool.map(lambda m:execute(cid,m),MODELS))
 if 'infrastructure_error' in statuses or budget.reserved>=14.5:break
