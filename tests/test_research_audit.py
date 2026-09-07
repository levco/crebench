import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

collector = module('research_collector', 'tools/collect-research.py')
native = module('research_native', 'tools/record-native-research.py')

class ResearchAuditTests(unittest.TestCase):
    def test_equivalent_financial_headers(self):
        for value, expected in [('Annual Face Rent $/SF', 'annual_face_rent_psf'),
                                ('Effective Net Rent ($/SF/yr)', 'effective_net_rent_psf_year'),
                                ('price_per_unit (USD/sf)', 'price_per_unit')]:
            self.assertEqual(collector.canonical(value), expected)

    def test_original_csv_unknowns_and_order(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            file = run / 'prospects.csv'
            answer = {'shortlist': [{'record_id': 'R1234', 'facts': {'contact_email': None}, 'source_ids': ['S-R1234']}]}
            key = {'task': 'sponsor_leads', 'candidates': {'R1234': {'facts': {'contact_email': None}}}}
            result = {'track': 'agent', 'artifacts': [{'path': 'prospects.csv'}]}
            def audit(value):
                with file.open('w', newline='') as f:
                    csv.writer(f).writerows([['Record ID', 'Email', 'Sources'], ['R1234', value, 'S-R1234']])
                return collector.audit_artifact(run, result, answer, key)
            self.assertTrue(all(c['passed'] for c in audit('unknown')['checks']))
            self.assertFalse(audit('')['checks'][2]['passed'])
            self.assertFalse(audit('invented@example.com')['checks'][2]['passed'])
            answer['shortlist'][0]['record_id'] = 'R9999'
            self.assertFalse(audit('unknown')['checks'][1]['passed'])

    def test_cost_sum_excludes_duplicate_summary(self):
        text = '''results[1]:
  - aiSessionId: session
    id: trace
    createdAt: date
    inputState: "packet"
    totalCost: 0.5
    totalLatency: 10
    events[3]:
      - createdAt: date
        event: $ai_generation
        properties:
          "$ai_span_name": "model:example"
          "$ai_total_cost_usd": 0.4
          "$ai_model": example
          "$ai_tools_called": external_search
      - createdAt: date
        event: $ai_embedding
        properties:
          "$ai_span_name": "model:embedding"
          "$ai_total_cost_usd": 0.1
          "$ai_model": embedding
      - createdAt: date
        event: $ai_generation
        properties:
          "$ai_span_name": "run_summary:example"
          "$ai_total_cost_usd": 0.5
'''
        audit, _ = native.trace_audit(text, 'packet')
        self.assertEqual(audit['total_cost_usd'], .5)
        self.assertEqual(audit['model_calls'], 2)
        self.assertEqual(audit['external_retrieval_audit'], 'needs_review')
        self.assertFalse(audit['confirmed_common_corpus'])
        observed, _ = native.trace_audit(text.replace('external_search', 'get_generated_file'), 'packet')
        self.assertEqual(observed['external_retrieval_audit'], 'no_retrieval_observed_partial_coverage')
        self.assertFalse(observed['confirmed_common_corpus'])
        with self.assertRaises(ValueError):
            native.trace_audit(text, 'different packet')
        with self.assertRaises(ValueError):
            native.trace_audit(text.replace('events[3]', 'events[4]'), 'packet')

    def test_missing_cost_is_unknown(self):
        summary = collector.aggregate([{'status': 'completed', 'track': 'lev_native'}])
        self.assertEqual(summary['costs_recorded'], 0)
        self.assertIsNone(summary['cost_per_verified_usd'])

    def test_infrastructure_failure_retains_unanswered_denominators(self):
        summary = collector.aggregate([{'status': 'infrastructure_error', 'track': 'direct',
            'expected_target': 3, 'expected_decisions': 20, 'cost_usd': None}])
        self.assertEqual(summary['verified'], 0)
        self.assertEqual(summary['target'], 3)
        self.assertEqual(summary['screening'], {'passed': 0, 'total': 20, 'answered_total': 0, 'unanswered': 20})
        self.assertEqual(summary['material_errors'], 0)
        self.assertEqual(summary['costs_recorded'], 0)

    def test_null_loss_is_attributed_to_matching_original_export(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / 'turn-01').mkdir()
            log = run / 'turn-01/tool-01.json'
            call = {'name': 'export_csv', 'arguments': {'headers': ['record_id', 'contact_email'], 'rows': [['R1234', None]]},
                    'result': {'created': 'prospects.csv'}}
            log.write_text(json.dumps(call))
            def checks():
                return [{'record_id': 'R1234', 'field': 'contact_email', 'expected': None, 'actual': '', 'passed': False}]
            fields = checks()
            collector.csv_null_attribution(run, run / 'prospects.csv', fields)
            self.assertEqual(fields[0]['attribution'], 'benchmark_csv_serializer')
            fields = checks()
            collector.csv_null_attribution(run, run / 'other-version.csv', fields)
            self.assertNotIn('attribution', fields[0])
            call['arguments']['rows'][0][1] = ''
            log.write_text(json.dumps(call))
            fields = checks()
            collector.csv_null_attribution(run, run / 'prospects.csv', fields)
            self.assertNotIn('attribution', fields[0])

    def test_all_rejected_grid_is_an_explicit_empty_shortlist(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            file = run / 'prospects.csv'
            def audit(value):
                with file.open('w', newline='') as f:
                    csv.writer(f).writerows([['record_id', 'eligible'], ['R1234', value]])
                return collector.audit_artifact(run, {'track': 'agent', 'artifacts': [{'path': 'prospects.csv'}]},
                    {'shortlist': []}, {'task': 'sponsor_leads', 'candidates': {}})
            self.assertTrue(all(c['passed'] for c in audit('false')['checks']))
            self.assertFalse(audit('')['checks'][1]['passed'])
            self.assertFalse(audit('true')['checks'][1]['passed'])

if __name__ == '__main__':
    unittest.main()
