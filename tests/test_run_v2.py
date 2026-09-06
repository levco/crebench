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
        self.assertNotIn('"const":',json.dumps(s))
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

    def test_transient_failure_is_retained_and_resume_does_not_repeat(self):
        import io
        import urllib.error
        from unittest.mock import MagicMock
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);catalog=root/'catalog.json'
            write(catalog,{'data':[{'id':m,'pricing':{'input':'.000001','output':'.000001'}} for m in MODELS]})
            target=root/'run';plan=prepare('cases/public/harbor-court-001',target,catalog)
            plan['request_sha256']={k:v for k,v in plan['request_sha256'].items() if k=='r1-1'}
            (target/'plan.json').write_text(json.dumps(plan))
            answer=Path('cases/public/harbor-court-001/reference-answer.json').read_text()
            payload={'model':'openai/gpt-5','choices':[{'finish_reason':'stop','message':{'content':answer}}]}
            response=MagicMock();response.__enter__.return_value=response
            response.status=200;response.read.return_value=json.dumps(payload).encode()
            opener=MagicMock();opener.open.side_effect=[urllib.error.HTTPError('https://example.invalid',429,'rate limit',{},io.BytesIO(b'limited')),response]
            with patch('crebench.run_v2.credential',return_value='test-token'),patch('urllib.request.build_opener',return_value=opener),patch('time.sleep'):
                execute('cases/public/harbor-court-001',target,None)
                self.assertEqual(opener.open.call_count,2)
                r=json.loads((target/'r1-1/result.json').read_text())
                self.assertEqual([a['http_status'] for a in r['attempts']],[429,200])
                self.assertEqual(r['score']['groups']['financial']['passed'],30)
                execute('cases/public/harbor-court-001',target,None)
                self.assertEqual(opener.open.call_count,2)
