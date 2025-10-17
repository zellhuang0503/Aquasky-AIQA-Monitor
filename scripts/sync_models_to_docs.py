#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步 config/working_models.json 到 README_BATCH.md 的「支援的 LLM 模型（代號）」清單。
"""
import json
from pathlib import Path


def load_models(json_path: Path):
    with open(json_path, 'r', encoding='utf-8') as f:
        models = json.load(f)
    assert isinstance(models, list)
    return models


def render_models_section(models):
    lines = ["## 支援的 LLM 模型（代號）\n"]
    for i, m in enumerate(models, start=1):
        name = m.get('name', '').strip()
        mid = m.get('id', '').strip()
        lines.append(f"{i}. {name} `{mid}`\n")
    lines.append("\n")
    return lines


def sync_readme(readme_path: Path, models):
    src = readme_path.read_text(encoding='utf-8')
    lines = src.splitlines(keepends=True)

    # 找到錨點「## 支援的 LLM 模型（代號）」
    start_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == "## 支援的 LLM 模型（代號）":
            start_idx = i
            break
    if start_idx is None:
        raise RuntimeError("找不到錨點：## 支援的 LLM 模型（代號）")

    # 向下尋找下一個 H2 「## 」作為結尾
    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        if lines[j].startswith('## '):
            end_idx = j
            break

    new_section = render_models_section(models)

    new_lines = lines[:start_idx] + new_section + lines[end_idx:]
    readme_path.write_text(''.join(new_lines), encoding='utf-8', newline='\n')


def main():
    repo_root = Path(__file__).resolve().parents[1]
    json_path = repo_root / 'config' / 'working_models.json'
    readme = repo_root / 'README_BATCH.md'

    if not json_path.exists():
        raise FileNotFoundError(f"找不到 {json_path}")
    if not readme.exists():
        raise FileNotFoundError(f"找不到 {readme}")

    models = load_models(json_path)
    sync_readme(readme, models)
    print("README_BATCH.md 模型清單已同步完成。")


if __name__ == '__main__':
    main()

