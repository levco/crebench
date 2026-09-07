import copy
import importlib.util
import json
from pathlib import Path
import unittest

from crebench.research_reference import resolve, truth, effective_rent, from_case
from crebench.grade_research import grade, equal
from crebench.run_research import normalize_answer, validate_answer

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('research_builder',ROOT/'tools/build-research-cases.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)


def ideal(key):
    return dict(shortlist=[dict(record_id=rid,facts=key['candidates'][rid]['facts'],
                               source_ids=key['candidates'][rid]['required_sources'],rationale='Reference')
                           for rid in key['ordered_unique_ids'][:key['target_count']]],
                candidate_decisions=[dict(record_id=rid,eligible=r['eligible'],reason='Reference',source_ids=r['required_sources'])
                                     for rid,r in key['candidates'].items()],summary='Reference answer',limitations=[])


class ResearchTests(unittest.TestCase):
    def test_all_24_reference_answers_pass_without_runtime_keys(self):
        for task in builder.TASKS:
            for v in range(6):
                c,r,u=builder.build(task,v);key=truth(c,r,u);s=grade(key,ideal(key))
                self.assertEqual(s['candidate_accuracy'],dict(passed=20,total=20))
                self.assertEqual(s['verified_count'],key['target_count'])
                self.assertEqual(s['material_errors'],[])
                if v==5:self.assertTrue(s['correct_abstention'])

    def test_future_and_draft_updates_are_not_applied(self):
        c,rs,us=builder.build('sales_comps',0);resolved=resolve(c,rs,us)
        for u in us:
            raw=next(r for r in rs if r['record_id']==u['record_id'])
            got=resolved[u['record_id']]
            if u['published_at']>'2026-08-31' or u['document_kind']=='unsigned_draft':
                self.assertEqual(got['consideration'],raw['consideration'])
            else:self.assertEqual(got['consideration'],27_900_000)

    def test_duplicate_not_another_comp(self):
        c,r,u=builder.build('sales_comps',0);key=truth(c,r,u);answer=ideal(key)
        first=answer['shortlist'][0]
        answer['shortlist'][1]=copy.deepcopy(first)
        score=grade(key,answer)
        self.assertEqual(score['eligible_count'],4)
        self.assertTrue(any(e['type']=='duplicate_entity' for e in score['material_errors']))

    def test_money_units_normalize(self):
        c,rs,us=builder.build('sales_comps',0);key=truth(c,rs,us)
        for r in rs:
            if r['consideration'] is None:continue
            if any(u['entity_id']==r['entity_id'] and u['published_at']<=c['as_of'] and u['document_kind']=='executed_amendment' for u in us):continue
            factors={'USD':1,'USD_thousands':1000,'USD_millions':1_000_000}
            self.assertAlmostEqual(key['candidates'][r['record_id']]['facts']['consideration_usd'],r['consideration']*factors[r['consideration_unit']])

    def test_monthly_rent_matches_independent_geometric_formula(self):
        c,rs,us=builder.build('rent_comps',2);key=truth(c,rs,us);resolved=resolve(c,rs,us)
        for rid in key['eligible_record_ids']:
            r=resolved[rid];face,got=effective_rent(r);years=r['term_months']//12;g=r['annual_increase_pct']/100
            gross=face*((1+g)**years-1)/g-face/12*r['free_months']
            expense=(r['annual_expenses_psf'] or 0)*years
            expected=(gross-expense-r['ti_allowance_psf'])/years
            self.assertAlmostEqual(got,expected,places=9)

    def test_unknown_concessions_are_not_zero(self):
        c,r,u=builder.build('rent_comps',0);key=truth(c,r,u)
        rid=next(x['record_id'] for x in r if x['free_months'] is None)
        self.assertFalse(key['candidates'][rid]['eligible'])
        self.assertIsNone(key['candidates'][rid]['facts']['effective_net_rent_psf_year'])

    def test_executed_extension_removes_refinance_lead(self):
        c,r,u=builder.build('refinance_leads',0);key=truth(c,r,u)
        rid=next(x['record_id'] for x in u if x['changes'].get('extension_status')=='executed')
        self.assertFalse(key['candidates'][rid]['eligible'])
        self.assertEqual(key['candidates'][rid]['facts']['maturity_date'],'2028-09-30')

    def test_original_principal_never_becomes_outstanding_balance(self):
        c,r,u=builder.build('refinance_leads',0);key=truth(c,r,u);answer=ideal(key)
        item=answer['shortlist'][0];item['facts']=dict(item['facts']);item['facts']['outstanding_balance_usd']=item['facts']['original_principal_usd']
        score=grade(key,answer)
        self.assertEqual(score['verified_count'],key['target_count']-1)
        self.assertTrue(any(e.get('field')=='outstanding_balance_usd' for e in score['material_errors']))

    def test_spv_resolves_to_parent_and_deduplicates(self):
        c,rs,us=builder.build('sponsor_leads',0);key=truth(c,rs,us)
        r=next(r for r in rs if r['firm_kind']=='property_SPV');ref=key['candidates'][r['record_id']]
        self.assertEqual(ref['entity_id'],r['parent_entity_id']);self.assertTrue(ref['eligible'])
        self.assertEqual(key['available_unique'],6)
        self.assertGreaterEqual(len(ref['required_sources']),2)

    def test_no_results_does_not_get_a_fake_yield_percentage(self):
        c,r,u=builder.build('sponsor_leads',5);key=truth(c,r,u);s=grade(key,ideal(key))
        self.assertTrue(s['correct_abstention']);self.assertIsNone(s['verified_yield']);self.assertIsNone(s['selection_precision'])

    def test_evidence_dump_does_not_pass(self):
        c,r,u=builder.build('sales_comps',0);key=truth(c,r,u);answer=ideal(key)
        answer['shortlist'][0]['source_ids']=[x['source_id'] for x in r]
        self.assertFalse(grade(key,answer)['selected_checks'][0]['evidence_passed'])

    def test_missing_update_citation_fails(self):
        c,r,u=builder.build('rent_comps',0);key=truth(c,r,u);answer=ideal(key)
        item=next(i for i in answer['shortlist'] if any(s.startswith('U-') for s in i['source_ids']))
        item['source_ids']=[s for s in item['source_ids'] if s.startswith('S-')]
        self.assertEqual(grade(key,answer)['verified_count'],key['target_count']-1)

    def test_missing_candidate_decisions_fail(self):
        c,r,u=builder.build('sales_comps',0);key=truth(c,r,u);a=ideal(key);a['candidate_decisions']=[]
        self.assertEqual(grade(key,a)['candidate_accuracy']['passed'],0)

    def test_one_safe_result_cannot_hide_incomplete_shortlist(self):
        c,r,u=builder.build('sales_comps',0);key=truth(c,r,u);a=ideal(key);a['shortlist']=a['shortlist'][:1];s=grade(key,a)
        self.assertEqual(s['selection_precision'],1);self.assertEqual(s['verified_yield'],.2)

    def test_text_wrapper_extraction_does_not_repair_facts(self):
        value={'shortlist':[],'candidate_decisions':[],'summary':'x','limitations':[]}
        self.assertEqual(normalize_answer('Here is the answer:\n```json\n'+json.dumps(value)+'\n```\nDone.'),value)
        with self.assertRaises(ValueError):normalize_answer('There are five matches.')
        with self.assertRaises(ValueError):normalize_answer('{"shortlist": [], "shortlist": [1]}')

    def test_numeric_formatting_and_bool_not_as_number(self):
        self.assertTrue(equal('$1,000.00',1000));self.assertFalse(equal(True,1));self.assertFalse(equal(float('nan'),1))
        self.assertFalse(equal('~1000',1000));self.assertTrue(equal('Not published',None))


if __name__=='__main__':unittest.main()
