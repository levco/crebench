"""Apply the frozen workbook checks to every completed recorded delivery."""
import concurrent.futures,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('artifact_audit',ROOT/'tools/verify-workflow-artifact.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
exp=Path(sys.argv[1]).resolve();node=sys.argv[2] if len(sys.argv)>2 else 'node';jobs=[]
for result_path in exp.glob('*/*/*/result.json'):
    r=json.loads(result_path.read_text());run=result_path.parent
    if not r.get('latest_workbook'):continue
    workbook=run/r['latest_workbook'];sha=hashlib.sha256(workbook.read_bytes()).hexdigest()
    audit_path=run/'audit/artifact-audit.json'
    if audit_path.exists():
        old=json.loads(audit_path.read_text())
        if old['source_workbook']==workbook.name and old.get('source_workbook_sha256',sha)==sha:
            if 'source_workbook_sha256' not in old:
                old['source_workbook_sha256']=sha;audit_path.write_text(json.dumps(old,indent=2)+'\n')
            continue
        (run/'audit').rename(run/('audit-superseded-'+old['source_workbook'].replace('.xlsx','')))
    mapping=run/'location-map.json' if (run/'location-map.json').exists() else workbook.with_suffix('.json')
    if not mapping.exists():print('Mapping pending:',run.name,flush=True);continue
    jobs.append((ROOT/'benchmarks/workflow-v1/cases'/r['case_id'],workbook,mapping,run/'audit',node))
def audit(job):
    result=module.verify(*job);result['source_workbook_sha256']=hashlib.sha256(job[1].read_bytes()).hexdigest();(job[3]/'artifact-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'workbook':str(job[1].relative_to(exp)),'checks':[(c['rubric_check'],c['passed']) for c in result['checks']]}),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(audit,jobs))
