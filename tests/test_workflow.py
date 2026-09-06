import importlib.util
import math
from pathlib import Path
import tempfile
import unittest
import json
from crebench.grade_workflow import grade,equivalent

CASE=Path(__file__).resolve().parents[1]/'benchmarks/workflow-v1/cases/meadow-commerce'


class WorkflowGradingTest(unittest.TestCase):
    def test_missing_is_not_a_correct_unknown(self):
        empty=grade(CASE,{'fields':[]})
        missing=next(x for x in empty['checks'] if x['field']=='verified_renewal_insurance')
        self.assertFalse(missing['passed'])
        answer=grade(CASE,{'fields':[{'id':'verified_renewal_insurance','value':None}]})
        self.assertTrue(next(x for x in answer['checks'] if x['field']=='verified_renewal_insurance')['passed'])

    def test_provisional_allowance_is_not_verified_insurance(self):
        self.assertFalse(equivalent('verified_renewal_insurance',36000,None))

    def test_presentation_normalization_preserves_values(self):
        self.assertTrue(equivalent('maximum_loan','$1,234,567',1234567))
        self.assertTrue(equivalent('contract_rate','6.50%',.065))
        self.assertTrue(equivalent('occupancy_area_pct','95.00%',95))
        self.assertTrue(equivalent('cash_to_borrower','($4,000)',-4000))
        self.assertFalse(equivalent('contract_rate','6.50',.065))

    def test_counts_exact_and_materiality_distinct_from_tolerance(self):
        self.assertFalse(equivalent('space_count',3.01,3))
        self.assertFalse(equivalent('maximum_loan',1001000,1000000))
        self.assertFalse(equivalent('space_count',True,1))

    def test_conflicting_duplicate_fields_do_not_choose_the_right_answer(self):
        result=grade(CASE,{'fields':[{'id':'space_count','value':3},{'id':'space_count','value':4}]})
        self.assertIn('space_count',result['duplicate_fields'])
        self.assertFalse(next(x for x in result['checks'] if x['field']=='space_count')['passed'])

    def test_supplied_reference_is_not_automatically_correct_evidence(self):
        result=grade(CASE,{'fields':[{'id':'space_count','value':3,'evidence':['Invented.pdf p.1']}]})
        check=next(x for x in result['checks'] if x['field']=='space_count')
        self.assertTrue(check['passed']);self.assertEqual(check['evidence_support_status'],'pending_source_review')
        self.assertIsNone(result['evidence_score'])

try:
    from crebench.workflow_tools import arithmetic,ToolContext,parse_json
    AVAILABLE=True
except ImportError:
    AVAILABLE=False


@unittest.skipUnless(AVAILABLE,'Workflow extras require the documented PDF/XLSX runtime')
class WorkflowToolsTest(unittest.TestCase):
    def test_monthly_payment_sign_and_zero_rate(self):
        self.assertAlmostEqual(arithmetic('pmt(0,360,360000)'),-1000)
        self.assertAlmostEqual(arithmetic('-12*pmt(.06/12,360,1000000)'),71946.0630183308,places=6)

    def test_arithmetic_has_no_code_or_file_access(self):
        for value in ["__import__('os').getcwd()",'open("answer-key.json")','(1).__class__','[x for x in range(5)]','2**10001']:
            with self.assertRaises((ValueError,SyntaxError)):arithmetic(value)

    def test_missing_source_cannot_escape_packet(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'case/sources').mkdir(parents=True)
            (root/'case/answer-key.json').write_text('{"secret":1}')
            context=ToolContext(root/'case',root/'run')
            for name in ['../answer-key.json','answer-key.json','/etc/passwd']:
                with self.assertRaises(ValueError):context.source(name)

    def test_format_wrapper_is_not_an_answer_correction(self):
        self.assertEqual(parse_json('```json\n{"value": 4}\n```'),{'value':4})
        with self.assertRaises(ValueError):parse_json('{"value": }')
        with self.assertRaises(ValueError):parse_json('{"value": 4,"value": 5}')
        with self.assertRaises(ValueError):parse_json('{"value": NaN}')

    def test_batch_is_ordered_arithmetic_without_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);context=ToolContext(root/'case',root/'run')
            result=context.call('calculate_batch',{'steps':[{'name':'income','expression':'1200*12'},{'name':'net','expression':'income-4000'}]})
            self.assertEqual(result['values'],{'income':14400,'net':10400})
            with self.assertRaises(ValueError):context.call('calculate_batch',{'steps':[{'name':'x','expression':'answer_key'}]})

    def test_nonfinite_and_excessive_values_rejected(self):
        for expression in ['1/0','1e100','exp(1000)','sqrt(-1)']:
            with self.assertRaises((ValueError,ZeroDivisionError,OverflowError)):arithmetic(expression)


if __name__=='__main__':unittest.main()
