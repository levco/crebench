"""Create original-byte coded work products and blank human review forms."""
import csv,hashlib,json,random,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'experiments/2026-09-07-cre-work-v2/results.json').read_text())
OUT=ROOT/'work/cre-work-v2/reviewer-packet';OUT.mkdir(parents=True,exist_ok=True)
for sheet in (OUT/'reviewer').glob('reviewer-*.csv'):
 with sheet.open(newline='') as f:
  for entry in csv.DictReader(f):
   if any(v for k,v in entry.items() if k not in ['code','case_id','stage']):raise ValueError('Existing human review must not be overwritten: '+str(sheet))
rows=[r for r in D['rows'] if r['status']=='completed'];random.Random(20260907).shuffle(rows)
mapping=[];forms=[]
for i,r in enumerate(rows,1):
 code=f'R{i:03d}';folder=OUT/'reviewer'/code;folder.mkdir(parents=True,exist_ok=True)
 hashes={}
 for kind,rel in r['artifacts'].items():
  if not rel:continue
  source=ROOT/rel;dest=folder/(kind+source.suffix);shutil.copyfile(source,dest)
  digest=hashlib.sha256(dest.read_bytes()).hexdigest()
  assert digest==hashlib.sha256(source.read_bytes()).hexdigest();hashes[dest.name]=digest
 case=ROOT/'benchmarks/cre-work-v2/cases'/r['case_id']
 context=OUT/'reviewer/sources'/r['case_id']
 shutil.copytree(case/'sources',context/'initial',dirs_exist_ok=True)
 shutil.copyfile(case/'brief.md',folder/'initial-brief.md')
 if r['stage']=='revision':
  shutil.copytree(case/'revision',context/'revision',dirs_exist_ok=True)
 shutil.copyfile(case/('brief.md' if r['stage']=='initial' else 'revision.md'),folder/'brief.md')
 mapping.append({'code':code,'case_id':r['case_id'],'stage':r['stage'],'model':r['model'],'trial':r['trial'],'original_run':r['run_path'],'sha256':hashes})
 forms.append({'code':code,'case_id':r['case_id'],'stage':r['stage']})
fields=['code','case_id','stage','reviewer','readiness_0_to_3','critical_failure','verification_minutes','correction_minutes','cross_file_agreement','revision_preserved_facts','identity_cue','source_disagreement','required_corrections','notes']
for reviewer in ['A','B']:
 with (OUT/'reviewer'/f'reviewer-{reviewer}.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(forms)
(OUT/'mapping.private.json').write_text(json.dumps(mapping,indent=2)+'\n')
shutil.copyfile(ROOT/'benchmarks/cre-work-v2/REVIEW-PACKET.md',OUT/'reviewer/INSTRUCTIONS.md')
print(json.dumps({'coded_stages':len(rows),'directory':str(OUT),'human_grades_completed':0}))
