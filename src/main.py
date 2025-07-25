"""AQUASKY 自動黃金問題問答主程式

1. `python src/main.py --once`  立即執行一次並產生報告。
2. `python src/main.py`         常駐排程，每週一 09:00 執行。

程式流程：
    - 讀取黃金問題庫 Markdown
    - 依 MODEL_LIST 呼叫 LLM 取得回覆
    - 透過 reporter 產生 Markdown 與 Excel
    - 排程使用 schedule，每分鐘檢查一次

注意：需先設定 .env（OPENROUTER_API_KEY, GEMINI_API_KEY）。
"""
from __future__ import annotations

import argparse
import logging
import os
import time
from pathlib import Path
from typing import Dict, List

import schedule
from dotenv import load_dotenv

from question_loader import load_questions
from llm_client import get_client, LLMError
from reporter import save_excel, save_markdown

# ---------------------------- 基本設定 ----------------------------
ROOT = Path(__file__).resolve().parent.parent
QUESTION_MD = ROOT / "AQUASKY AEO 監控專案 - 黃金問題庫 V2.0.md"
REPORT_DIR = ROOT / "reports"

# 使用者指定模型
MODEL_LIST = [
    "gpt-4o",
    "gemini-1.5-pro-latest",
    # 以下模型名以 OpenRouter 支援為準
    "claude-3-sonnet-20240229",
    "mistral-large",
    "deepseek-chat",
    "grok-3",
    "kimi",
    "perplexity",
]

# --------------------------- logger ------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --------------------------- 核心函式 -----------------------------

def ask_all_models(questions: List[str]) -> Dict[str, List[str]]:
    """逐模型提問並收集回覆。"""
    results: Dict[str, List[str]] = {m: [] for m in MODEL_LIST}
    for model in MODEL_LIST:
        client = get_client(model)
        logger.info("→ %s 開始回答 …", model)
        for q in questions:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": q},
            ]
            try:
                ans = client.chat(messages, max_tokens=1024)
            except LLMError as e:
                logger.warning("%s 第一次失敗：%s，重試一次…", model, e)
                try:
                    ans = client.chat(messages, max_tokens=1024)
                except Exception as e2:
                    logger.error("%s 第二次失敗：%s，答案留空。", model, e2)
                    ans = ""
            results[model].append(ans)
    return results


def generate_reports() -> None:
    """單次完整流程：讀問題→問模型→寫報告"""
    logger.info("讀取問題庫…")
    questions = load_questions(QUESTION_MD)
    logger.info("共 %d 題。", len(questions))

    results = ask_all_models(questions)

    md_path = save_markdown(results, questions, REPORT_DIR)
    xls_path = save_excel(results, questions, REPORT_DIR)
    logger.info("✅ 報告完成 → %s, %s", md_path.name, xls_path.name)

# ---------------------------- 入口 -------------------------------

def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="AQUASKY Weekly LLM Q&A")
    parser.add_argument("--once", action="store_true", help="run once and exit")
    args = parser.parse_args()

    if args.once:
        generate_reports()
        return

    # 排程：每週一 09:00
    schedule.every().monday.at("09:00").do(generate_reports)
    logger.info("排程已啟動，每週一 09:00 自動產出報告… (Ctrl+C 結束)")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
