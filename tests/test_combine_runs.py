import json
from pathlib import Path
import tempfile
import unittest

from scripts.combine_runs import collect_runs
from working_models_processor import fingerprint


class CombineRunTests(unittest.TestCase):
    def make_run(self, root, name, key, prompt='same prompt', complete=True):
        run = root / name
        (run / 'raw').mkdir(parents=True)
        questions = [{'id':'A1','question':'Exact question?','group':'A','purpose':''}]
        manifest = {'schema_version':1,'questions':questions,'system_prompt':prompt,
                    'max_tokens':6000,'official_domains':['aquaskyplus.com'],
                    'question_hash':fingerprint(questions),'question_source':'snapshot.md',
                    'models':[{'key':key}], 'created_at':'2026-09-22T00:00:00+08:00', 'run_hash':'hash'}
        records = [{'model_key':key,'question_id':'A1','question':'Exact question?','status':'success'}] if complete else []
        (run / 'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
        (run / 'results.json').write_text(json.dumps(records),encoding='utf-8')
        (run / 'raw' / f'{key}_A1.json').write_text('{}',encoding='utf-8')
        return run

    def test_merge_keeps_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            a = self.make_run(root, 'first', 'a'); b = self.make_run(root, 'second', 'b')
            manifest, records, raw = collect_runs([a,b])
            self.assertTrue(manifest['report_only'])
            self.assertEqual([r['source_run'] for r in records], ['first','second'])
            self.assertEqual(len(raw), 2)

    def test_different_prompts_and_duplicate_models_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            a = self.make_run(root, 'first', 'a')
            b = self.make_run(root, 'second', 'b', prompt='different prompt')
            duplicate = self.make_run(root, 'duplicate', 'a')
            for paths in ([a,b],[a,duplicate]):
                with self.assertRaises(ValueError): collect_runs(paths)

    def test_incomplete_run_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.make_run(Path(temp), 'incomplete', 'a', complete=False)
            with self.assertRaises(ValueError): collect_runs([run])
