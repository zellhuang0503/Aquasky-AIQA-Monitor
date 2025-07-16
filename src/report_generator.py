# -*- coding: utf-8 -*-
"""Module for generating reports from LLM query results."""

import os
from datetime import datetime
from typing import List, Dict

import pandas as pd


def save_to_excel(results: List[Dict], output_dir: str) -> None:
    """Saves the results to an Excel file.

    Args:
        results: A list of dictionaries, where each dict is a result.
        output_dir: The directory to save the report file in.
    """
    if not results:
        print("No results to save to Excel.")
        return

    print("Generating Excel report...")
    try:
        os.makedirs(output_dir, exist_ok=True)
        df = pd.DataFrame(results)
        # Reorder columns for better readability
        df = df[['question_id', 'question', 'model', 'answer']]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"AQUASKY_AIQA_Report_{timestamp}.xlsx"
        file_path = os.path.join(output_dir, file_name)

        df.to_excel(file_path, index=False, engine='openpyxl')
        print(f"Successfully saved Excel report to {file_path}")
    except Exception as e:
        print(f"Error saving Excel report: {e}")


def save_to_markdown(results: List[Dict], output_dir: str) -> None:
    """Saves the results to a Markdown file.

    Args:
        results: A list of dictionaries, where each dict is a result.
        output_dir: The directory to save the report file in.
    """
    if not results:
        print("No results to save to Markdown.")
        return

    print("Generating Markdown report...")
    try:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"AQUASKY_AIQA_Report_{timestamp}.md"
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# AQUASKY AIQA Monitor Report\n\n")
            f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

            # Group results by question
            grouped_results = {}
            for res in results:
                qid = res['question_id']
                if qid not in grouped_results:
                    grouped_results[qid] = []
                grouped_results[qid].append(res)

            for qid in sorted(grouped_results.keys()):
                question = grouped_results[qid][0]['question']
                f.write(f"## Question {qid}: {question}\n\n")
                for res in grouped_results[qid]:
                    f.write(f"### Answer from `{res['model']}`\n\n")
                    f.write(f"> {res['answer'].replace('\n', '\n> ')}\n\n")
                f.write("---\n\n")
        print(f"Successfully saved Markdown report to {file_path}")
    except Exception as e:
        print(f"Error saving Markdown report: {e}")
