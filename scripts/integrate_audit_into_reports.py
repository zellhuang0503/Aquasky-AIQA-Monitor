#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrate site audit results into executive summary report.

- Reads outputs/cross_analysis/home_audit.md (produced by audit_site_features.py)
- Extracts JSON block and computes a simple site-audit score (0-100)
  Scoring (each 20 pts): json-ld present, hreflang present, meta description,
  canonical, tracking (GA4/gtag or GTM). Partial if either gtag or GTM exists.
- Appends/updates a section in Exec_Summary_*.md with the score and key flags.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from datetime import datetime


def load_audit_json(md_path: Path) -> dict:
    text = md_path.read_text(encoding='utf-8', errors='ignore')
    m = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text)
    if not m:
        raise RuntimeError('找不到 JSON 稽核區塊')
    return json.loads(m.group(1))


def calc_score(a: dict) -> tuple[int, dict]:
    score = 0
    details = {}
    # json-ld
    has_jsonld = bool(a.get('json_ld_types'))
    score += 20 if has_jsonld else 0
    details['json_ld'] = has_jsonld
    # hreflang
    has_hreflang = bool(a.get('has_hreflang'))
    score += 20 if has_hreflang else 0
    details['hreflang'] = has_hreflang
    # meta description
    has_desc = bool(a.get('has_meta_description'))
    score += 20 if has_desc else 0
    details['meta_description'] = has_desc
    # canonical
    has_canon = bool(a.get('has_canonical'))
    score += 20 if has_canon else 0
    details['canonical'] = has_canon
    # tracking
    has_gtag = bool(a.get('has_ga4_or_gtag'))
    has_gtm = bool(a.get('has_gtm'))
    has_tracking = has_gtag or has_gtm
    score += 20 if has_tracking else 0
    details['tracking'] = {'ga4_or_gtag': has_gtag, 'gtm': has_gtm}
    return score, details


def update_exec_summary(exec_path: Path, score: int, details: dict):
    src = exec_path.read_text(encoding='utf-8', errors='ignore')
    block = [
        "## 站點稽核分數（整合）\n",
        f"- 本期站點稽核分數：{score}/100\n",
        f"- JSON‑LD：{'有' if details['json_ld'] else '無'}；hreflang：{'有' if details['hreflang'] else '無'}；meta description：{'有' if details['meta_description'] else '無'}；canonical：{'有' if details['canonical'] else '無'}；追蹤：{'有' if (details['tracking']['ga4_or_gtag'] or details['tracking']['gtm']) else '無'}\n",
        "\n",
    ]
    if '## 站點稽核分數（整合）' in src:
        # replace existing section
        pattern = r"## 站點稽核分數（整合）[\s\S]*?(?:\n## |\Z)"
        new_src = re.sub(pattern, ''.join(block) + "## ", src, count=1)
        if new_src.endswith('## '):
            new_src = new_src[:-3]
        exec_path.write_text(new_src, encoding='utf-8', newline='\n')
    else:
        # append near the top after Executive Summary
        if '## 一頁摘要' in src:
            parts = src.split('## 一頁摘要', 1)
            new_src = parts[0] + '## 一頁摘要' + parts[1] + '\n' + ''.join(block)
        else:
            new_src = src + '\n' + ''.join(block)
        exec_path.write_text(new_src, encoding='utf-8', newline='\n')


def main():
    base = Path(__file__).resolve().parents[1]
    audit_md = base / 'outputs' / 'cross_analysis' / 'home_audit.md'
    if not audit_md.exists():
        raise SystemExit('找不到 outputs/cross_analysis/home_audit.md，請先執行 audit_site_features.py')

    data = load_audit_json(audit_md)
    score, details = calc_score(data)

    # find latest exec summary
    exec_files = sorted((base / 'outputs' / 'cross_analysis').glob('Exec_Summary_*.md'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not exec_files:
        raise SystemExit('找不到 Exec_Summary_*.md')
    exec_path = exec_files[0]

    update_exec_summary(exec_path, score, details)
    print(f'已整合站點稽核分數：{exec_path} -> {score}/100')


if __name__ == '__main__':
    main()

