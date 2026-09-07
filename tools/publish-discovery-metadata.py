"""Publish auditable model fact extracts, excluding retrieved article bodies."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/2026-09-07-live-discovery-v1'
allowed={'name','address_or_market','transaction_date','publication_date','property_type','size_sf','units','price_usd','annual_rent_psf','buyer_or_owner','contact_name','contact_role','contact_email','source_urls','original_loan_amount','original_loan_amount_usd','current_balance','current_balance_usd','maturity_date','loan_maturity_date','borrower_entity','borrower_owner'}
counts={}
for group,pattern in [('runs','*/*/result.json'),('native','*/*/result.json')]:
 for p in (OUT/group).glob(pattern):
  r=json.loads(p.read_text());private=ROOT/'work/cre-work-v2'/('native-discovery' if group=='native' else 'discovery')
  if group=='runs':private/=r['model'].replace('/','--')
  private/=r['case_id'];answer=private/'answer.json'
  if not answer.exists():continue
  original=json.loads(answer.read_text());rows=original.get('results',[])
  extracted=[{k:v for k,v in row.items() if k in allowed or (isinstance(v,(int,float)) and not isinstance(v,bool))} for row in rows]
  data={'case_id':r['case_id'],'model':r['model'],'trial':r['trial'],'verification':'Unverified model claims; see SOURCE-AUDIT.md for the limited fields inspected so far.','original_answer_sha256':hashlib.sha256(answer.read_bytes()).hexdigest(),'extraction':'Field values copied without corrections. Narrative explanations, search summaries, exclusions and retrieved pages are omitted; this is not the full original submission. Read the source audit for qualifications that affect interpretation.','results':extracted}
  (p.parent/'fact-extract.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
  r['returned_count']=len(rows);r['fact_extract']='fact-extract.json'
  if group=='runs':
   executed={'web_search':0,'web_open':0}
   for request in private.glob('**/web-*/request.json'):
    kind=json.loads(request.read_text())['tool'];executed[kind]+=1
   assert all(n<=8 for n in executed.values()),executed
   r['executed_web_requests']=executed
   r['tool_count_semantics']='tool_counts includes rejected excess requests; executed_web_requests counts dispatched searches and page opens.'
  if r['case_id'] in ['atlanta-mf-sales','dallas-industrial-sales','phoenix-industrial-leases','office-refinance-2027']:r['verification_status']='Partial author source inspection; full score pending'
  p.write_text(json.dumps(r,indent=2)+'\n');counts[r['model']]=counts.get(r['model'],0)+len(rows)
print(json.dumps({'model_claims_extracted':counts,'fully_verified_precision':None}))
