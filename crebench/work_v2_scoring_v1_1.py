"""Disclosed scoring correction; never alters model facts or original grades."""
import copy,json
from .grade_work_v2 import grade as original_grade,equivalent


def score(case,analysis,stage):
 original=original_grade(case,analysis,stage);result=copy.deepcopy(original);result['scoring_version']='1.1';result['adjustments']=[]
 # After the last pending occupant takes possession, the current occupancy risk resolves.
 # The immutable author key incorrectly carried the initial pending count into revision risk.
 reference=json.loads((case/'reference.json').read_text())
 if stage=='revision' and reference['revision']['pending_units']==0 and reference['initial']['pending_units']>0:
  field=next(c for c in result['checks'] if c['field']=='risk_pending_in_occupancy');before=field['passed'];field['original_expected']=field['expected'];field['expected']='absent'
  supplied=[f for f in analysis.get('fields',[]) if f.get('id')==field['field']]
  field['passed']=len(supplied)==1 and equivalent(field['field'],field['actual'],'absent')
  result['scores']['judgment']['passed']+=int(field['passed'])-int(before)
  result['adjustments'].append({'field':field['field'],'reason':'Current revised roll has zero pending occupants; original key retained initial risk incorrectly.','original_expected':'present','corrected_expected':'absent'})
 risks=[r for r in result['checks'] if r['field'].startswith('risk_')]
 result['risk_counts']={'true_positives':sum(r['expected']=='present' and r['actual']=='present' for r in risks),'false_positives':sum(r['expected']=='absent' and r['actual']=='present' for r in risks),'false_negatives':sum(r['expected']=='present' and r['actual']!='present' for r in risks)}
 # The brief allows evidence arrays and does not forbid file/location objects.
 normalized=copy.deepcopy(analysis)
 for f in normalized.get('fields',[]):
  if isinstance(f.get('evidence'),list):
   f['evidence']=[(str(e.get('file',''))+' '+str(e.get('loc',e.get('location','')))) if isinstance(e,dict) else e for e in f['evidence']]
 normalized_grade=original_grade(case,normalized,stage)
 for row,new in zip(result['checks'],normalized_grade['checks']):
  if row['citation_location_present']!=new['citation_location_present']:
   result['adjustments'].append({'field':row['field'],'reason':'Lossless file/location evidence-object mapping; financial value unchanged.'})
   row['citation_location_present']=new['citation_location_present']
 # The field names do not say dollars or ratios. Do not score this ambiguity
 # as a finance error, and do not reward either interpretation selectively.
 ambiguous={'ltv_limit','dscr_limit','debt_yield_limit'}
 for row in result['checks']:
  row['scored']=row['field'] not in ambiguous
  if not row['scored']:
   result['scores']['financial']['total']-=1
   result['scores']['financial']['passed']-=int(row['passed'])
   result['adjustments'].append({'field':row['field'],'reason':'Unscored for every provider: brief does not distinguish covenant ratio from dollar loan capacity. Original expected and actual values retained.'})
 result['professional_acceptance']=None
 return result
