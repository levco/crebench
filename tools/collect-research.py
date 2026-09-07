"""Reproduce the full planned matrix and inspect original research deliverables."""
import csv
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from crebench.grade_research import grade, equal
from crebench.research_representation_v1_1 import normalize, VERSION

EXP = ROOT / 'experiments/2026-09-07-research-v1'
CASES = ROOT / 'benchmarks/research-v1/cases'
SYSTEMS = [('lev_native', 'lev/native'), ('agent', 'openai/gpt-5'), ('agent', 'anthropic/claude-opus-5'),
           ('direct', 'openai/gpt-5'), ('direct', 'anthropic/claude-opus-5')]
NAMES = ['Lev Agent', 'GPT-5 + tools', 'Opus 5 + tools', 'GPT-5 direct', 'Opus 5 direct']

def norm(value):
    return re.sub('[^a-z0-9]', '', str(value).lower())

ALIASES = {
    'record_id': ['record', 'recordid', 'base record id'],
    'entity_id': ['entity', 'sponsor entity id', 'property entity id', 'operating parent id'],
    'event_date': ['close date', 'closing date', 'sale date', 'transaction date', 'lease execution date', 'execution date'],
    'consideration_usd': ['consideration', 'sale price usd', 'price usd'],
    'property_size': ['property size units', 'property size sf', 'units', 'size', 'size units'],
    'price_per_unit': ['price unit', 'price per sf', 'price sf', 'price per unit usd', 'price per sf usd', 'price sf usd', 'price per unit usd sf', 'price per sf usd sf', 'price per unit psf'],
    'annual_face_rent_psf': ['annual face rent psf yr', 'annual face rent psf year', 'annual face psf', 'face rent psf year', 'face rent psf yr', 'annual face rent psf psf yr'],
    'effective_net_rent_psf_year': ['effective net rent psf yr', 'effective net psf year', 'effective net psf yr', 'effective net rent psf', 'effective net rent year', 'effective net rent psf year psf yr'],
    'term_months': ['term mo', 'term in months', 'lease term months'],
    'firm_name': ['firm', 'sponsor', 'sponsor name', 'operating sponsor', 'company'],
    'transaction_size_usd': ['transaction usd', 'transaction size', 'acquisition size usd', 'transaction amount usd'],
    'contact_name': ['contact', 'name of contact', 'decision maker'],
    'contact_role': ['role', 'title', 'contact title'],
    'contact_email': ['email', 'verified email'],
    'owner_entity_id': ['owner id', 'owner entity'],
    'maturity_date': ['maturity', 'confirmed maturity', 'executed maturity date'],
    'original_principal_usd': ['original principal', 'original loan principal usd'],
    'outstanding_balance_usd': ['outstanding balance', 'current outstanding balance usd'],
    'source_ids': ['sources', 'source', 'source ids citations', 'citations', 'source references', 'citations S U IDs'],
    'eligible': ['qualifies', 'qualified', 'eligibility'],
}

def canonical(value):
    n = norm(re.sub(r'\$/\s*sf', 'psf', str(value), flags=re.I))
    for key, aliases in ALIASES.items():
        if n in {norm(key), *(norm(a) for a in aliases)}:
            return key
    return None

def read_tables(path):
    if path.suffix == '.csv':
        with path.open(encoding='utf-8-sig', newline='') as f:
            return [('CSV', list(csv.reader(f)))]
    import openpyxl
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    return [(s.title, [[v.isoformat()[:10] if isinstance(v, (datetime, date)) else v for v in row] for row in s.values]) for s in book]

def csv_null_attribution(run, file, field_checks):
    """Attribute blank cells only when the original matched tool input proves null.

    Python's scored CSV writer turns None into an empty cell. Do not attribute
    this loss of annotation to a model that supplied an explicit JSON null.
    """
    for log in sorted(run.glob('turn-*/tool-*.json')):
        call = json.loads(log.read_text())
        if call.get('name') != 'export_csv' or call.get('result', {}).get('created') != str(file.relative_to(run)):
            continue
        args = call.get('arguments', {})
        headers = [canonical(v) for v in args.get('headers', [])]
        if 'record_id' not in headers:
            continue
        index = headers.index('record_id')
        by_id = {str(row[index]): row for row in args.get('rows', []) if len(row) > index}
        for check in field_checks:
            if check['passed'] or check['expected'] is not None or check['actual'] not in (None, ''):
                continue
            row = by_id.get(check['record_id'], [])
            field = check['field']
            if field in headers and len(row) > headers.index(field) and row[headers.index(field)] is None:
                check.update(attribution='benchmark_csv_serializer',
                    attribution_detail='Model supplied explicit JSON null; the frozen CSV writer serialized it as a blank cell.',
                    tool_evidence=str(log.relative_to(ROOT)) if log.is_relative_to(ROOT) else str(log.relative_to(run)))

def audit_artifact(run, result, answer, key, case=None, records=None):
    if result['track'] == 'direct':
        return dict(applicable=False, reason='Direct API control has no artifact tools')
    required = '.xlsx' if key['task'].endswith('comps') else '.csv'
    files = [run / a['path'] for a in result.get('artifacts', []) if Path(a['path']).suffix in ('.xlsx', '.csv')]
    # Last version in execution order. Choose requested format when also supplied.
    candidates = [p for p in files if p.suffix == required] or files
    def version(p):
        match = re.search(r'-v(\d+)\.', p.name)
        return int(match[1]) if match else 0
    candidates.sort(key=version)
    file = candidates[-1] if candidates else None
    checks = [dict(id='readable_required_format', passed=False), dict(id='identity_and_order', passed=False),
              dict(id='selected_facts_and_unknowns', passed=False), dict(id='source_identifiers', passed=False)]
    audit = dict(applicable=True, required_format=required, checks=checks, file=str(file.relative_to(run)) if file else None,
                 criterion='Original artifact consistency with submitted answer; factual truth is scored separately', issues=[])
    if file is None:
        audit['issues'].append('No generated CSV or XLSX file')
        return audit
    try:
        tables = read_tables(file)
    except Exception as e:
        audit['issues'].append('Unreadable original file: ' + str(e))
        return audit
    checks[0]['passed'] = file.suffix == required
    if file.suffix != required:
        audit['issues'].append(f'Requested {required}; delivered {file.suffix}')
    shortlist = answer['shortlist']
    possible = []
    for sheet, rows in tables:
        if any(word in norm(sheet) for word in ['decision', 'candidate', 'reject', 'exclusion']):
            continue
        for index, row in enumerate(rows[:20]):
            headers = [canonical(v) for v in row]
            if 'record_id' in headers:
                possible.append((sheet, rows[index + 1:], headers))
                break
    audit['sheets'] = [s for s, _ in tables]
    if not possible:
        if not shortlist:
            # Empty output is explicit only if the artifact states no matches.
            text = ' '.join(str(v) for _, rows in tables for row in rows for v in row if v is not None).lower()
            explicit = bool(re.search(r'(no|zero|0) (qualifying|eligible|qualified|matching|verified)', text))
            for check in checks[1:]:
                check['passed'] = explicit
            if not explicit:
                audit['issues'].append('Cannot identify an explicit empty shortlist')
            return audit
        audit['issues'].append('Could not map an original shortlist table by record identifier; manual mapping required')
        audit['needs_manual_mapping'] = True
        return audit
    sheet, rows, headers = possible[0]
    record_col = headers.index('record_id')
    original_rows = [row for row in rows if len(row) > record_col and re.fullmatch(r'R\d+', str(row[record_col]).strip())]
    # An explicit all-rejected screening grid represents an empty shortlist.
    # Unknown/blank eligibility is not evidence of rejection.
    if not shortlist and 'eligible' in headers and original_rows:
        col = headers.index('eligible')
        def rejected(row):
            value = row[col] if len(row) > col else None
            return value is False or str(value).strip().lower() in {'false', 'no', 'ineligible', 'not eligible'}
        if all(rejected(row) for row in original_rows):
            audit['empty_shortlist_representation'] = 'Every displayed candidate is explicitly ineligible'
            original_rows = []
    ids = [str(row[record_col]).strip() for row in original_rows]
    expected_ids = [item['record_id'] for item in shortlist]
    checks[1]['passed'] = ids == expected_ids
    audit['table_sheet'] = sheet
    audit['original_record_order'] = ids
    audit['answer_record_order'] = expected_ids
    if ids != expected_ids:
        audit['issues'].append('Original shortlist identities/order differ from the submitted answer')
    by_id = {str(row[record_col]).strip(): row for row in original_rows}
    fact_checks, source_checks = [], []
    for item in shortlist:
        row = by_id.get(item['record_id'], [])
        required_facts = key['candidates'].get(item['record_id'], {}).get('facts', item.get('facts', {}))
        for field in required_facts:
            present = field in headers and len(row) > headers.index(field)
            original = actual = row[headers.index(field)] if present else None
            if case is not None and records is not None:
                mapped, _ = normalize({'shortlist': [{'record_id': item['record_id'], 'facts': {field: actual}}]}, case, records)
                actual = mapped['shortlist'][0]['facts'][field]
            expected = item.get('facts', {}).get(field)
            # A blank export is not an explicitly marked unknown, even if JSON
            # correctly says null. This is a delivery annotation issue.
            passed = present and equal(actual, expected) and (expected is not None or actual not in (None, ''))
            fact_checks.append(dict(record_id=item['record_id'], field=field, actual=actual, original=original, expected=expected, passed=passed))
        sources = set(re.findall(r'(?:S-R\d+|U-R\d+-\d+)', ' '.join(str(v) for v in row)))
        expected_sources = set(item.get('source_ids', []))
        source_checks.append(dict(record_id=item['record_id'], passed=bool(row) and expected_sources <= sources,
                                  expected=sorted(expected_sources), actual=sorted(sources)))
    checks[2]['passed'] = all(c['passed'] for c in fact_checks) and checks[1]['passed']
    checks[3]['passed'] = all(c['passed'] for c in source_checks) and checks[1]['passed']
    audit['field_checks'] = fact_checks
    if result['track'] == 'agent' and file.suffix == '.csv':
        csv_null_attribution(run, file, fact_checks)
    audit['harness_induced_null_annotations'] = sum(c.get('attribution') == 'benchmark_csv_serializer' for c in fact_checks)
    if audit['harness_induced_null_annotations']:
        audit['issues'].append(f"{audit['harness_induced_null_annotations']} blank unknown annotations were caused by the benchmark CSV writer after explicit model-supplied JSON nulls; these are harness delivery failures, not model factual errors.")
    audit['source_checks'] = source_checks
    audit['issues'] += [f"{c['record_id']} / {c['field']}: artifact differs from answer or lacks explicit unknown" for c in fact_checks if not c['passed']]
    audit['issues'] += [f"{c['record_id']}: missing answer source IDs" for c in source_checks if not c['passed']]
    audit['source_sha256'] = hashlib.sha256(file.read_bytes()).hexdigest()
    return audit

def aggregate(rows):
    graded = [r for r in rows if r.get('grade')]
    def metric(name):
        return dict(passed=sum(r['grade'][name]['passed'] for r in graded), total=sum(r['grade'][name]['total'] for r in graded))
    costs = [r.get('cost_usd') if r['track'] != 'lev_native' else r.get('estimated_inference_cost_usd') for r in rows]
    errors = [e for r in graded for e in r['grade']['material_errors']]
    artifact_checks = [c for r in rows for c in r.get('artifact_audit', {}).get('checks', [])]
    unanswered = [r for r in rows if not r.get('grade')]
    unanswered_target = sum(r.get('expected_target', 0) for r in unanswered)
    screening = metric('candidate_accuracy')
    screening['answered_total'] = screening['total']
    screening['unanswered'] = sum(r.get('expected_decisions', 0) for r in unanswered)
    screening['total'] += screening['unanswered']
    return dict(planned=len(rows), completed=sum(r['status'] == 'completed' for r in rows), graded=len(graded),
        failed=len(unanswered), unanswered_target=unanswered_target,
        verified=sum(r['grade']['verified_count'] for r in graded), target=sum(r['grade']['target_count'] for r in graded)+unanswered_target,
        eligible=sum(r['grade']['eligible_count'] for r in graded), returned=sum(r['grade']['returned_count'] for r in graded),
        screening=screening, facts=metric('field_accuracy'), evidence=metric('evidence_accuracy'), ranking=metric('ranking_pair_agreement'),
        abstention=dict(passed=sum(r['grade']['correct_abstention'] is True for r in graded), total=sum(r['grade']['correct_abstention'] is not None for r in graded)),
        material_errors=len(errors), cases_with_material_errors=sum(bool(r['grade']['material_errors']) for r in graded),
        artifact_checks=dict(passed=sum(c['passed'] for c in artifact_checks), total=len(artifact_checks)),
        harness_induced_null_annotations=sum(r.get('artifact_audit', {}).get('harness_induced_null_annotations', 0) for r in rows),
        cases_with_harness_null_loss=sum(bool(r.get('artifact_audit', {}).get('harness_induced_null_annotations')) for r in rows),
        cost_total_usd=sum(c for c in costs if c is not None), costs_recorded=sum(c is not None for c in costs),
        cost_per_verified_usd=(sum(costs) / sum(r['grade']['verified_count'] for r in graded)) if all(c is not None for c in costs) and sum(r['grade']['verified_count'] for r in graded) else None)

def collect():
    plan = json.loads((EXP / 'plan.json').read_text())
    for path, expected in plan['sha256'].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen file drift: ' + path)
    rows = []
    for case in plan['cases']:
        key = json.loads((CASES / case / 'answer-key.json').read_text())
        spec = json.loads((CASES / case / 'case.json').read_text())
        records = json.loads((CASES / case / 'sources/records.json').read_text())
        for (track, system), label in zip(SYSTEMS, NAMES):
            run = EXP / track / system.replace('/', '--') / case
            if (run / 'result.json').exists():
                result = json.loads((run / 'result.json').read_text())
            else:
                result = dict(case_id=case, system=system, track=track, status='running' if run.exists() else 'not_started')
            result.update(label=label, task=key['task'], path=str(run.relative_to(ROOT)),
                          expected_target=key['target_count'], expected_decisions=len(key['candidates']))
            if (run / 'answer.json').exists():
                answer = json.loads((run / 'answer.json').read_text())
                original_grade = grade(key, answer)
                (run / 'grade-v1.json').write_text(json.dumps(original_grade, indent=2) + '\n')
                normalized, changes = normalize(answer, spec, records)
                result['grade'] = dict(grade(key, normalized), scoring_version=VERSION, representation_adjustments=changes)
                result['artifact_audit'] = audit_artifact(run, result, normalized, key, spec, records)
                (run / 'grade.json').write_text(json.dumps(result['grade'], indent=2) + '\n')
                (run / 'artifact-audit.json').write_text(json.dumps(result['artifact_audit'], indent=2) + '\n')
            rows.append(result)
    data = dict(version=VERSION, execution_version=plan['version'], generated_at=datetime.now(timezone.utc).isoformat(), planned_runs=120,
        scoring_erratum='SCORING-ERRATUM.md', aggregation='All planned target slots and candidate decisions remain in denominators; infrastructure failures are unanswered, not attributed model factual errors.',
        source_commit=plan['source_commit'], qualification=plan['qualification'], conditions=plan['limitations'],
        case_ids=plan['cases'], runs=rows, summary=[], tasks=[])
    for (track, system), label in zip(SYSTEMS, NAMES):
        subset = [r for r in rows if r['track'] == track and r['system'] == system]
        data['summary'].append(dict(track=track, system=system, label=label, **aggregate(subset)))
        for task in ['sales_comps', 'rent_comps', 'sponsor_leads', 'refinance_leads']:
            data['tasks'].append(dict(track=track, system=system, label=label, task=task, **aggregate([r for r in subset if r['task'] == task])))
    (EXP / 'results.json').write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    with (EXP / 'run-summary.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['case', 'system', 'condition', 'status', 'verified', 'target', 'eligible', 'returned', 'screening_correct', 'screening_total', 'material_errors', 'artifact_passed', 'artifact_total', 'inference_usd', 'cost_basis'])
        for r in rows:
            g = r.get('grade', {}); a = r.get('artifact_audit', {}).get('checks', [])
            writer.writerow([r['case_id'], r['label'], r['track'], r['status'], g.get('verified_count'), g.get('target_count'), g.get('eligible_count'), g.get('returned_count'),
                             g.get('candidate_accuracy', {}).get('passed'), g.get('candidate_accuracy', {}).get('total'), len(g['material_errors']) if g else None,
                             sum(c['passed'] for c in a) if a else None, len(a) or None,
                             r.get('estimated_inference_cost_usd') if r['track'] == 'lev_native' else r.get('cost_usd'), r.get('cost_basis')])
    print(json.dumps(data['summary'], indent=2))
    return data

if __name__ == '__main__':
    collect()
