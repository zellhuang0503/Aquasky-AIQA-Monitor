import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import working_models_processor as monitor
from src.question_loader import load_question_records


class MonitorTests(unittest.TestCase):
    def test_source_table_preserves_all_questions_and_ignores_meeting_notes(self):
        rows = load_question_records(monitor.ROOT / 'config/questions_20260922.md')
        self.assertEqual([r['id'] for r in rows], [f'A{i}' for i in range(1, 6)] + [f'B{i}' for i in range(1, 8)])
        self.assertIn('（pressure tank）', rows[0]['question'])
        self.assertNotIn('AQUASKY', monitor.build_payload({'id':'test','api_type':'openrouter','search_engine':'native'}, rows[0], 6000)['messages'][0]['content'])

    def test_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'questions.md'
            p.write_text('| A1 | One | purpose |\n| A1 | Two | purpose |', encoding='utf-8')
            with self.assertRaises(ValueError):
                load_question_records(p)

    def test_provider_preference_keeps_exact_requested_model_and_search(self):
        model = {'id':'deepseek/deepseek-v4.1-flash','api_type':'openrouter',
                 'search_engine':'exa','provider':{'sort':'throughput'}}
        payload = monitor.build_payload(model, {'question':'Unchanged question?'}, 6000)
        self.assertEqual(payload['model'], model['id'])
        self.assertEqual(payload['provider'], {'sort':'throughput'})
        self.assertEqual(payload['plugins'], [{'id':'web','engine':'exa'}])
        self.assertEqual(payload['messages'][1]['content'], 'Unchanged question?')

    def test_body_url_is_not_a_citation_and_host_is_exact(self):
        raw = {'choices':[{'message':{'content':'AQUASKY https://aquaskyplus.com/'},'finish_reason':'stop'}]}
        result = monitor.normalize_response(raw)
        self.assertTrue(result['brand_mentioned'])
        self.assertFalse(result['official_cited'])
        self.assertFalse(monitor.official_url('https://aquaskyplus.com.evil.example'))
        self.assertFalse(monitor.official_url('https://evil.example/aquaskyplus.com'))
        self.assertTrue(monitor.official_url('https://www.aquaskyplus.com/en/'))

    def test_annotations_and_perplexity_citations_preserved(self):
        raw = {'citations':['https://aquaskyplus.com/'], 'choices':[{'message':{'content':'answer',
               'annotations':[{'type':'url_citation','url_citation':{'url':'https://aquaskyplus.com/','title':'Brand'}}]},'finish_reason':'stop'}]}
        result = monitor.normalize_response(raw)
        self.assertEqual(len(result['citations']), 1)
        self.assertTrue(result['official_cited'])

    def test_empty_and_truncated_are_not_successes(self):
        self.assertEqual(monitor.normalize_response({'choices':[]})['status'], 'failed')
        raw = {'choices':[{'message':{'content':'partial'},'finish_reason':'length'}]}
        self.assertEqual(monitor.normalize_response(raw)['status'], 'truncated')

    def test_google_redirect_resolves_without_fetching_destination(self):
        url = 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/example'
        rows = [{'citations':[{'url':url}]}]
        with patch.object(monitor.requests, 'head') as head:
            head.return_value.status_code = 302
            head.return_value.is_redirect = True
            head.return_value.headers = {'Location':'https://aquaskyplus.com/en/feature'}
            monitor.resolve_citation_redirects(rows)
            self.assertTrue(rows[0]['official_cited'])
            self.assertEqual(rows[0]['citations'][0]['url'], url)
            self.assertEqual(head.call_count, 1)
            self.assertFalse(head.call_args.kwargs['allow_redirects'])
            monitor.resolve_citation_redirects(rows)
            self.assertEqual(head.call_count, 1)

    def test_unresolved_google_redirect_is_explicit(self):
        rows = [{'citations':[{'url':'https://vertexaisearch.cloud.google.com/example'}]}]
        with patch.object(monitor.requests, 'head', side_effect=monitor.requests.Timeout):
            monitor.resolve_citation_redirects(rows)
        self.assertEqual(rows[0]['unresolved_citations'], 1)
        self.assertFalse(rows[0]['official_cited'])

    def test_report_denominator_uses_actual_questions(self):
        manifest = {'created_at':'now','question_hash':'hash','models':[{'key':'test','name':'Test','search_engine':'native'}],
                    'questions':[{'id':str(i)} for i in range(12)]}
        report = monitor.summary_markdown(manifest, [])
        self.assertIn('0/12', report)
        self.assertNotIn('/20', report)

    def test_offline_export_reopens_and_keeps_formula_as_text(self):
        from openpyxl import load_workbook
        record = {'model_key':'test','question_id':'A1','group':'A','question':'question',
                  'status':'success','answer':'=1+1','citations':[]}
        manifest = {'created_at':'now','question_hash':'hash','models':[{'key':'test','name':'Test','search_engine':'native'}], 'questions':[{}]}
        with tempfile.TemporaryDirectory() as tmp:
            monitor.write_reports(Path(tmp), manifest, [record])
            book = load_workbook(Path(tmp) / 'answers.xlsx')
            self.assertEqual(book.active['F2'].value, '=1+1')
            self.assertEqual(book.active['F2'].data_type, 's')
            book.close()
            self.assertEqual(json.loads((Path(tmp)/'results.json').read_text(encoding='utf-8'))[0]['question_id'], 'A1')

    def test_auth_error_not_retried_or_logged_with_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp)/'config.ini'
            config.write_text('[api_keys]\nopenrouter_api_key=secret\n', encoding='utf-8')
            client = monitor.APIClient(config)
            with patch.object(monitor.requests, 'post') as post:
                post.return_value.status_code = 401
                post.return_value.json.return_value = {'error':'secret'}
                result, fatal = client.query({'api_type':'openrouter'}, {})
                self.assertTrue(fatal)
                self.assertNotIn('secret', json.dumps(result))
                self.assertEqual(post.call_count, 1)

    def test_http_200_embedded_provider_failure_retries_and_keeps_evidence(self):
        failed = {'choices':[{'finish_reason':'error','error':{'code':502},
                             'message':{'content':'Incomplete'}}]}
        success = {'choices':[{'finish_reason':'stop','message':{'content':'Complete'}}]}
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp)/'config.ini'
            config.write_text('[api_keys]\nopenrouter_api_key=secret\n', encoding='utf-8')
            client = monitor.APIClient(config)
            with patch.object(monitor.requests, 'post') as post, patch.object(monitor.time, 'sleep'):
                post.return_value.status_code = 200
                post.return_value.json.side_effect = [failed, success]
                result, fatal = client.query({'api_type':'openrouter'}, {})
                self.assertFalse(fatal)
                self.assertEqual(result, success)
                self.assertEqual(client.retry_responses, [failed])
                self.assertEqual(post.call_count, 2)

    def test_resume_skips_saved_answers_and_rejects_changed_questions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'config').mkdir()
            questions = root / 'config/questions_20260922.md'
            questions.write_text('| A1 | Original question? | purpose |', encoding='utf-8')
            (root / 'config/working_models.json').write_text(json.dumps([
                {'key':'test','id':'test/model','api_type':'openrouter','name':'Test',
                 'search_engine':'native','enabled':True}]), encoding='utf-8')
            response = {'choices':[{'message':{'content':'Full answer'},'finish_reason':'stop'}]}
            with patch.object(monitor, 'ROOT', root), patch.object(monitor.APIClient, 'query', return_value=(response, False)) as query:
                args = ['--questions', str(questions), '--run']
                self.assertEqual(monitor.main(args), 0)
                run = next((root/'outputs/runs').iterdir())
                self.assertEqual(monitor.main(args + ['--resume', str(run)]), 0)
                self.assertEqual(query.call_count, 1)
                questions.write_text('| A1 | Changed question? | purpose |', encoding='utf-8')
                with self.assertRaises(SystemExit) as raised:
                    monitor.main(args + ['--resume', str(run)])
                self.assertEqual(raised.exception.code, 2)
                self.assertEqual(query.call_count, 1)


if __name__ == '__main__':
    unittest.main()
