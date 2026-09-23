"""Load question rows, preserving IDs, categories and exact wording."""
from pathlib import Path
import re


def load_question_records(md_path: Path) -> list[dict]:
    text = Path(md_path).read_text(encoding="utf-8-sig")
    rows = []
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if line.lstrip().startswith("|") and re.fullmatch(r"[AB]\d+", cells[0]):
            if len(cells) != 3 or not cells[1]:
                raise ValueError(f"Invalid question row: {cells[0]}")
            rows.append({"id": cells[0], "group": cells[0][0],
                         "question": cells[1], "purpose": cells[2]})
    if not rows:
        for line in text.splitlines():
            match = re.match(r"^\s*(\d+)\.\s+(.+)$", line)
            if match:
                rows.append({"id": match[1], "group": "legacy",
                             "question": match[2].strip(), "purpose": ""})
    if not rows:
        raise ValueError("No question rows found; expected A/B table rows or numbered questions.")
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate question IDs.")
    return rows


def load_questions(md_path: Path) -> list[str]:
    return [row["question"] for row in load_question_records(md_path)]
