import unittest
from crebench.research_representation_v1_1 import normalize

class RepresentationTests(unittest.TestCase):
    def test_numeric_wrapper_preserves_value_and_requires_matching_unit(self):
        original={'shortlist':[{'record_id':'R1','facts':{'property_size':{'value':64,'unit':'sf'},'price_per_unit':{'value':125,'unit':'USD_per_sf'}}}]}
        value,changes=normalize(original,{'unit':'sf'},[])
        self.assertEqual(value['shortlist'][0]['facts'],{'property_size':64,'price_per_unit':125})
        self.assertEqual(len(changes),2)
        self.assertIsInstance(original['shortlist'][0]['facts']['property_size'],dict)
        wrong,_=normalize(original,{'unit':'unit'},[])
        self.assertEqual(wrong,original)
        original['shortlist'][0]['facts']['property_size']['value']=999
        value,_=normalize(original,{'unit':'sf'},[])
        self.assertEqual(value['shortlist'][0]['facts']['property_size'],999)

    def test_parent_annotation_needs_exact_source_relationship(self):
        records=[{'record_id':'R1','entity_id':'E1','firm_name':'Parent'},
                 {'record_id':'R2','entity_id':'E2','firm_name':'Property','parent_entity_id':'E1','firm_kind':'property_SPV','parent_link':'executed_ownership_schedule'}]
        answer={'shortlist':[{'record_id':'R2','facts':{'firm_name':'Parent (parent of SPV Property)','contact_name':'Wrong Person'}}]}
        value,changes=normalize(answer,{},records)
        self.assertEqual(value['shortlist'][0]['facts'],{'firm_name':'Parent','contact_name':'Wrong Person'})
        self.assertEqual(len(changes),1)
        records[1]['parent_link']='unverified'
        self.assertEqual(normalize(answer,{},records)[0],answer)

if __name__=='__main__':unittest.main()
