"""Collect recorded outcomes; never fill missing answers or select better retries."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from crebench.grade_workflow import grade
from crebench.normalize_workflow import normalize
from crebench.run_workflow import digest
p=argparse.ArgumentParser();p.add_argument('experiment');a=p.parse_args();exp=Path(a.experiment).resolve();plan=json.loads((exp/'plan.json').read_text());rows=[]
for track in ['agent','direct','lev_native']:
    systems=plan['models'] if track!='lev_native' else ['lev/native']
    for model in systems:
        for case in plan['cases']:
            run=exp/track/model.replace('/','--')/case
            if not (run/'result.json').exists():
                rows.append({'case_id':case,'system':model,'track':track,'status':'pending'});continue
            result=json.loads((run/'result.json').read_text());answer_path=run/'analysis.json'
            if not answer_path.exists():answer_path=run/'analysis.transcribed.json'
            answer=json.loads(answer_path.read_text()) if answer_path.exists() else {'fields':[]}
            original=grade(ROOT/'benchmarks/workflow-v1/cases'/case,answer)
            (run/'field-score-original.json').write_text(json.dumps(original,indent=2)+'\n')
            normalized,changes=normalize(answer)
            (run/'display-normalization.json').write_text(json.dumps({'changes':changes,'policy':'docs/workflow-display-normalization-2026-09-06.md'},indent=2)+'\n')
            scored=grade(ROOT/'benchmarks/workflow-v1/cases'/case,normalized)
            (run/'field-score-normalized-strict.json').write_text(json.dumps(scored,indent=2)+'\n')
            excluded=[c for c in scored['checks'] if c['field']=='verified_renewal_insurance']
            scored['diagnostic_exclusions']={'policy':'docs/workflow-insurance-criterion-2026-09-06.md','checks':excluded}
            scored['checks']=[c for c in scored['checks'] if c['field']!='verified_renewal_insurance']
            for group in ['extraction','financial']:
                checks=[c for c in scored['checks'] if c['group']==group];passed=sum(c['passed'] for c in checks)
                scored['groups'][group]={'passed':passed,'total':len(checks),'percent':100*passed/len(checks)}
            scored['critical_errors']=sum(c['critical_error'] for c in scored['checks'])
            (run/'field-score.json').write_text(json.dumps(scored,indent=2)+'\n')
            audit_path=run/'audit/artifact-audit.json';review_path=run/'review.json'
            audit=json.loads(audit_path.read_text()) if audit_path.exists() else None
            review=json.loads(review_path.read_text()) if review_path.exists() else None
            evidence=review.get('evidence',[]) if review else []
            evidence_score={'passed':sum(c['passed'] for c in evidence),'total':17,'percent':100*sum(c['passed'] for c in evidence)/17} if len(evidence)==17 else None
            usages=[x['usage'] for x in result.get('attempts',[]) if isinstance(x.get('usage'),dict)]
            usage_summary={k:sum(u.get(k,0) or 0 for u in usages) for k in ['prompt_tokens','completion_tokens','total_tokens']} if usages else None
            if usage_summary:usage_summary.update(reported_attempts=len(usages),all_attempts=len(result['attempts']),scope='Reported model usage only; rejected-attempt usage unavailable')
            artifacts=[]
            for key,kind in [('latest_workbook','xlsx'),('latest_memo','pdf')]:
                if result.get(key) and (run/result[key]).is_file():
                    f=run/result[key];artifacts.append({'kind':kind,'path':str(f.relative_to(ROOT)),'sha256':digest(f),'bytes':f.stat().st_size})
            rows.append({'case_id':case,'system':model,'track':track,'status':result['status'],'field_scores':scored['groups'],
                'quality_status':'excluded_infrastructure' if result['status']=='infrastructure_error' else 'scored',
                'field_checks':scored['checks'],'evidence_score':evidence_score,
                'critical_errors':scored['critical_errors'],'failed_fields':[c['field'] for c in scored['checks'] if not c['passed']],
                'workbook_audit':audit,'review':review,'artifacts':artifacts,'elapsed_seconds':result.get('elapsed_seconds'),
                'cost_usd':result.get('gateway_reported_cost_usd') if track!='lev_native' else result.get('estimated_inference_cost_usd'),
                'cost_basis':result.get('cost_basis'),'cost_scope':result.get('cost_scope','Inference only; hosting, subscriptions and operator time excluded'),
                'known_partial_cost_usd':result.get('known_partial_cost_usd'),'returned_models':result.get('returned_models'),
                'model_calls':result.get('model_calls_including_retries'),'tool_calls':result.get('tool_calls'),
                'reported_usage':usage_summary,
                'operator_semantic_corrections':result.get('operator_semantic_corrections',0),'run_path':str(run.relative_to(ROOT))})
out={'version':'workflow-v1','source_commit':plan['source_commit'],'case_ids':plan['cases'],'planned_runs':30,'completed_records':sum(r['status']!='pending' for r in rows),'completed_workflows':sum(r['status']=='completed' for r in rows),'runs':rows,
    'limitations':plan['limitations'],'cost_comparison':'Gateway-reported API inference vs trace-estimated Lev workflow inference; not total product cost or customer pricing'}
(exp/'results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps({'recorded':out['completed_records'],'planned':30,'statuses':{s:sum(r['status']==s for r in rows) for s in sorted(set(r['status'] for r in rows))}}))
