import os
import re
import csv
from datetime import datetime

# --- Configuration ---
OUTPUTS_DIR = 'outputs'
CSV_REPORT_PATH = os.path.join(OUTPUTS_DIR, 'aiqa_report_data.csv')
# Regex to capture model name and date from the filename.
# It's designed to be flexible with model names.
FILENAME_PATTERN = re.compile(
    r'AQUASKY_AIQA_(?P<model_name>.+?)_(?P<date>\d{8})_\d{6}\.md$'
)

# Regex to find blocks of Question, Answer, and Token usage for each entry.
CONTENT_PATTERN = re.compile(
    r'\*\*問題 (?P<question_id>\d+):\*\*\s*(?P<question_text>[^\*]+?)\n+'
    r'\*\*回答\*\*:\s*(?P<answer_text>.+?)\n+'
    r'\*\*Token使用:\*\*\s*Input: (?P<input_tokens>\d+) / Output: (?P<output_tokens>\d+) / Total: (?P<total_tokens>\d+)',
    re.DOTALL
)

# Fallback: answer-only blocks when question/token markers are absent
ANSWER_ONLY_PATTERN = re.compile(
    r'\*\*回答\*\*:\s*(?P<answer_text>.+?)(?=(\n\*\*回答\*\*:|\Z))',
    re.DOTALL
)

# Section-based parsing: split by '## 問題 N' then extract fields within
SECTION_PATTERN = re.compile(
    r'^##\s*問題\s*(?P<qid>\d+)\s*\n(?P<section>.*?)(?=\n##\s*問題\s*\d+\s*\n|\Z)',
    re.DOTALL | re.MULTILINE
)
SECTION_QUESTION_LINE = re.compile(r'^\*\*問題\*\*:\s*(?P<q>.+)$', re.MULTILINE)
SECTION_ANSWER_START = re.compile(r'\*\*回答\*\*:\s*')
SECTION_TOKEN_LINE = re.compile(r'^\*\*Token使用\*\*:\s*Input:\s*(?P<input>\d+)\s*/\s*Output:\s*(?P<output>\d+)\s*/\s*Total:\s*(?P<total>\d+)', re.MULTILINE)

def parse_markdown_file(filepath):
    """Parses a single markdown report file to extract structured data."""
    print(f"[INFO] Processing file: {os.path.basename(filepath)}")
    match = FILENAME_PATTERN.match(os.path.basename(filepath))
    if not match:
        print(f"[WARN] Filename regex did not match for: {os.path.basename(filepath)}")
        return []

    data = match.groupdict()
    # Replace slashes in model names for cleaner CSV data, e.g., 'openai/gpt-4o-mini' -> 'openai_gpt-4o-mini'
    model_name = data['model_name'].replace('/', '_')
    report_date = datetime.strptime(data['date'], '%Y%m%d').strftime('%Y-%m-%d')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except IOError as e:
        print(f"[ERROR] Could not read file {filepath}: {e}")
        return []

    extracted_data = []

    # 1) Try section-based parsing first
    sections = list(SECTION_PATTERN.finditer(content))
    if sections:
        for sec in sections:
            qid = int(sec.group('qid'))
            sec_text = sec.group('section')
            # question line
            q_match = SECTION_QUESTION_LINE.search(sec_text)
            question_text = q_match.group('q').strip() if q_match else ''
            # answer block: from '**回答**:' to next separator or end of section
            a_start = SECTION_ANSWER_START.search(sec_text)
            answer_text = ''
            if a_start:
                start_idx = a_start.end()
                # stop at token line, next '## 問題', or a horizontal rule '---'
                stop_candidates = []
                token_m = SECTION_TOKEN_LINE.search(sec_text, pos=start_idx)
                if token_m:
                    stop_candidates.append(token_m.start())
                hr_idx = sec_text.find('\n---', start_idx)
                if hr_idx != -1:
                    stop_candidates.append(hr_idx)
                stop_idx = min(stop_candidates) if stop_candidates else len(sec_text)
                answer_text = sec_text[start_idx:stop_idx].strip()
            # token line (optional)
            token_line = SECTION_TOKEN_LINE.search(sec_text)
            in_tok = int(token_line.group('input')) if token_line else None
            out_tok = int(token_line.group('output')) if token_line else None
            tot_tok = int(token_line.group('total')) if token_line else None

            extracted_data.append({
                'date': report_date,
                'model_name': model_name,
                'question_id': qid,
                'question_text': question_text,
                'answer_text': answer_text,
                'input_tokens': in_tok,
                'output_tokens': out_tok,
                'total_tokens': tot_tok,
            })
    else:
        # 2) Fallback to strict structured pattern
        qa_blocks = list(CONTENT_PATTERN.finditer(content))
        if qa_blocks:
            for block in qa_blocks:
                block_data = block.groupdict()
                extracted_data.append({
                    'date': report_date,
                    'model_name': model_name,
                    'question_id': int(block_data['question_id']),
                    'question_text': block_data['question_text'].strip(),
                    'answer_text': block_data['answer_text'].strip(),
                    'input_tokens': int(block_data['input_tokens']),
                    'output_tokens': int(block_data['output_tokens']),
                    'total_tokens': int(block_data['total_tokens']),
                })
        else:
            # 3) Fallback to answer-only
            print(f"[INFO] Structured QA pattern not found; falling back to answer-only parsing for {os.path.basename(filepath)}")
            answers = list(ANSWER_ONLY_PATTERN.finditer(content))
            if not answers:
                print(f"[WARN] No '**回答**:' markers found in {os.path.basename(filepath)}")
            for idx, m in enumerate(answers, start=1):
                answer_text = m.group('answer_text').strip()
                extracted_data.append({
                    'date': report_date,
                    'model_name': model_name,
                    'question_id': idx,
                    'question_text': '',  # unknown in fallback
                    'answer_text': answer_text,
                    'input_tokens': None,
                    'output_tokens': None,
                    'total_tokens': None,
                })

    return extracted_data

def main():
    """Main function to generate the CSV report from markdown files."""
    all_data = []
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outputs_path = os.path.join(base_dir, OUTPUTS_DIR)

    if not os.path.isdir(outputs_path):
        print(f"[ERROR] Directory not found: {outputs_path}")
        return

    for filename in sorted(os.listdir(outputs_path)):
        if filename.endswith('.md'):
            filepath = os.path.join(outputs_path, filename)
            data = parse_markdown_file(filepath)
            if data:
                all_data.extend(data)

    if not all_data:
        print("[ERROR] No data was parsed from any file. Exiting.")
        return

    # Write to CSV
    csv_filepath = os.path.join(base_dir, CSV_REPORT_PATH)
    try:
        with open(csv_filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = [
                'date', 'model_name', 'question_id', 'question_text', 
                'answer_text', 'input_tokens', 'output_tokens', 'total_tokens'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data)
        print(f"\n[SUCCESS] CSV report generated successfully at: {csv_filepath}")
        print(f"Total records written: {len(all_data)}")
    except IOError as e:
        print(f"[ERROR] Could not write to CSV file {csv_filepath}: {e}")

if __name__ == '__main__':
    main()
