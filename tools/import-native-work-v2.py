"""Import already observed original UI outputs, without repairing model content."""
import json,sys,shutil,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from crebench.work_v2_scoring_v1_1 import score
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
cid,stage,provider=sys.argv[1:4]
private=ROOT/'work/cre-work-v2'/('native' if provider=='lev-agent' else 'consumer-claude')/cid
run=ROOT/'experiments/2026-09-07-cre-work-v2'/('native' if provider=='lev-agent' else 'consumer')/'trial-1'/provider/cid
run.mkdir(parents=True,exist_ok=True);art=run/'artifacts';art.mkdir(exist_ok=True)
blocks=json.loads((private/f'code-blocks-{stage}.json').read_text());analysis=json.loads(blocks[-1])
save(run/f'analysis-{stage}.json',analysis)
session=None
for kind,ext in [('workbook','xlsx'),('pdf','pdf')]:
 dest=art/f'{"underwriting" if kind=="workbook" else "om"}-{stage}.{ext}'
 if not dest.exists():
  if provider=='lev-agent':
   raw=(private/f'{kind}-embed-{stage}.private.txt').read_text();url=urllib.parse.parse_qs(urllib.parse.urlsplit(raw).query)['src'][0] if kind=='workbook' else raw
   with urllib.request.urlopen(url,timeout=90) as response:dest.write_bytes(response.read())
  else:
   suffix='-rev2' if stage=='revision' else ''
   source=Path('/Users/yjzar/Downloads')/(('magnolia-terrace-underwriting' if kind=='workbook' else 'magnolia-terrace-offering-memorandum')+suffix+'.'+ext)
   shutil.copyfile(source,dest)
 if provider=='lev-agent':
  raw=(private/f'{kind}-embed-{stage}.private.txt').read_text();url=urllib.parse.parse_qs(urllib.parse.urlsplit(raw).query)['src'][0] if kind=='workbook' else raw
  parts=urllib.parse.urlsplit(url).path.split('/');session=next((s for s in parts if len(s)==36),None)
submission=json.loads((private/('submission.json' if stage=='initial' else 'submission-revision.json')).read_text())
completion=private/f'completed-{stage}.json'
result={'case_id':cid,'model':'lev/native' if provider=='lev-agent' else 'claude/consumer-opus-5-high','trial':1,'stage':stage,'status':'completed','started_at':submission.get('started_at',submission.get('at')),'completed_at':json.loads(completion.read_text()).get('observed_completed_at') if completion.exists() else None,'latest_workbook':f'artifacts/underwriting-{stage}.xlsx','latest_memo':f'artifacts/om-{stage}.pdf','cost_usd':None,'estimated_inference_cost_usd':None,'cost_basis':'Pending matched trace' if provider=='lev-agent' else 'Consumer UI does not expose per-task inference cost; existing subscription, no incremental subscription purchase.','operator_semantic_corrections':0,'input_map_source':'unaltered final JSON','session_id':session}
if not (run/f'result-{stage}.json').exists():save(run/f'result-{stage}.json',result)
save(run/f'grade-{stage}-v1.1.json',score(ROOT/'benchmarks/cre-work-v2/cases'/cid,analysis,stage))
print(json.dumps({'run':str(run.relative_to(ROOT)),'stage':stage,'session_id':session,'bytes':{p.name:p.stat().st_size for p in art.iterdir()}}))
