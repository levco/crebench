import unittest
from crebench.normalize_workflow import normalize

class DisplayNormalization(unittest.TestCase):
    def test_annotated_rate_and_attribution(self):
        original={'fields':[{'id':'contract_rate','value':'6.250% (fixed)','evidence':['Lender-Terms.pdf p.1']}]}
        result,changes=normalize(original)
        self.assertEqual(result['fields'][0]['value'],'6.250%')
        self.assertEqual(result['fields'][0]['original_display_value'],'6.250% (fixed)')
        self.assertEqual(original['fields'][0]['value'],'6.250% (fixed)')
        self.assertEqual(len(changes),1)
    def test_conflicting_annotation_is_not_a_numeric_answer(self):
        for value in ['100 (actually 200)','100 (should be 200)','100 (corrected to 200)','100 (not 100)']:
            self.assertEqual(normalize({'fields':[{'id':'maximum_loan','value':value}]})[0]['fields'][0]['value'],value)
    def test_dates_and_unknowns_are_preserved(self):
        for field,value in [('subject_lease_expiry','2030-08-31'),('verified_renewal_insurance','Unknown'),('maximum_loan',None)]:
            self.assertEqual(normalize({'fields':[{'id':field,'value':value}]})[0]['fields'][0]['value'],value)
    def test_evidence_question_equivalent_negations(self):
        for value in [False,'FALSE','No','No — no exercise notice in packet','No - not evidenced']:
            self.assertEqual(normalize({'fields':[{'id':'renewal_option_exercised','value':value}]})[0]['fields'][0]['value'],'Not evidenced')
        self.assertEqual(normalize({'fields':[{'id':'renewal_option_exercised','value':'Yes'}]})[0]['fields'][0]['value'],'Yes')
    def test_unicode_ratio_unit(self):
        self.assertEqual(normalize({'fields':[{'id':'sizing_dscr','value':'1.250×'}]})[0]['fields'][0]['value'],'1.250x')
