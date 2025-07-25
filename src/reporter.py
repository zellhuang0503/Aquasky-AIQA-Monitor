"""Generate Markdown and Excel reports for LLM responses."""
from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Dict, List

import pandas as _pd


def _timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def save_markdown(results: Dict[str, List[str]], questions: List[str], out_dir: Path) -> Path:
    """Save responses as a Markdown table.

    Parameters
    ----------
    results : Dict[str, List[str]]
        model -> list of answers (length == len(questions))
    questions : List[str]
        Original question list.
    out_dir : Path
        Directory to write file.
    Returns
    -------
    Path : generated markdown path
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"llm_responses_{_timestamp()}.md"

    headers = ["#", "Question"] + list(results.keys())
    lines = ["| " + " | ".join(headers) + " |",
             "| " + " | ".join(["---"] * len(headers)) + " |"]
    for idx, q in enumerate(questions, 1):
        row = [str(idx), q]
        for model in results:
            ans = results[model][idx - 1] if idx - 1 < len(results[model]) else ""
            row.append(ans.replace("\n", "<br>"))
        lines.append("| " + " | ".join(row) + " |")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def save_excel(results: Dict[str, List[str]], questions: List[str], out_dir: Path) -> Path:
    """Save responses to an Excel file using pandas."""
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _pd.DataFrame({"#": range(1, len(questions) + 1), "Question": questions})
    for model, answers in results.items():
        df[model] = answers
    xls_path = out_dir / f"llm_responses_{_timestamp()}.xlsx"
    df.to_excel(xls_path, index=False, engine="openpyxl")
    return xls_path


if __name__ == "__main__":
    # quick self-test demo
    qs = ["測試問題 1", "測試問題 2"]
    res = {"gpt-4o": ["答案 A1", "答案 A2"], "gemini": ["B1", "B2"]}
    out = Path("reports")
    print("Markdown:", save_markdown(res, qs, out))
    print("Excel:", save_excel(res, qs, out))
