"""Reconcile expansion inference without treating purchases as consumption."""
import datetime
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/2026-09-07-cre-work-v2'
DATA = json.loads((OUT / 'results.json').read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def attempts(directory, public=True):
    assert directory.is_dir(), f'Required source records unavailable: {directory}. Inspect the published ledger; do not replace missing costs with zero.'
    records = []
    for started in sorted(directory.glob('**/turn-*/attempt-*/started.json')):
        result_path = started.with_name('result.json')
        assert result_path.exists(), f'Inference still in flight: {started}'
        before = json.loads(started.read_text())
        result = json.loads(result_path.read_text())
        cost = (result.get('usage') or {}).get('cost')
        known = type(cost) in (int, float) and math.isfinite(cost) and cost >= 0
        refused = result.get('http_status') in (401, 402) and not result.get('usage')
        records.append({
            'started_at': before['at'],
            'http_status': result.get('http_status'),
            'reported_cost_usd': cost if known else None,
            'retained_reservation_usd': cost if known else 0 if refused else before['request_reservation_usd'],
            'refused_before_inference': refused,
            'source_sha256': digest(result_path),
            'source_path': str(result_path.relative_to(ROOT)) if public else None,
        })
    return {
        'attempts': len(records),
        'reported_usage_usd': sum(r['reported_cost_usd'] or 0 for r in records),
        'conservatively_accounted_usd': sum(r['retained_reservation_usd'] for r in records),
        'refused_requests': sum(r['refused_before_inference'] for r in records),
        'unknown_nonrefused_requests': sum(r['reported_cost_usd'] is None and not r['refused_before_inference'] for r in records),
        'records': records,
    }


api = {
    'workflow': attempts(OUT / 'credential-resumption'),
    'original_auth_rejections': attempts(OUT / 'api'),
    'discovery': attempts(ROOT / 'work/cre-work-v2/discovery', public=False),
    'lender': attempts(ROOT / 'experiments/2026-09-07-lender-qualification-v1/runs'),
}
native = []
for row in DATA['rows']:
    if row['model'] == 'lev/native':
        native.append({'task': f"{row['case_id']}/{row['stage']}", 'estimate_usd': row['cost_usd'], 'run_path': row['run_path']})
for track in ('lender_rows', 'discovery_rows'):
    for row in DATA[track]:
        if row['model'] == 'lev/native':
            native.append({'task': track + '/' + row['case_id'], 'estimate_usd': row['estimated_inference_cost_usd'], 'run_path': row['run_path']})
assert len({r['task'] for r in native}) == len(native) == 22
assert all(type(r['estimate_usd']) in (int, float) for r in native)
native_total = sum(r['estimate_usd'] for r in native)
for key, limit in [('workflow', 37), ('discovery', 26), ('lender', 2)]:
    assert api[key]['conservatively_accounted_usd'] <= limit + 1e-8
assert native_total <= 25
observed = sum(v['reported_usage_usd'] for v in api.values()) + native_total
data = {
    'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'project_inference_limit_usd': 200,
    'allocation': DATA['budget'],
    'purchase': {'gateway_credits_usd': 100, 'processing_fee_usd': 3.20, 'tax_usd': 9.16, 'total_charged_usd': 112.36, 'auto_reload': False, 'purpose': 'Funding only; does not raise the cumulative inference limit.'},
    'api': api,
    'native_matched_main_trace_estimate_usd': native_total,
    'native_records': native,
    'expansion_reported_api_plus_native_estimate_usd': observed,
    'limitations': [
        'The prior-project $110 is a reservation, not a claim of exact historical consumption.',
        'HTTP 401 and 402 refused requests retain their evidence; their inference reservations were administratively released.',
        'Unknown transport outcomes retain the full request reservation. Missing usage is not assigned zero cost.',
        'Native main-trace estimates exclude incompletely attributed titling, setup and indexing; native allocation retains headroom.',
        'Consumer inference, search/data services, subscriptions and human labor are not fully measured. This is not an all-in cost.',
        'Private live-research request records are represented by hashes and accounting facts; retrieved third-party article bodies are not republished.',
    ],
}
(OUT / 'cost-ledger.json').write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
print(json.dumps({'expansion_reported_api_plus_native_estimate_usd': observed, 'native_main_traces_usd': native_total, 'project_inference_limit_usd': 200}))
