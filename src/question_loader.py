"""Utility to load golden questions from markdown file.

Assumes the markdown lists questions as numbered or bulleted items. Returns
List[str].
"""
from pathlib import Path
from typing import List
import re


MARKDOWN_LIST_PATTERN = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.*)$")


def load_questions(md_path: Path) -> List[str]:
    """Parse markdown file and extract question lines.

    Parameters
    ----------
    md_path : Path
        Path to markdown file containing the questions.

    Returns
    -------
    List[str]
        Extracted question strings in original order.
    """
    if not md_path.exists():
        raise FileNotFoundError(md_path)

    questions: List[str] = []
    with md_path.open(encoding="utf-8") as f:
        for line in f:
            m = MARKDOWN_LIST_PATTERN.match(line)
            if m:
                q = m.group(1).strip()
                if q:
                    questions.append(q)
    if not questions:
        raise ValueError("未能在檔案中解析出任何問題，請確認格式。")
    return questions


if __name__ == "__main__":
    path = Path(__file__).resolve().parent.parent / "AQUASKY AEO 監控專案 - 黃金問題庫 V2.0.md"
    for idx, q in enumerate(load_questions(path), 1):
        print(idx, q)
