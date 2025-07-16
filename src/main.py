# -*- coding: utf-8 -*-
"""Main script for AQUASKY AIQA Monitor.

This script will:
1. Load questions from the golden query file.
2. Initialize LLM clients for target models.
3. Iterate through questions and get answers from each model.
4. Save the results into a structured format (e.g., CSV or Excel).
5. (Future) Schedule the script to run weekly.
"""

import os
import re
import time
from typing import List

def load_questions(file_path: str) -> List[str]:
    """Loads questions from the specified markdown file.

    Args:
        file_path: The path to the markdown file containing the questions.

    Returns:
        A list of questions as strings.
    """
    if not os.path.exists(file_path):
        print(f"Error: Question file not found at {file_path}")
        return []

    print(f"Loading questions from {file_path}...")
    questions = []
    # Regex to find lines starting with a number, a dot, and a space. e.g., "1. ..."
    question_pattern = re.compile(r"^\d+\.\s.*")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if question_pattern.match(line.strip()):
                    # Remove the leading number and dot, e.g., "1. "
                    question_text = re.sub(r"^\d+\.\s", "", line.strip())
                    questions.append(question_text)
        print(f"Successfully loaded {len(questions)} questions.")
        return questions
    except Exception as e:
        print(f"Error reading or parsing question file: {e}")
        return []

def main():
    """Main execution function."""
    print("Starting AQUASKY AIQA Monitor...")
    
    # --- 1. Load Questions ---
    # The question file is expected to be in the project root, one level above the 'src' directory.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    question_file = os.path.join(project_root, "AQUASKY AEO 監控專案 - 黃金問題庫 V2.0.md")
    questions = load_questions(question_file)

    if not questions:
        print("No questions loaded. Exiting.")
        return

    # --- 2. Initialize Models ---
    from llm_client import get_client, LLMError
    TARGET_MODELS = [
        "kimi-k2-free",
        "devstral-medium",
        "deepseek-chimera-free",
        "gemini-2.5-flash-lite",
        "grok-3",
        "claude-sonnet-4",
        "gpt-4o-mini-high",
        "perplexity-sonar-pro",
    ]
    print(f"\nTarget models: {', '.join(TARGET_MODELS)}")

    # --- 3. Run Q&A ---
    results = []
    for i, question in enumerate(questions):
        print(f"\n--- Processing Question {i+1}/{len(questions)} ---")
        print(f"Q: {question}")
        for model_name in TARGET_MODELS:
            print(f"  > Asking {model_name}...")
            try:
                client = get_client(model_name)
                # Format the question into the message structure the client expects
                messages = [
                    {"role": "system", "content": "You are a professional assistant for the water systems industry. Please respond exclusively in Traditional Chinese (請務必使用繁體中文回答)."},
                    {"role": "user", "content": question}
                ]
                answer = client.chat(messages)
                print(f"  < Answer from {model_name} received.")
                results.append({
                    "question_id": i + 1,
                    "question": question,
                    "model": model_name,
                    "answer": answer
                })
            except LLMError as e:
                print(f"  ! Error from {model_name}: {e}")
                results.append({
                    "question_id": i + 1,
                    "question": question,
                    "model": model_name,
                    "answer": f"ERROR: {e}"
                })
        # Add a delay to avoid hitting API rate limits
        print("  ... Pausing for 2 seconds ...")
        time.sleep(2)

    # --- 4. Save Results ---
    from report_generator import save_to_excel, save_to_markdown

    if results:
        output_dir = os.path.join(project_root, "outputs")
        save_to_excel(results, output_dir)
        save_to_markdown(results, output_dir)
    else:
        print("No results to save.")

    print("AQUASKY AIQA Monitor finished.")

if __name__ == "__main__":
    main()
