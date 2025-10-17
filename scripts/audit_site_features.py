#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Site feature auditor: 檢查頁面是否已具備關鍵 SEO/AEO 標記

支援輸入：
- 本機 HTML 檔路徑，例如: outputs/html_snapshots/home_en.html
- 網站 URL，例如: https://aquaskyplus.com/

檢查項目：
- JSON-LD 結構化資料存在與類型（Organization/Brand/Product/FAQ/Breadcrumb）
- hreflang link 標記
- meta description / canonical
- GA4/gtag / Google Tag Manager 存在

輸出：人類可讀的摘要與機器可讀的 JSON 結果
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Dict, Any

try:
    import requests
except Exception:
    requests = None


def load_content(target: str) -> str:
    if target.startswith('http://') or target.startswith('https://'):
        if not requests:
            raise RuntimeError('未安裝 requests，無法抓取 URL')
        r = requests.get(target, timeout=20)
        r.raise_for_status()
        return r.text
    p = Path(target)
    return p.read_text(encoding='utf-8', errors='ignore')


def audit(html: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        'json_ld_types': [],
        'has_hreflang': False,
        'hreflang_locales': [],
        'has_meta_description': False,
        'has_canonical': False,
        'has_ga4_or_gtag': False,
        'has_gtm': False,
    }

    # JSON-LD blocks
    jsonld_blocks = re.findall(r'<script[^>]*type=["\\\']application/ld\+json["\\\'][^>]*>(.*?)</script>', html, re.I | re.S)
    types = []
    for block in jsonld_blocks:
        try:
            data = json.loads(block)
        except Exception:
            # 有時會有多個物件或註解，盡力拆解
            try:
                data = json.loads(block.strip().strip('\n'))
            except Exception:
                continue
        def collect_types(obj):
            if isinstance(obj, dict):
                t = obj.get('@type')
                if isinstance(t, str):
                    types.append(t)
                elif isinstance(t, list):
                    types.extend([x for x in t if isinstance(x, str)])
                for v in obj.values():
                    collect_types(v)
            elif isinstance(obj, list):
                for v in obj:
                    collect_types(v)
        collect_types(data)
    result['json_ld_types'] = sorted(set(types))

    # hreflang
    hreflang_links = re.findall(r'<link[^>]+rel=["\\\']alternate["\\\'][^>]+hreflang=["\\\']([^"\\\']+)["\\\']', html, re.I)
    result['has_hreflang'] = len(hreflang_links) > 0
    result['hreflang_locales'] = sorted(set(hreflang_links))

    # meta description / canonical
    result['has_meta_description'] = bool(re.search(r'<meta[^>]+name=["\\\']description["\\\']', html, re.I))
    result['has_canonical'] = bool(re.search(r'<link[^>]+rel=["\\\']canonical["\\\']', html, re.I))

    # GA4 / gtag / GTM
    result['has_ga4_or_gtag'] = bool(re.search(r'gtag\(', html, re.I) or re.search(r'G-[-A-Z0-9]{6,}', html))
    result['has_gtm'] = bool(re.search(r'googletagmanager\.com/gtm\.js', html, re.I) or re.search(r'GTM-[A-Z0-9]+', html))

    return result


def human_readable(result: Dict[str, Any]) -> str:
    lines = []
    lines.append('# Site Feature Audit\n')
    lines.append('## 結構化資料 (JSON-LD)\n')
    lines.append(f"- 類型：{', '.join(result['json_ld_types']) if result['json_ld_types'] else '未偵測到'}\n")
    lines.append('## 多語標記\n')
    lines.append(f"- hreflang：{'有' if result['has_hreflang'] else '無'}；Locales: {', '.join(result['hreflang_locales'])}\n")
    lines.append('## 基礎 SEO 標記\n')
    lines.append(f"- meta description：{'有' if result['has_meta_description'] else '無'}\n")
    lines.append(f"- canonical：{'有' if result['has_canonical'] else '無'}\n")
    lines.append('## 追蹤碼\n')
    lines.append(f"- GA4/gtag：{'有' if result['has_ga4_or_gtag'] else '無'}\n")
    lines.append(f"- GTM：{'有' if result['has_gtm'] else '無'}\n")
    lines.append('\n---\n')
    lines.append('```json\n')
    lines.append(json.dumps(result, ensure_ascii=False, indent=2))
    lines.append('\n```\n')
    return ''.join(lines)


def main():
    import argparse
    p = argparse.ArgumentParser(description='Audit site features from HTML or URL')
    p.add_argument('target', help='HTML 路徑或 URL')
    p.add_argument('-o', '--output', help='輸出 MD 檔（可選）')
    args = p.parse_args()

    html = load_content(args.target)
    res = audit(html)
    report = human_readable(res)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding='utf-8', newline='\n')
        print(f'已輸出：{out_path}')
    else:
        print(report)


if __name__ == '__main__':
    main()

