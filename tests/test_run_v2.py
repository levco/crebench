import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from crebench.run_v2 import MODELS, prepare, execute, schema
from crebench.run_pilot import write

class V2RunnerTests(unittest.TestCase):
    def test_structured_schema_exposes_types_not_expected_values(self):
        s=schema('cases/public/harbor-court-001')
        self.assertEqual(len(s['properties']['fields']['properties']),27)
        self.assertNotIn('150000',json.dumps(s))
        self.assertNotIn('const',json.dumps(s))
        self.assertEqual(s['properties']['fields']['properties']['noi']['properties']['value']['type'],['number','null'])

    def test_mutated_request_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);catalog=root/'catalog.json'
            write(catalog,{'data':[{'id':m,'pricing':{'input':'.000001','output':'.000001'}} for m in MODELS]})
            target=root/'run';prepare('cases/public/harbor-court-001',target,catalog)
            requests=list(target.glob('r*/request.json'))
            self.assertEqual(len(requests),6)
            self.assertEqual(len({json.dumps(json.loads(p.read_text())['response_format']) for p in requests}),1)
            requests[0].write_text('{}')
            with patch('urllib.request.build_opener') as opener:
                with self.assertRaisesRegex(ValueError,'Request changed'):
                    execute('cases/public/harbor-court-001',target,None)
                opener.assert_not_called()
