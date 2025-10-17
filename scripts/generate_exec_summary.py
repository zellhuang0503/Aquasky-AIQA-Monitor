#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從現有 cross analysis 輸出產生「主管版交叉分析摘要」，聚焦 AEO/GEO 的可執行策略，
避免過度技術細節，適合高階主管閱讀。
"""
import re
from pathlib import Path
from datetime import datetime


def find_latest_cross_report(base: Path) -> Path:
    cand = list((base / 'outputs' / 'cross_analysis').glob('AEO_*analysis*.md'))
    if not cand:
        return None
    cand.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return cand[0]


def load_template(base: Path) -> str:
    tpl = base / 'templates' / 'exec_cross_analysis_template.md'
    return tpl.read_text(encoding='utf-8')


def extract_simple_highlights(text: str):
    # 粗略擷取三個重點（從原報告的前 3000 字中挑句號結束的三句）
    snippet = text[:3000]
    sentences = re.split(r'[。.!?]\s*', snippet)
    highlights = [s.strip() for s in sentences if len(s.strip()) > 12][:3]
    return highlights


def build_exec_report(base: Path, src: Path) -> str:
    tpl = load_template(base)
    raw = src.read_text(encoding='utf-8', errors='ignore')

    # 嘗試找出使用模型清單（若原報告中有列出）
    model_lines = []
    for line in raw.splitlines():
        if any(k in line.lower() for k in ['deepseek', 'gpt', 'gemini', 'claude', 'llama', 'mistral', 'grok', 'perplexity']):
            model_lines.append(line.strip())
    models = ', '.join(sorted(set(re.findall(r'([A-Za-z0-9][A-Za-z0-9\-\./]+)', ' '.join(model_lines))))) or '見原始報告'

    # 三大重點（非常粗略的句子擷取，後續可人工微調）
    hi = extract_simple_highlights(raw)
    summary = '\n  - ' + '\n  - '.join(hi) if hi else '\n  - （本期重點請補充）\n  - \n  - '

    out = tpl
    out = out.replace('{models}', models)
    out = out.replace('{date}', datetime.now().strftime('%Y-%m-%d'))
    out = out.replace('{reference}', src.name)
    out = out.replace('  - \n  - \n  - ', summary)
    return out


def main():
    base = Path(__file__).resolve().parents[1]
    src = find_latest_cross_report(base)
    if not src:
        raise SystemExit('找不到 cross analysis 報告（outputs/cross_analysis 目錄）。')

    exec_md = build_exec_report(base, src)
    out_dir = base / 'outputs' / 'cross_analysis'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"Exec_Summary_{datetime.now().strftime('%Y%m%d')}.md"
    out_path.write_text(exec_md, encoding='utf-8', newline='\n')
    print(f'已產生主管版摘要：{out_path}')


if __name__ == '__main__':
    main()

