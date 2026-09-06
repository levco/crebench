"""Verify retained experiment evidence and generate a public, non-ranking report."""
import collections
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crebench.grade import grade, read_json, sha256


def summarize(directory):
    directory = Path(directory)
    plan = read_json(directory/'plan.json')
    case = Path('cases/public')/plan['case_id']
    if sha256(case/'manifest.json') != plan['case_manifest_sha256']:
        raise ValueError('Case manifest changed')
    if sha256(Path('crebench/grade.py')) != plan['grader_sha256']:
        raise ValueError('Use the frozen grader revision to reproduce this experiment')
    models = []
    for index, model in enumerate(plan['models'], 1):
        runs = []
        for repetition in range(1, plan['repetitions']+1):
            run = directory/f'r{repetition}-{index}'
            if not (run/'result.json').exists():
                runs.append({'run': run.name, 'status': 'interrupted' if (run/'started.json').exists() else 'not_run'})
                continue
            result = read_json(run/'result.json')
            for name, expected in result['sha256'].items():
                if sha256(run/name) != expected:
                    raise ValueError(f'Changed run artifact: {run/name}')
            row = {'run': run.name, 'status': result['status'], 'elapsed_seconds': result['elapsed_seconds'],
                   'returned_model': result.get('returned_model'), 'usage': result.get('usage'),
                   'http_status': result.get('http_status'), 'groups': {}, 'failed_checks': [],
                   'complete_success': False}
            if result['grade']:
                actual = grade(case, read_json(run/'answer.txt'))
                if actual['criteria'] != result['grade']['criteria']:
                    raise ValueError(f'Grade mismatch: {run}')
                groups = collections.defaultdict(lambda: {'passed': 0, 'total': 0})
                for criterion in actual['criteria']:
                    groups[criterion['kind']]['total'] += 1
                    groups[criterion['kind']]['passed'] += int(criterion['pass'])
                row.update(groups=dict(groups), passed=actual['passed'], total=actual['total'],
                           material_errors=actual['material_errors'],
                           failed_checks=[c['criterion'] for c in actual['criteria'] if not c['pass']],
                           complete_success=result['status']=='scored' and actual['all_checks_pass'])
            runs.append(row)
        models.append({'model': model, 'planned_runs': plan['repetitions'],
                       'complete_successes': sum(r.get('complete_success',False) for r in runs), 'runs': runs})
    return {'experiment': directory.name, 'track': plan['track'], 'leaderboard_eligible': False,
            'unique_cases': 1, 'case_id': plan['case_id'], 'models': models,
            'limitations': plan['limitations'], 'plan_sha256': sha256(directory/'plan.json')}


if __name__ == '__main__':
    target = Path(sys.argv[1])
    data = summarize(target)
    # This is a derived report; immutable raw records remain the source of truth.
    (target/'summary.json').write_text(json.dumps(data,indent=2)+'\n')
    rows = ['# Financial pilot results', '', '> Historical strict-parser report. See [corrected financial scoring](FINANCIAL-RESULTS.md); all nine retained answers are now scorable. Original execution records below are preserved.', '',
            'Real API attempts on one public synthetic case. These are development findings, not a leaderboard.', '',
            '| Requested model | Run | Status | Checks passed | Complete success | Seconds |',
            '|---|---|---|---|---|---|']
    for model in data['models']:
        for run in model['runs']:
            score = f"{run['passed']}/{run['total']}" if 'passed' in run else '—'
            rows.append(f"| {model['model']} | {run['run']} | {run['status']} | {score} | {run.get('complete_success',False)} | {run.get('elapsed_seconds','—')} |")
    rows += ['', '## Interpretation', '',
             'A single case and repeated calls do not establish accuracy on real CRE work. The 58 checks include 27 field-value checks, 27 prescribed-reference checks, one exact discrepancy-set check, two consistency checks and one format check. References are supplied in the contract, so reference compliance is not independent evidence retrieval.', '',
             'All nine accessible-model attempts returned HTTP 200 but failed strict JSON parsing. Financial correctness was not scored; zero complete submissions must not be read as zero financial accuracy. This finding motivates separate format-compliance and semantic-correctness reporting in the next protocol version. The original grades remain unchanged.', '',
             'No answer repairs or favorable-run selection. HTTP errors and unattempted calls are infrastructure outcomes, not financial mistakes. A truncated or invalid response is not complete success even when some values are correct.', '',
             'Cost and token usage are preserved as returned by the gateway. No inference cost is invented when absent. Latency includes the gateway and network, and is not pure model generation time.', '',
             '## Limits', '']
    rows += ['- '+x for x in data['limitations']]
    (target/'RESULTS.md').write_text('\n'.join(rows)+'\n')
    print(json.dumps({'experiment':data['experiment'], 'models':[{'model':m['model'],'complete_successes':m['complete_successes']} for m in data['models']]}))
