import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from crebench.run_pilot import MODELS, credential, packet, prepare, write


class PilotTests(unittest.TestCase):
    def test_packet_excludes_keys(self):
        text = packet('cases/public/harbor-court-001')
        self.assertNotIn('<file name="answer-key.json">', text)
        self.assertNotIn('<file name="reference-answer.json">', text)
        self.assertEqual(text.count('<file name='), 6)

    def test_records_cannot_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'record.json'
            write(path, {'first': True})
            with self.assertRaises(FileExistsError):
                write(path, {'first': False})

    def test_env_is_data_not_executable(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict('os.environ', {}, clear=True):
            path = Path(folder)/'.env.local'
            path.write_text('VERCEL_OIDC_TOKEN="$(never-execute)"\n')
            self.assertEqual(credential(path), '$(never-execute)')

    def test_expensive_plan_rejected_before_creating_requests(self):
        with tempfile.TemporaryDirectory() as folder:
            catalog = Path(folder)/'catalog.json'
            write(catalog, {'data': [{'id': m, 'pricing': {'input': '1', 'output': '1'}} for m in MODELS]})
            with self.assertRaisesRegex(ValueError, 'exceeds'):
                prepare('cases/public/harbor-court-001', Path(folder)/'run', catalog)
            self.assertFalse((Path(folder)/'run').exists())

    def test_same_packet_all_models_no_keys_or_tools(self):
        with tempfile.TemporaryDirectory() as folder:
            catalog = Path(folder)/'catalog.json'
            write(catalog, {'data': [{'id': m, 'pricing': {'input': '.000001', 'output': '.000001'}} for m in MODELS]})
            target = Path(folder)/'run'
            prepare('cases/public/harbor-court-001', target, catalog)
            requests = [json.loads(p.read_text()) for p in target.glob('r*/request.json')]
            self.assertEqual(len(requests), 9)
            self.assertEqual(len({json.dumps(r['messages']) for r in requests}), 1)
            self.assertTrue(all(set(r) == {'model', 'messages', 'max_tokens', 'stream'} for r in requests))


if __name__ == '__main__':
    unittest.main()
