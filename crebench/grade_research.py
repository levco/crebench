"""Public research grader. Input facts, evidence and coverage remain separate."""
import json
import math
from pathlib import Path
import re


def equal(actual, expected):
    if expected is None:
        return actual is None or (isinstance(actual,str) and actual.strip().lower() in {'unknown','not reported','not published','not provided','unavailable','n/a','null'})
    if type(expected) in (int,float):
        if isinstance(actual,str):
            a=actual.strip().replace(',','').removeprefix('$')
            if re.fullmatch(r'-?\d+(?:\.\d+)?',a):actual=float(a)
        return type(actual) in (int,float) and math.isfinite(actual) and abs(actual-expected)<=max(.01,abs(expected)*.00001)
    return isinstance(actual,str) and actual.strip().casefold()==str(expected).strip().casefold()


def grade(key, answer):
    candidates=key['candidates'];shortlist=answer.get('shortlist',[]);decisions=answer.get('candidate_decisions',[])
    if not isinstance(shortlist,list) or not isinstance(decisions,list):raise ValueError('Expected shortlist and candidate_decisions arrays')
    selected=[];seen=set();eligible=verified=0;critical=[];field_pass=field_total=evidence_pass=0
    order_scores=[];ranked=key['ordered_unique_ids']
    best_order={candidates[rid]['entity_id']:candidates[rid]['order'] for rid in reversed(ranked)}
    for position,item in enumerate(shortlist,1):
        if not isinstance(item,dict):
            critical.append({'position':position,'type':'invalid_shortlist_row'});continue
        rid=item.get('record_id');ref=candidates.get(rid)
        if ref is None:
            critical.append({'position':position,'record_id':rid,'type':'unrecognized_record'});selected.append(dict(record_id=rid,verified=False,error='Unknown record'));continue
        duplicate=ref['entity_id'] in seen;seen.add(ref['entity_id'])
        in_limit=position<=key['requested_count']
        eligible_row=ref['eligible'] and not duplicate and in_limit
        actual=item.get('facts') if isinstance(item.get('facts'),dict) else {}
        checks=[dict(field=name,actual=actual.get(name),expected=value,passed=name in actual and equal(actual[name],value)) for name,value in ref['facts'].items()]
        field_total+=len(checks);field_pass+=sum(c['passed'] for c in checks)
        sources=item.get('source_ids',[]);sources=sources if isinstance(sources,list) else []
        required=set(ref['required_sources']);reported=set(str(s) for s in sources)
        # No credit for a citation dump: only base/update records of this result or its evidenced parent are allowed.
        allowed=set(required)
        for other in candidates.values():
            if other['entity_id']==ref['entity_id']:allowed.update(other['required_sources'])
        base_required={s for s in required if s.startswith('S-')}
        updates_required=required-base_required
        base_supported=bool(reported & {s for s in allowed if s.startswith('S-')}) if len(base_required)==1 else base_required<=reported
        evidence=base_supported and updates_required<=reported and reported<=allowed
        evidence_pass+=int(evidence)
        good=eligible_row and all(c['passed'] for c in checks) and evidence
        eligible+=int(eligible_row);verified+=int(good)
        if not ref['eligible']:critical.append(dict(record_id=rid,type='ineligible_selection',reasons=ref['reasons']))
        if duplicate:critical.append(dict(record_id=rid,type='duplicate_entity'))
        for check in checks:
            if check['passed']:continue
            ex=check['expected'];ac=check['actual']
            material=ex is None and ac is not None
            if type(ex) in (int,float):
                try:material=abs(float(str(ac).replace(',','').replace('$',''))-ex)>max(.01,abs(ex)*.01)
                except (ValueError,TypeError):material=ac is not None
            elif ex is not None:material=ac is not None
            if material:critical.append(dict(record_id=rid,type='material_field_error',field=check['field'],actual=ac,expected=ex))
        selected.append(dict(record_id=rid,eligible=eligible_row,duplicate=duplicate,verified=good,
                             field_checks=checks,evidence_passed=evidence,required_sources=sorted(required),reported_sources=sources))
        if eligible_row:order_scores.append(best_order[ref['entity_id']])
    by_id={};duplicate_decisions=set()
    for item in decisions:
        if isinstance(item,dict) and item.get('record_id') in candidates:
            rid=item['record_id']
            if rid in by_id:duplicate_decisions.add(rid)
            by_id[rid]=item
    decision_checks=[]
    for rid,ref in candidates.items():
        item=by_id.get(rid,{});actual=item.get('eligible')
        if isinstance(actual,str) and actual.lower() in ('true','false'):actual=actual.lower()=='true'
        decision_checks.append(dict(record_id=rid,actual=actual,expected=ref['eligible'],
                                    passed=rid not in duplicate_decisions and type(actual) is bool and actual==ref['eligible'],
                                    reasons=ref['reasons']))
    positives=[d for d in decision_checks if d['expected']];negatives=[d for d in decision_checks if not d['expected']]
    pair_total=len(order_scores)*(len(order_scores)-1)//2
    pair_pass=sum(order_scores[i]<=order_scores[j] for i in range(len(order_scores)) for j in range(i+1,len(order_scores)))
    target=key['target_count']
    return dict(case_id=key['case_id'],task=key['task'],target_count=target,available_unique=key['available_unique'],
                returned_count=len(shortlist),eligible_count=eligible,verified_count=verified,
                eligible_yield=eligible/target if target else None,verified_yield=verified/target if target else None,
                selection_precision=eligible/len(shortlist) if shortlist else None,
                correct_abstention=len(shortlist)==0 if target==0 else None,
                field_accuracy=dict(passed=field_pass,total=field_total),evidence_accuracy=dict(passed=evidence_pass,total=len(shortlist)),
                candidate_accuracy=dict(passed=sum(d['passed'] for d in decision_checks),total=len(candidates)),
                eligible_recall=dict(passed=sum(d['passed'] for d in positives),total=len(positives)),
                ineligible_rejection=dict(passed=sum(d['passed'] for d in negatives),total=len(negatives)),
                ranking_pair_agreement=dict(passed=pair_pass,total=pair_total),
                material_errors=critical,selected_checks=selected,decision_checks=decision_checks,
                limits=['Classification and shortlist assessment of supplied fictional extracts; not real-world discovery accuracy',
                        'Evidence checks match source IDs and controlling updates; prose rationale requires separate review'])


if __name__=='__main__':
    import sys
    key=json.loads(Path(sys.argv[1]).read_text());answer=json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(grade(key,answer),indent=2,allow_nan=False))
