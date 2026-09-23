"""Combine disjoint model runs only when question and request settings match."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from working_models_processor import ROOT, dump_json, fingerprint, write_reports

COMMON_FIELDS = ('schema_version', 'questions', 'system_prompt', 'max_tokens', 'official_domains')


def collect_runs(paths):
    if not paths:
        raise ValueError('At least one source run is required.')
    merged = None
    records, raw_files, sources = [], [], []
    seen_models = set()
    for path in paths:
        path = Path(path).resolve()
        manifest = json.loads((path / 'manifest.json').read_text(encoding='utf-8'))
        if manifest.get('report_only'):
            raise ValueError('Use original API runs, not a previously combined report.')
        if manifest['question_hash'] != fingerprint(manifest['questions']):
            raise ValueError('Source question hash mismatch.')
        if merged is None:
            merged = {k: manifest[k] for k in COMMON_FIELDS}
            merged.update(models=[], question_hash=manifest['question_hash'],
                          question_source=manifest['question_source'])
        elif any(merged[k] != manifest[k] for k in COMMON_FIELDS):
            raise ValueError('Question, prompt, token limit or domain settings differ.')
        keys = {m['key'] for m in manifest['models']}
        if seen_models & keys or len(keys) != len(manifest['models']):
            raise ValueError('Duplicate models: select only one run per model.')
        seen_models.update(keys)
        question_map = {q['id']: q['question'] for q in manifest['questions']}
        expected = {(key, qid) for key in keys for qid in question_map}
        rows = json.loads((path / 'results.json').read_text(encoding='utf-8'))
        actual = {(r['model_key'], r['question_id']) for r in rows}
        if actual != expected or len(rows) != len(expected):
            raise ValueError('Source run is incomplete or contains duplicate results.')
        for row in rows:
            if row['question'] != question_map[row['question_id']]:
                raise ValueError('Result question differs from its manifest.')
            raw = path / 'raw' / f"{row['model_key']}_{row['question_id']}.json"
            if not raw.exists():
                raise ValueError(f'Missing raw evidence: {raw.name}')
            records.append({**row, 'source_run': path.name})
            raw_files.append(raw)
        merged['models'].extend(manifest['models'])
        sources.append({'run_id': path.name, 'path': str(path),
                        'created_at': manifest['created_at'], 'run_hash': manifest['run_hash'],
                        'models': sorted(keys)})
    merged.update(report_only=True, source_runs=sources,
                  created_at=datetime.now().astimezone().isoformat())
    return merged, records, raw_files


def combine_runs(paths, output_root=None):
    manifest, records, raw_files = collect_runs(paths)
    output_root = Path(output_root) if output_root else ROOT / 'outputs/runs'
    out = output_root / ('combined_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    (out / 'raw').mkdir(parents=True, exist_ok=False)
    dump_json(out / 'manifest.json', manifest)
    for raw in raw_files:
        shutil.copy2(raw, out / 'raw' / raw.name)
    write_reports(out, manifest, records)
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', nargs='+', type=Path)
    args = parser.parse_args()
    try:
        print(combine_runs(args.runs))
    except ValueError as exc:
        parser.error(str(exc))
