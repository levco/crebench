"""Resume budget stops with identical messages and the original remaining limits."""
import argparse,json,re,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from crebench.run_discovery_v1 import OUT,PRIVATE,BRIEFS,MODELS,TOOLS,bridge
from crebench.run_workflow import Budget,model_call,save,digest
from crebench.run_pilot import credential,now
from crebench.workflow_tools import parse_json
parser=argparse.ArgumentParser();parser.add_argument('--label',required=True);parser.add_argument('--limit',type=float,default=20);parser.add_argument('--amendment',default='../2026-09-07-cre-work-v2/BUDGET-AMENDMENT-2.md');args_cli=parser.parse_args()
if not re.fullmatch(r'[a-z0-9-]+',args_cli.label):raise ValueError('Invalid continuation label')
plan=json.loads((OUT/'plan.json').read_text())
for f,h in plan['sha256'].items():
 if digest(ROOT/f)!=h:raise ValueError('Frozen source changed: '+f)
budget=Budget(args_cli.limit,PRIVATE)
for p in PRIVATE.glob('**/turn-*/attempt-*/result.json'):
 if json.loads(p.read_text()).get('http_status')==402:budget.reserved-=json.loads(p.with_name('started.json').read_text())['request_reservation_usd']
token=credential(ROOT/'.env.local');catalog={m['id']:m for m in json.loads((OUT/'catalog.json').read_text())['data']}
save(OUT/(args_cli.label+'-resumption.json'),{'at':now(),'allocation_usd':args_cli.limit,'amendment':args_cli.amendment,'runner_sha256':digest(__file__),'policy':'Saved messages only; original remaining turns and tools; turn-limit runs excluded.'})
def execute(cid,model):
 run=PRIVATE/model.replace('/','--')/cid;old=json.loads((run/'result.json').read_text())
 if old['status']!='budget_stop':return old['status']
 prior=max(run.glob('**/conversation.json'),key=lambda p:p.stat().st_mtime_ns)
 messages=json.loads(prior.read_text());first=1+sum(m['role']=='assistant' for m in messages)
 work=run/(args_cli.label+'-continuation');work.mkdir(exist_ok=False);(work/'input-views').mkdir()
 save(work/'before-result.json',old);save(work/'resume-context.json',messages)
 save(work/'provenance.json',{'at':now(),'source_conversation':str(prior.relative_to(run)),'source_sha256':digest(prior),'first_turn':first})
 attempts=[json.loads(p.read_text()) for p in sorted(run.glob('**/turn-*/attempt-*/result.json'))]
 counts=old['tool_counts'].copy();start=time.monotonic();web_calls=0;status='turn_limit'
 for turn in range(first,17):
  try:response,info=model_call({'model':model,'messages':messages,'max_tokens':16384,'tools':TOOLS,'tool_choice':'auto','stream':False},work,turn,token,budget,catalog[model]['pricing'])
  except ValueError:status='budget_stop';break
  attempts+=info
  if response is None:status='infrastructure_error';break
  msg=response['choices'][0]['message'];calls=msg.get('tool_calls',[]);messages.append({'role':'assistant','content':msg.get('content'),**({'tool_calls':calls} if calls else {})})
  if not calls:status='incomplete';break
  done=False
  for call in calls:
   name=call['function']['name'];args={}
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
  print(json.dumps({'brief':cid,'model':model,'turn':turn,'cost_so_far':budget.actual}),flush=True)
  if done:status='completed';break
 known=[a['usage']['cost'] for a in attempts if isinstance(a.get('usage',{}).get('cost'),(float,int))]
 result={**old,'status':status,'elapsed_seconds':old['elapsed_seconds']+time.monotonic()-start,'known_partial_cost_usd':sum(known),'inference_cost_usd':sum(known) if len(known)==len(attempts) else None,'tool_counts':counts,'administrative_continuation':True}
 save(run/'result.json',result);save(OUT/'runs'/model.replace('/','--')/cid/'result.json',result);save(work/'conversation.json',messages)
 save(OUT/'budget-status.json',{'api_observed_usd':budget.actual,'reserved_usd':budget.reserved,'limit_usd':args_cli.limit});return status
for cid,_ in BRIEFS:
 statuses=[execute(cid,m) for m in MODELS]
 if 'infrastructure_error' in statuses:break
