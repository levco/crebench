"""Deterministic field scoring; presentation normalization never fixes answers.

Evidence truth, artifact usability and claim review are separate auditable review
records. Citation-shaped text is not automatically treated as supported evidence.
"""
import argparse
import json
import math
from pathlib import Path
import re

RATES={'contract_rate','sizing_rate','annual_debt_constant','sizing_dscr','sizing_debt_yield'}
COUNTS={'space_count','occupied_count','total_area_sf','occupied_area_sf'}
PCTS={'occupancy_count_pct','occupancy_area_pct'}
UNKNOWN={'unknown','not provided','not evidenced','not supplied','not verified','unavailable','null','none'}


def number(value,field):
    if type(value) in (int,float):return value if math.isfinite(value) else None
    if not isinstance(value,str):return None
    text=value.strip();negative=text.startswith('(') and text.endswith(')')
    text=text.strip('()').replace('$','').replace(',','').strip()
    percent=text.endswith('%');text=text.removesuffix('%').removesuffix('x').strip()
    if not re.fullmatch(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)',text):return None
    result=float(text)*(-1 if negative else 1)
    if percent and field in RATES:result/=100
    return result


def equivalent(field,value,expected):
    if expected is None:return value is None or (isinstance(value,str) and value.strip().lower() in UNKNOWN)
    if isinstance(expected,(int,float)):
        actual=number(value,field)
        tolerance=0 if field in COUNTS else .01 if field in PCTS else .0001 if field in RATES else max(1,abs(expected)*.0001)
        return actual is not None and abs(actual-expected)<=tolerance
    if not isinstance(value,str):return False
    if field=='binding_constraint':
        normalize=lambda s:re.sub(r'[^a-z]','',s.lower()).replace('debtyield','dy').replace('loantovalue','ltv').replace('debtservicecoverageratio','dscr')
        return normalize(value)==normalize(expected)
    if field=='renewal_option_exercised':return value.strip().lower() in {'not evidenced','unknown','not provided','no exercise notice provided','exercise not evidenced','no / not evidenced'}
    return value.strip()==expected


def grade(case,answer):
    key=json.loads((Path(case)/'answer-key.json').read_text())
    values=answer.get('fields',[])
    if isinstance(values,dict):values=[{'id':k,**(v if isinstance(v,dict) else {'value':v})} for k,v in values.items()]
    if not isinstance(values,list):raise ValueError('Fields need a list or mapping; unparseable content requires attributed transcription')
    parsed={};duplicates=[]
    for v in values:
        if not isinstance(v,dict) or 'id' not in v:continue
        if v['id'] in parsed:duplicates.append(v['id'])
        else:parsed[v['id']]=v
    checks=[]
    for group,names in [('extraction',key['extraction_fields']),('financial',key['financial_fields'])]:
        for field in names:
            expected=key['fields'][field];entry=parsed.get(field);present=entry is not None and 'value' in entry and field not in duplicates
            value=entry.get('value') if entry else None
            passed=present and equivalent(field,value,expected)
            material=False;deviation=None
            if field in key['critical_fields'] and not passed:
                if isinstance(expected,(int,float)) and number(value,field) is not None:
                    deviation=number(value,field)-expected
                    material=abs(deviation)>(1 if field in PCTS else abs(expected)*.01)
                else:material=True
            checks.append({'field':field,'group':group,'present':present,'actual':value,'expected':expected,'passed':passed,
                'critical_error':material,'deviation':deviation,'evidence':entry.get('evidence',[]) if entry else [],
                'calculation':entry.get('calculation','') if entry else '',
                'evidence_support_status':'pending_source_review','transcription_excerpt':entry.get('transcription_excerpt') if entry else None})
    groups={g:{'passed':sum(c['passed'] for c in checks if c['group']==g),'total':sum(c['group']==g for c in checks)} for g in ['extraction','financial']}
    for g in groups.values():g['percent']=100*g['passed']/g['total'] if g['total'] else None
    return {'case_id':key['case_id'],'checks':checks,'groups':groups,'critical_errors':sum(c['critical_error'] for c in checks),
            'missing_fields':[c['field'] for c in checks if not c['present']],'duplicate_fields':duplicates,
            'evidence_score':None,'evidence_status':'Requires source-supported review, not regex citation credit',
            'qualifications':answer.get('qualifications',[]),'blocked':answer.get('blocked',[])}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case');p.add_argument('answer');p.add_argument('--output');a=p.parse_args()
    result=grade(a.case,json.loads(Path(a.answer).read_text()));text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if a.output:Path(a.output).write_text(text)
    print(json.dumps({k:result[k] for k in ['case_id','groups','critical_errors','missing_fields']}))
