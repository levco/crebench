"""Replay disclosed scores and expose incomplete coverage without ranking it."""
import csv,json,sys,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from crebench.work_v2_scoring_v1_1 import score
from crebench.grade_work_v2 import grade as original_grade
OUT=ROOT/'experiments/2026-09-07-cre-work-v2';BASE=ROOT/'benchmarks/cre-work-v2/cases'
LABELS={'lev/native':'Lev Agent','openai/gpt-5':'GPT-5 API agent','anthropic/claude-opus-5':'Opus 5 API agent','anthropic/claude-opus-4.7':'Opus 4.7 API agent','claude/consumer-opus-5-high':'Claude Chat · Opus 5 High'}
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def collect():
 rows=[]
 for folder in ['credential-resumption/api','native','consumer']:
  for p in sorted((OUT/folder).glob('trial-*/*/*/result-*.json')):
   if p.name not in ('result-initial.json','result-revision.json'):continue
   r=json.loads(p.read_text());stage=r['stage'];ap=p.with_name(f'analysis-{stage}.json');a=json.loads(ap.read_text()) if ap.exists() else {};g=score(BASE/r['case_id'],a,stage);save(p.with_name(f'grade-{stage}-v1.1.json'),g)
   original=p.with_name(f'grade-{stage}.json')
   if not original.exists():save(original,{**original_grade(BASE/r['case_id'],a,stage),'grade_provenance':'Frozen v1 grader replay on unaltered delivered analysis; not an execution-time grade.'})
   audit=p.with_name(f'artifact-audit-{stage}.json');audit=json.loads(audit.read_text()) if audit.exists() else None
   cost=r.get('cost_usd');basis='Gateway reported'
   if r['model']=='lev/native':cost=r.get('estimated_inference_cost_usd');basis='Native trace estimate'
   if r['model'].startswith('claude/'):basis='Unmeasured consumer inference'
   rows.append({'case_id':r['case_id'],'stage':stage,'trial':r['trial'],'model':r['model'],'label':LABELS[r['model']],'status':r['status'],'analysis_present':ap.exists(),'scores':g['scores'],'critical_errors':g['critical_errors'],'risk_counts':g['risk_counts'],'citation_locations':sum(c['citation_location_present'] for c in g['checks'] if c.get('scored',True)),'audit':audit,'cost_usd':cost,'known_partial_cost_usd':r.get('known_partial_cost_usd',cost),'cost_basis':basis,'elapsed_seconds':r.get('elapsed_seconds'),'run_path':str(p.parent.relative_to(ROOT)),'artifacts':{k:str((p.parent/r[v]).relative_to(ROOT)) if r.get(v) and (p.parent/r[v]).exists() else None for k,v in [('workbook','latest_workbook'),('om','latest_memo')]}})
 for r in rows:
  g=json.loads((ROOT/r['run_path']/f"grade-{r['stage']}-v1.1.json").read_text());r['error_magnitude']={}
  for field in ['annual_in_place_rent','uw_noi','maximum_loan']:
   check=next(c for c in g['checks'] if c['field']==field);actual=check['actual'];expected=check['expected']
   if type(actual) in (int,float) and type(expected) in (int,float) and expected:
    r['error_magnitude'][field]={'difference_usd':actual-expected,'absolute_percent':abs(actual-expected)/abs(expected)*100}
   else:r['error_magnitude'][field]=None
 conditions=[]
 for model,label in LABELS.items():
  selected=[r for r in rows if r['model']==model];conditions.append({'model':model,'label':label,'target_stages':120,'recorded_stages':len(selected),'completed_stages':sum(r['status']=='completed' for r in selected),'cases_started':len(set(r['case_id'] for r in selected)),'cost_recorded_usd':sum(r['cost_usd'] or r['known_partial_cost_usd'] or 0 for r in selected),'cost_missing_stages':sum(r['cost_usd'] is None for r in selected),'cost_basis':selected[0]['cost_basis'] if selected else 'Unknown'})
 conditions.append({'model':'chatgpt/consumer-agent','label':'ChatGPT agent product','target_stages':120,'recorded_stages':0,'completed_stages':0,'cases_started':0,'cost_recorded_usd':0,'cost_missing_stages':0,'cost_basis':'Access pending; no measured run'})
 primary_models=[m for m in LABELS if not m.startswith('claude/')]
 keys=[{(r['case_id'],r['stage'],r['trial']) for r in rows if r['model']==m and r['status']=='completed'} for m in primary_models]
 matched_keys=set.intersection(*keys) if keys else set();matched=[r for r in rows if r['model'] in primary_models and (r['case_id'],r['stage'],r['trial']) in matched_keys]
 consumer_keys=matched_keys & {(r['case_id'],r['stage'],r['trial']) for r in rows if r['model'].startswith('claude/') and r['status']=='completed'}
 consumer_rows=[r for r in rows if (r['case_id'],r['stage'],r['trial']) in consumer_keys]
 lender=[];ld=ROOT/'experiments/2026-09-07-lender-qualification-v1'
 for folder,pattern in [('runs','trial-*/*/*/result.json'),('native','trial-*/*/*/result.json')]:
  for p in sorted((ld/folder).glob(pattern)):
   r=json.loads(p.read_text());gp=p.with_name('grade.json');g=json.loads(gp.read_text()) if gp.exists() else {};lender.append({**{k:r.get(k) for k in ['case_id','model','trial','status','inference_cost_usd','estimated_inference_cost_usd','known_partial_cost_usd']},'grade':g,'run_path':str(p.parent.relative_to(ROOT))})
 discovery=[];dd=ROOT/'experiments/2026-09-07-live-discovery-v1'
 for p in sorted((dd/'runs').glob('*/*/result.json')):discovery.append({**json.loads(p.read_text()),'run_path':str(p.parent.relative_to(ROOT))})
 for p in sorted((dd/'native').glob('*/*/result.json')):discovery.append({**json.loads(p.read_text()),'run_path':str(p.parent.relative_to(ROOT))})
 data={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Partial diagnostic expansion; independent CRE qualification pending','scoring_version':'1.1','distinct_deal_packets':20,'authoring_families':4,'authentic_customer_deals':0,'target_workflow_stages':720,'conditions':conditions,'matched_keys':[list(k) for k in sorted(matched_keys)],'matched_rows':matched,'rows':rows,'lender_rows':lender,'lender_target_per_condition':24,'discovery_rows':discovery,'discovery_target_briefs':6,'discovery_target_repetitions':3,'professional_acceptance':None,'human_minutes':None,'budget':{'project_token_limit_usd':200,'prior_reservation_usd':110,'workflow_api_allocation_usd':40,'discovery_api_allocation_usd':15,'lender_api_allocation_usd':2,'native_allocation_usd':33}}
 data['budget'].update(workflow_api_allocation_usd=37,discovery_api_allocation_usd=26,native_allocation_usd=25)
 data.update(primary_models=primary_models,consumer_comparison_keys=[list(k) for k in sorted(consumer_keys)],consumer_comparison_rows=consumer_rows)
 save(OUT/'results.json',data)
 with (OUT/'run-summary.csv').open('w',newline='') as f:
  fields=['case_id','stage','trial','label','status','ingestion_passed','ingestion_total','financial_passed','financial_total','judgment_passed','judgment_total','critical_errors','cost_usd','known_partial_cost_usd','cost_basis','run_path'];writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
  for r in rows:
   flat={k:r[k] for k in fields if k in r}
   for group,s in r['scores'].items():flat[group+'_passed']=s['passed'];flat[group+'_total']=s['total']
   writer.writerow(flat)
 print(json.dumps({'workflow_recorded':len(rows),'completed':sum(r['status']=='completed' for r in rows),'matched_stage_cases':len(matched_keys),'lender_recorded':len(lender),'discovery_recorded':len(discovery)}))
 return data
if __name__=='__main__':collect()
