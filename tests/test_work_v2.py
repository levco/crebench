import json,tempfile,unittest
from pathlib import Path
import openpyxl
from crebench.grade_work_v2 import grade,equivalent
from crebench.work_v2_scoring_v1_1 import score
from crebench.work_v2_tools import WorkContext,write_workbook,recalc,read_cell
ROOT=Path(__file__).resolve().parents[1];CASES=ROOT/'benchmarks/cre-work-v2/cases'

class WorkV2Test(unittest.TestCase):
 def test_reference_matches_actual_source_rows(self):
  # Independent of the fixture authoring parameters and reference-grade replay.
  for case in CASES.iterdir():
   ref=json.loads((case/'reference.json').read_text())
   for stage,rel in [('initial','sources/rent-roll-certified.xlsx'),('revision','revision/rent-roll-revised.xlsx')]:
    book=openpyxl.load_workbook(case/rel,data_only=True,read_only=True)
    rows=[r for r in list(book.active.values)[4:] if isinstance(r[4],(int,float))]
    expected=ref[stage];active=[r for r in rows if r[3]=='active'];pending=[r for r in rows if r[3]=='pending']
    with self.subTest(case=case.name,stage=stage):
     self.assertEqual(sum(r[4] for r in rows)*12,expected['gross_potential_rent'])
     self.assertEqual(sum(r[2] for r in rows),expected['total_area_sf'])
     self.assertEqual(sum(r[2] for r in active),expected['occupied_area_sf'])
     self.assertEqual(len(rows),expected['total_units']);self.assertEqual(len(active),expected['occupied_units']);self.assertEqual(len(pending),expected['pending_units'])
    book.close()
 def test_revision_risk_correction_and_ambiguous_fields_apply_uniformly(self):
  c=CASES/'mf-01';key=json.loads((c/'reference.json').read_text())['revision']
  fields=[{'id':f,'value':v} for f,v in key.items()]
  next(f for f in fields if f['id']=='risk_pending_in_occupancy')['value']='absent'
  a=score(c,{'fields':fields},'revision')
  for f in fields:
   if f['id'] in {'ltv_limit','dscr_limit','debt_yield_limit'}:f['value']=.1
  b=score(c,{'fields':fields},'revision')
  self.assertEqual(a['scores'],b['scores']);self.assertEqual(b['scores']['financial'],{'passed':12,'total':12})
  self.assertEqual(b['scores']['judgment'],{'passed':8,'total':8})
  self.assertEqual(sum(not r['scored'] for r in b['checks']),3)
  next(f for f in fields if f['id']=='risk_pending_in_occupancy')['value']='present'
  self.assertEqual(score(c,{'fields':fields},'revision')['risk_counts']['false_positives'],1)
 def test_citation_objects_change_locations_only(self):
  c=CASES/'mf-01';analysis={'fields':[{'id':'total_units','value':999,'evidence':[{'file':'rent-roll-certified.xlsx','loc':'A5'}]}]}
  r=score(c,analysis,'initial');f=next(x for x in r['checks'] if x['field']=='total_units')
  self.assertTrue(f['citation_location_present']);self.assertFalse(f['passed']);self.assertEqual(f['actual'],999)
 def test_reference_answers_are_solvable_for_all_cases_and_stages(self):
  for c in sorted(CASES.iterdir()):
   key=json.loads((c/'reference.json').read_text())
   for stage in ('initial','revision'):
    result=grade(c,{'fields':[{'id':k,'value':v} for k,v in key[stage].items()]},stage)
    self.assertTrue(all(x['passed'] for x in result['checks']),(c.name,stage));self.assertIsNone(result['professional_acceptance'])
 def test_revision_preserves_actuals_and_updates_proscribed_assumptions(self):
  for c in CASES.iterdir():
   k=json.loads((c/'reference.json').read_text());a,b=k['initial'],k['revision']
   self.assertEqual(a['reported_t12_noi'],b['reported_t12_noi'])
   self.assertEqual(a['uw_tax'],b['uw_tax']);self.assertEqual(a['uw_insurance'],b['uw_insurance'])
   self.assertAlmostEqual(b['gross_potential_rent']-a['gross_potential_rent'],2700)
   self.assertAlmostEqual(b['cap_rate']-a['cap_rate'],.0025)
   self.assertAlmostEqual(b['sizing_rate']-a['sizing_rate'],.0075)
   self.assertEqual(b['occupied_units']-a['occupied_units'],1 if a['pending_units'] else 0)
 def test_material_mutation_and_duplicate_are_not_hidden(self):
  c=CASES/'mf-01';k=json.loads((c/'reference.json').read_text())['initial'];fields=[{'id':f,'value':v} for f,v in k.items()]
  next(x for x in fields if x['id']=='maximum_loan')['value']*=1.1
  result=grade(c,{'fields':fields});self.assertEqual(result['critical_errors'],1)
  fields.append({'id':'maximum_loan','value':k['maximum_loan']})
  result=grade(c,{'fields':fields});self.assertIn('maximum_loan',result['duplicate_fields']);self.assertEqual(result['critical_errors'],1)
 def test_unknown_units_and_boolean_are_distinct(self):
  self.assertTrue(equivalent('insurance_policy_limit','Unknown',None));self.assertFalse(equivalent('insurance_policy_limit',0,None))
  self.assertFalse(equivalent('occupied_units',True,1));self.assertFalse(equivalent('unit_occupancy',95,.95));self.assertTrue(equivalent('unit_occupancy','95%',.95))
  self.assertFalse(equivalent('maximum_loan',{'value':100,'unit':'EUR'},100))
  missing=grade(CASES/'mf-04',{'fields':[]});self.assertFalse(next(x for x in missing['checks'] if x['field']=='insurance_policy_limit')['passed'])
 def test_source_and_revision_are_isolated(self):
  with tempfile.TemporaryDirectory() as temp:
   ctx=WorkContext(CASES/'mf-01',Path(temp))
   for name in ('../reference.json','reference.json','rent-roll-revised.xlsx','/etc/passwd'):
    with self.assertRaises(ValueError):ctx.source(name)
   ctx.stage='revision';self.assertTrue(ctx.source('rent-roll-revised.xlsx').exists())
 def test_public_workbook_renderer_and_recalculation(self):
  spec={'sheets':[{'name':'Model','cells':[{'cell':'A1','value':'Income'},{'cell':'B1','value':100000},{'cell':'B2','value':.05},{'cell':'B3','formula':'=B1/B2'},{'cell':'A4','value':None}]}]}
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);path=root/'model.xlsx';write_workbook(spec,path);cached=recalc(path,root/'calc');book=openpyxl.load_workbook(cached,data_only=True)
   self.assertEqual(read_cell(book,'Model!B3'),2000000);self.assertEqual(read_cell(book,'Model!A4'),'Unknown')
   bad={'sheets':[{'name':'Model','cells':[{'cell':'A1','formula':'=WEBSERVICE("https://example.com")'}]}]}
   with self.assertRaises(ValueError):write_workbook(bad,root/'bad.xlsx')
 def test_false_alarm_on_clean_controls(self):
  k=json.loads((CASES/'mf-05/reference.json').read_text())['initial'];self.assertTrue(all(v=='absent' for f,v in k.items() if f.startswith('risk_')))
  r=grade(CASES/'mf-05',{'fields':[{'id':'risk_missing_insurance','value':'present'}]});self.assertEqual(r['risk_counts']['false_positives'],1)
