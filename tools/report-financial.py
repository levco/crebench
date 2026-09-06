"""Rescore all retained answers consistently, preserving original run records."""
import datetime
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from crebench.grade import read_json,sha256,verify_case
from crebench.normalize import score_text


def report(root):
    root=Path(root);case=Path('cases/public/harbor-court-001');verify_case(case)
    plan=read_json(root/'plan.json')
    if sha256(case/'manifest.json') != plan['case_manifest_sha256']:raise ValueError('Case drift')
    rows=[]
    for run in sorted(root.glob('r*')):
        if not run.is_dir():continue
        if not (run/'result.json').exists():raise ValueError('Unfinished run: '+run.name)
        original=read_json(run/'result.json')
        for path,digest in original['sha256'].items():
            if sha256(run/path)!=digest:raise ValueError('Run artifact drift: '+str(run/path))
        answer=run/original.get('answer_path','answer.txt')
        row={'run':run.name,'model':original['requested_model'],'original_status':original['status'],
             'elapsed_seconds':original['elapsed_seconds'],'usage':original.get('usage'),
             'result_sha256':sha256(run/'result.json'),'status':'no_answer','score':None}
        if answer.exists():
            row['answer_sha256']=sha256(answer)
            try: row.update(status='scored',score=score_text(case,answer.read_text()))
            except ValueError as e:row.update(status='needs_review',error=str(e))
        rows.append(row)
    data={'experiment':root.name,'scorer_version':'presentation-tolerant-v2.1',
          'scoring_correction':'Supplemental development correction applied to every retained answer; original records unchanged',
          'scorer_sha256':{p:sha256(p) for p in ['crebench/normalize.py','crebench/grade.py']},
          'plan_sha256':sha256(root/'plan.json'),'unique_cases':1,'leaderboard_eligible':False,'runs':rows}
    (root/'financial-v2.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    lines=['# Financial pilot: corrected scoring','','One public fictional case. Every retained response is included. Formatting is diagnostic; financial and source-reference checks are separate.','','| Model | Run | Financial checks | Reference checks | Seconds |','|---|---|---|---|---|']
    for r in rows:
        def count(kind):
            g=r['score']['groups'][kind] if r['score'] else None
            return f"{g['passed']}/{g['total']}" if g else 'Unscored'
        lines.append(f"| {r['model']} | {r['run']} | {count('financial')} | {count('references')} | {r['elapsed_seconds']} |")
    lines+=['','## Financial failures','']
    for r in rows:
        failed=r['score']['groups']['financial']['failed'] if r['score'] else [r['status']]
        lines.append(f"- {r['run']} ({r['model']}): {', '.join(failed) or 'None'}")
    lines+=['','## Interpretation','','The 30 financial checks are 27 values, one exact conflict-set check and two consistency checks. They are correlated checks on one case, not 30 independent transactions. The 27 reference checks measure the supplied canonical references, not evidence discovery. No statistical ranking is supported by three repetitions on one case.','','All raw responses and original execution outcomes remain unchanged. The supplemental scorer removes presentation wrappers and recognizes equivalent constraint labels. It never computes missing answers or replaces incorrect numbers. The scoring correction was developed after inspecting earlier responses and applies to all runs; it was not preregistered before their generation.','','See [the correction policy](../../docs/scoring-correction-2026-09-06.md) and [the machine-readable report](financial-v2.json) for normalization logs, exact failed checks and hashes.']
    (root/'FINANCIAL-RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'experiment':root.name,'runs':[{'run':r['run'],'model':r['model'],'financial':r['score']['groups']['financial'] if r['score'] else None} for r in rows]}))

if __name__=='__main__':report(sys.argv[1])
