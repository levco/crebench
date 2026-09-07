"""Content grading; location existence is explicitly separate from support."""
import json,math,re
from pathlib import Path
import openpyxl
from pypdf import PdfReader

RATIOS={'unit_occupancy','area_occupancy','sizing_rate','cap_rate'}
COUNTS={'total_units','occupied_units','pending_units','total_area_sf','occupied_area_sf'}

def equivalent(field,value,expected):
 if isinstance(value,dict):
  unit=value.get('unit');allowed={'ratio','decimal','fraction'} if field in RATIOS else {'count','units','suites','SF','sf','square feet'} if field in COUNTS or field.endswith(('_units','_occupied')) else {'USD','usd','$','USD/year','USD/month'}
  if unit not in allowed:return False
  value=value.get('value')
 if expected is None:return value is None or isinstance(value,str) and value.strip().lower() in ('unknown','not provided','not available','unresolved')
 if isinstance(expected,str):return isinstance(value,str) and value.strip().lower()==expected.lower()
 if isinstance(value,str):
  s=value.strip();negative=s.startswith('(') and s.endswith(')');percent=s.endswith('%');s=s.strip('()').replace('$','').replace(',','').rstrip('%')
  try:value=float(s)*(-1 if negative else 1)/(100 if percent else 1)
  except ValueError:return False
 if type(value) not in (int,float) or not math.isfinite(value):return False
 tol=.0001 if field in RATIOS else 0 if field in COUNTS or field.endswith(('_units','_occupied')) else max(1,abs(expected)*.0001)
 return abs(value-expected)<=tol


def grade(case,analysis,stage='initial'):
 case=Path(case);key=json.loads((case/'reference.json').read_text());ref=key[stage];fields={};duplicates=set()
 for item in analysis.get('fields',[]):
  field=item.get('id')
  if field in fields:duplicates.add(field)
  fields[field]=item
 rows=[]
 for field,expected in ref.items():
  item=fields.get(field,{});actual=item.get('value');passed=field in fields and field not in duplicates and equivalent(field,actual,expected)
  evidence=item.get('evidence',[]);loc=[]
  for citation in evidence if isinstance(evidence,list) else []:
   if not isinstance(citation,str):continue
   for folder in [case/'sources']+([case/'revision'] if stage=='revision' else []):
    for source in folder.iterdir():
     if source.name not in citation:continue
     if source.suffix=='.pdf':
      pages=re.findall(r'(?:page|p\.?)[ :]*(\d+)',citation,re.I)
      for page in pages:
       if 1<=int(page)<=len(PdfReader(source).pages):loc.append(citation)
     elif source.suffix=='.xlsx':
      book=openpyxl.load_workbook(source,read_only=True,data_only=False)
      addresses=re.findall(r'\b[A-Z]{1,3}\d+\b',citation)
      if any(sheet[cell].value is not None for sheet in book for cell in addresses):loc.append(citation)
      book.close()
  rows.append({'field':field,'expected':expected,'actual':actual,'passed':passed,'citation_location_present':bool(loc),'citation_support':'independent-review-pending','critical':field in key['critical_fields']})
 groups={}
 for group in ['ingestion','financial','judgment']:
  selected=[r for r in rows if ('judgment' if r['field'].startswith('risk_') else 'financial' if r['field'].startswith('uw_') or r['field'] in {'gross_potential_rent','sizing_rate','cap_rate','capitalization_value','ltv_limit','dscr_limit','debt_yield_limit','maximum_loan','net_cash_out'} else 'ingestion')==group]
  groups[group]={'passed':sum(r['passed'] for r in selected),'total':len(selected)}
 risks=[r for r in rows if r['field'].startswith('risk_')];tp=sum(r['expected']=='present' and r['actual']=='present' for r in risks);fp=sum(r['expected']=='absent' and r['actual']=='present' for r in risks);fn=sum(r['expected']=='present' and r['actual']!='present' for r in risks)
 return {'stage':stage,'checks':rows,'scores':groups,'critical_errors':sum(r['critical'] and not r['passed'] for r in rows),'duplicate_fields':sorted(duplicates),'risk_counts':{'true_positives':tp,'false_positives':fp,'false_negatives':fn},'professional_acceptance':None,'professional_review_status':'pending','analyst_minutes':None}
