import json
from pathlib import Path
import unittest
from crebench.normalize import normalize, score_text
CASE = Path('cases/public/harbor-court-001')

class NormalizeTests(unittest.TestCase):
    def setUp(self):
        self.answer = json.loads((CASE/'reference-answer.json').read_text())

    def test_presentation_variants_preserve_financial_score(self):
        forms = [json.dumps(self.answer), 'Here is the answer:\n```json\n'+json.dumps(self.answer)+'\n```',
                 'Answer follows.\n'+json.dumps(self.answer)+'\nDone.',
                 json.dumps({**self.answer['fields'], 'discrepancies':self.answer['discrepancies']}),
                 json.dumps({'fields':{k:v['value'] for k,v in self.answer['fields'].items()},'discrepancies':self.answer['discrepancies']})]
        for text in forms:
            with self.subTest(text=text[:30]):
                result=score_text(CASE,text)
                self.assertEqual(result['groups']['financial']['passed'],30)

    def test_missing_evidence_does_not_erase_correct_value(self):
        a=self.answer; a['fields']['noi'].pop('evidence')
        result=score_text(CASE,json.dumps(a))
        self.assertEqual(result['groups']['financial']['passed'],30)
        self.assertIn('noi.evidence',result['groups']['references']['failed'])

    def test_wrong_value_is_never_repaired(self):
        a=self.answer; a['fields']['noi']['value']=151000
        result=score_text(CASE,'```json\n'+json.dumps(a)+'\n```')
        self.assertIn('noi',result['groups']['financial']['failed'])
        self.assertIn('noi.reconciles',result['groups']['financial']['failed'])
        self.assertEqual(result['normalized_answer']['fields']['noi']['value'],151000)

    def test_duplicates_nonfinite_and_ambiguous_answers_rejected(self):
        for s in ['{"noi":1,"noi":2}', '{"noi":NaN}', '{} {}', '```json\n{}\n```\n```json\n{}\n```', '```json\n{}\n```\nAlternative: {}']:
            with self.subTest(text=s), self.assertRaises(ValueError): normalize(s)

    def test_numeric_display_without_unit_guessing(self):
        a,_=normalize('{"noi":"$150,000", "unit_occupancy_pct":"75%", "max_ltv":0.65}')
        self.assertEqual(a['fields']['noi']['value'],150000)
        self.assertEqual(a['fields']['unit_occupancy_pct']['value'],75)
        self.assertEqual(a['fields']['max_ltv']['value'],0.65)

    def test_missing_values_stay_missing(self):
        result=score_text(CASE,'{"noi":150000}')
        self.assertEqual(result['groups']['financial']['passed'],1)
        self.assertNotIn('operating_revenue',result['normalized_answer']['fields'])

    def test_constraint_labels_are_equivalent_but_wrong_constraints_fail(self):
        for label in ['ltv','LTV','ltv_limit','Loan-to-value']:
            a=self.answer; a['fields']['binding_constraint']['value']=label
            self.assertTrue(score_text(CASE,json.dumps(a))['financial_complete'])
        for label in ['DSCR','debt_yield_limit']:
            a=self.answer; a['fields']['binding_constraint']['value']=label
            self.assertIn('binding_constraint',score_text(CASE,json.dumps(a))['groups']['financial']['failed'])

    def test_duplicate_conflicts_are_noise_but_false_conflicts_fail(self):
        a=self.answer;a['discrepancies'].append(a['discrepancies'][0])
        self.assertTrue(score_text(CASE,json.dumps(a))['financial_complete'])
        a['discrepancies'].append('historical_revenue_differs_from_current_rent')
        self.assertIn('conflicts.exact_set',score_text(CASE,json.dumps(a))['groups']['financial']['failed'])
