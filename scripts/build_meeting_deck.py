"""Build the dated, offline client deck from preserved AIQA evidence.

Narrative and manual flags are specific to the reviewed run. Never refresh the
numbers beneath old conclusions: a new run requires a new editorial review.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'outputs/runs/combined_20260922_012711_656878'
OUT = ROOT / 'presentations/20260924'
MODELS = {
    'openai': 'GPT-6 Astra', 'google': 'Gemini 3.8 Flash',
    'perplexity': 'Perplexity Sonar Pro', 'claude': 'Claude Sonnet 5',
    'grok': 'Grok 4.6', 'deepseek': 'DeepSeek V4.1 Flash',
}
INTRO_ONLY = {'grok:A1', 'grok:A3', 'grok:A5', 'grok:B6'}
FLAGS = {
    'google:A4': ['中文名稱誤寫為「天水」；仍計入字面提及，不能當作品牌資訊正確'],
    'perplexity:B7': ['錯認為 Fluval Aquasky 水族燈；排除溢康品牌有效回答'],
    'grok:B7': ['有辨識溢康，但僅概述地區差異，未回答具體保固年限及申請流程'],
    'claude:B1': ['漂流故事是模型轉述，尚未獨立查證；不能取代控制條件下的耐久測試'],
    'claude:B5': ['未找到循環次數；與其他模型取用 FAQ 的結果不同'],
    'perplexity:B6': ['未找到 MOQ 數字；其他模型已從 FAQ 取得數字，需區分檢索差異與內容缺口'],
    'deepseek:B6': ['將 MOQ 適用範圍作了解釋；該解釋仍需業務核准'],
}

def visible_text(answer: str) -> str:
    text = re.sub(r'\[([^\]]*)\]\(https?://[^)]+\)', lambda m: m[1], answer)
    # Strip both linked and bare domains. A domain containing 'plus' is not a
    # literal brand-name mention. Restrict domain characters to ASCII so Chinese
    # prose immediately preceding an address is never swallowed.
    return re.sub(r'(?:https?://)?(?:www\.)?[a-z0-9_.-]+\.(?:com|org|net|tw|gov|edu)(?:\.[a-z]+)?(?:/[^\s)\]>]*)?', '', text, flags=re.I)

def build():
    records = json.loads((RUN / 'results.json').read_text(encoding='utf-8'))
    manifest = json.loads((RUN / 'manifest.json').read_text(encoding='utf-8'))
    assert len(records) == 72 and len({(r['model_key'], r['question_id']) for r in records}) == 72
    for r in records:
        r['id'] = f"{r['model_key']}:{r['question_id']}"
        r['model_name'] = MODELS[r['model_key']]
        text = visible_text(r['answer'])
        r['text_brand'] = bool(re.search(r'aqua\s*sky|溢康', text, re.I))
        r['text_plus'] = bool(re.search(r'aqua\s*sky\s*(?:plus|\+)', text, re.I))
        r['intro_only'] = r['id'] in INTRO_ONLY
        r['wrong_entity'] = r['id'] == 'perplexity:B7'
        r['review_flags'] = FLAGS.get(r['id'], []).copy()
        if r['intro_only']:
            r['review_flags'].append('只回開場，未展開題目所要求的名單、比較或條件；API status=success 並不等於答題完整')
        r['answer_sha256'] = hashlib.sha256(r['answer'].encode()).hexdigest()
        raw = RUN / 'raw' / f"{r['model_key']}_{r['question_id']}.json"
        assert raw.is_file(), raw
    assert {r['id'] for r in records if r['text_plus']} == {'openai:B7', 'perplexity:B6', 'claude:B1'}
    assert sum(r['text_brand'] for r in records if r['group'] == 'A') == 11
    assert sum(r['official_cited'] for r in records if r['group'] == 'B') == 41
    assert all(not r['text_brand'] for r in records if r['question_id'] == 'A3')
    data = {
        'as_of': '2026-09-22', 'meeting_date': '2026-09-24', 'review_date': '2026-09-23',
        'run_id': RUN.name, 'models': MODELS, 'questions': manifest['questions'],
        'records': records,
        'method': {
            'unit': 'one model × one exact question; one recorded response per pair',
            'brand': 'case-insensitive AQUASKY / Aqua Sky / 溢康 in answer text, excluding URLs; not an accuracy or recommendation score',
            'plus': 'case-insensitive AQUASKY Plus / Aqua Sky Plus / AQUASKY+ in answer text, excluding domains',
            'official': 'preserved structured citation metadata, aquaskyplus.com or a subdomain; not proof that the answer used the source correctly',
            'manual_flags': 'four introduction-only responses; one wrong entity; other selected qualitative flags, not exhaustive technical fact checking',
        },
        'source_sha256': hashlib.sha256((RUN / 'results.json').read_bytes()).hexdigest(),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'reviewed_evidence.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    template = (ROOT / 'templates/meeting_deck_20260924.html').read_text(encoding='utf-8')
    marked = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/marked/lib/marked.umd.js'
    # The parser is bundled, so the resulting HTML has no CDN dependency.
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    html = template.replace('__EVIDENCE_JSON__', payload).replace('__MARKED_BUNDLE__', marked.read_text(encoding='utf-8'))
    (OUT / 'AQUASKY_AIQA_客戶會議簡報_20260924.html').write_text(html, encoding='utf-8')
    print(json.dumps({'output': str(OUT), 'responses': len(records), 'A_mentions': 11, 'literal_Plus': 3,
                      'intro_only': len(INTRO_ONLY), 'wrong_entity': 1}, ensure_ascii=False))

if __name__ == '__main__':
    build()
