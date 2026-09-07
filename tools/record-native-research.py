"""Import original native outputs; retain raw traces privately and publish minimal audits.

The trace reader intentionally accepts only the scalar subset actually needed
from the connector's TOON response. It does not interpret arbitrary nested data.
"""
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from crebench.run_research import normalize_answer, validate_answer
from crebench.grade_research import grade

EXP = ROOT / 'experiments/2026-09-07-research-v1'
PRIVATE = ROOT / 'work/research-v1/native'

def scalar(text):
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return text

def fields(text, spaces):
    result = {}
    for line in text.splitlines():
        match = re.match(r'^' + ' ' * spaces + r'("[^"\n]+"|[\w]+): (.*)$', line)
        if match:
            result[scalar(match[1])] = scalar(match[2])
    return result

def trace_audit(text, packet):
    root = fields(text, 4)
    root['aiSessionId'] = scalar(re.search(r'^  - aiSessionId: (.*)$', text, re.M)[1])
    count = re.search(r'^    events\[(\d+)\]:$', text, re.M)
    parts = re.split(r'^      - createdAt: ', text, flags=re.M)[1:]
    if not count or int(count[1]) != len(parts):
        raise ValueError('Trace event count does not match parsed event boundaries')
    events = []
    for part in parts:
        e = fields(part, 8)
        p = fields(part, 10)
        events.append((e, p))
    generations = [(e, p) for e, p in events if e.get('event') in ('$ai_generation', '$ai_embedding') and not str(p.get('$ai_span_name', '')).startswith('run_summary:')]
    costs = [p.get('$ai_total_cost_usd') for _, p in generations]
    tool_names = {str(p.get('$ai_span_name'))[5:] for _, p in events if str(p.get('$ai_span_name', '')).startswith('tool:')}
    for _, p in generations:
        tool_names.update(str(p.get('$ai_tools_called', '')).split(','))
    for names in re.findall(r'^          "\$ai_tools_called"\[\d+\]: (.*)$', text, re.M):
        tool_names.update(names.split(','))
    tools = sorted(t.strip() for t in tool_names if t.strip())
    # These observed delivery/expertise tools do not establish full execution
    # coverage. File-creation internals are absent from the available metadata.
    unexpected = sorted(set(tools) - {'get_generated_file', 'get_expertise_instructions'})
    trace_input = str(root.get('inputState', ''))
    visible = re.sub(r'\s+', ' ', trace_input).strip()
    expected = re.sub(r'\s+', ' ', packet).strip()
    matched = visible == expected
    truncated = '…[truncated' in trace_input or '… [truncated' in trace_input
    prefix = re.split(r'…\s*\[truncated', visible)[0]
    prefix_matched = truncated and len(prefix) > 5000 and expected.startswith(prefix)
    if not (matched or prefix_matched):
        raise ValueError('Trace input is not the frozen case packet')
    total = sum(costs) if costs and all(type(c) in (int, float) for c in costs) else None
    if total is not None and abs(total - root.get('totalCost', total)) > .000001:
        raise ValueError('Generation sum does not match trace total')
    audit = dict(trace_id=root['id'], session_id=root['aiSessionId'], started_at=root['createdAt'],
        packet_match='Whitespace-equivalent complete root input' if matched else 'Trace prefix matches; connector truncates root input. Complete UI input was independently verified before submission.', event_count=len(events),
        model_calls=len(generations), generation_costs_usd=costs, total_cost_usd=total,
        cost_sources=sorted({p.get('$ai_cost_model_source', 'unknown') for _, p in generations}),
        models=sorted({p.get('$ai_model', 'unknown') for _, p in generations}),
        agent_versions=sorted({str(p.get('agent_version', 'unknown')) for _, p in events}),
        tools_called=tools, external_retrieval_audit='no_retrieval_observed_partial_coverage' if not unexpected else 'needs_review',
        execution_coverage='Recorded backend tools only; internal file-creation execution is not visible in the available trace metadata.',
        confirmed_common_corpus=False,
        tools_requiring_review=unexpected, elapsed_seconds=root.get('totalLatency'),
        cost_scope='Matched workflow generations and embeddings; duplicate run-summary excluded. Session naming, hosting, subscriptions, operator time and product credits excluded.',
        cost_basis='PostHog model-rate estimate; not a billed Lev customer price')
    return audit, root.get('outputState')

def record(case):
    private = PRIVATE / case
    target = EXP / 'lev_native/lev--native' / case
    target.mkdir(parents=True, exist_ok=True)
    packet = (ROOT / 'benchmarks/research-v1/cases' / case / 'packet.md').read_text()
    submission = json.loads((private / 'submission.json').read_text())
    blocks = json.loads((private / 'code-blocks.json').read_text())
    answers = []
    for block in blocks:
        try:
            answer = normalize_answer(block)
            validate_answer(answer)
            answers.append(answer)
        except ValueError:
            pass
    if len(answers) != 1:
        raise ValueError(f'{case}: {len(answers)} unambiguous original answers')
    answer = answers[0]
    (target / 'original-code-blocks.json').write_text(json.dumps(blocks, indent=2) + '\n')
    (target / 'answer.json').write_text(json.dumps(answer, indent=2) + '\n')
    audit = None
    if (private / 'trace.private.toon').exists():
        audit, original = trace_audit((private / 'trace.private.toon').read_text(), packet)
        (target / 'trace-audit.json').write_text(json.dumps(audit, indent=2) + '\n')
        # The root output may be truncated or contain signed file URLs. Complete
        # visible JSON blocks are the public original; retain root output privately.
        (private / 'trace-output.private.txt').write_text(str(original) + '\n')
        (target / 'original-response.md').unlink(missing_ok=True)
    urls = []
    if (private / 'trace.private.toon').exists():
        for part in re.split(r'^      - createdAt: ', (private / 'trace.private.toon').read_text(), flags=re.M)[1:]:
            if fields(part, 10).get('$ai_span_name') == 'tool:get_generated_file':
                generated = fields(part, 12).get('result')
                if isinstance(generated, str):
                    try:
                        files = json.loads(generated)
                        for file in files:
                            if isinstance(file, dict) and file.get('download_url'):
                                urls.append(file['download_url'])
                    except (ValueError, TypeError):
                        pass
    if (private / 'artifact-frame.private.json').exists():
        frames = json.loads((private / 'artifact-frame.private.json').read_text())
        for frame in frames:
            if frame['name'] != 'doc-drawer-viewer':
                continue
            urls.append(urllib.parse.parse_qs(urllib.parse.urlsplit(frame['src']).query)['src'][0])
    if (private / 'artifact-url.private.json').exists():
        urls.append(json.loads((private / 'artifact-url.private.json').read_text())['url'])
    for url in dict.fromkeys(urls):
            name = Path(urllib.parse.unquote(urllib.parse.urlsplit(url).path)).name
            if Path(name).suffix.lower() not in ('.xlsx', '.csv'):
                raise ValueError('Unexpected artifact type')
            out = target / 'artifacts' / name
            out.parent.mkdir(exist_ok=True)
            if not out.exists():
                out.write_bytes(urllib.request.urlopen(url, timeout=90).read())
    artifacts = [dict(path=str(p.relative_to(target)), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)
                 for p in sorted((target / 'artifacts').glob('*')) if p.is_file()]
    result = dict(case_id=case, system='lev/native', track='lev_native', status='completed',
        started_at=submission['started_at'], observed_completed_at=json.loads((private / 'completed-time.json').read_text())['observed_completed_at'],
        packet_sha256=submission['packet_sha256'], ui_whitespace_equivalent=submission['ui_whitespace_equivalent'],
        operator_semantic_corrections=0, artifacts=artifacts, cost_usd=None,
        estimated_inference_cost_usd=audit['total_cost_usd'] if audit else None,
        cost_basis=audit['cost_basis'] if audit else 'Not yet attributable',
        elapsed_seconds=audit['elapsed_seconds'] if audit else None,
        returned_models=audit['models'] if audit else [], trace_audit=audit,
        access_audit=audit['external_retrieval_audit'] if audit else 'unverified')
    (target / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    key = json.loads((ROOT / 'benchmarks/research-v1/cases' / case / 'answer-key.json').read_text())
    g = grade(key, answer)
    (target / 'grade.json').write_text(json.dumps(g, indent=2) + '\n')
    return dict(case=case, verified=g['verified_count'], target=g['target_count'], decisions=g['candidate_accuracy'],
                errors=len(g['material_errors']), files=len(artifacts), cost=result['estimated_inference_cost_usd'])

if __name__ == '__main__':
    for case in sys.argv[1:] or sorted(p.name for p in PRIVATE.iterdir() if (p / 'code-blocks.json').exists()):
        print(json.dumps(record(case)))
