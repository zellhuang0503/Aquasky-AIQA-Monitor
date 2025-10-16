#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的 Deepseek 批次處理腳本
直接處理所有 20 個問題，避開複雜的批次處理系統
"""

import os
import sys
import json
import requests
import configparser
import time
from datetime import datetime
from pathlib import Path
import pandas as pd

def load_config():
    """載入配置檔案"""
    config = configparser.ConfigParser()
    config_path = Path("config.ini")
    
    if not config_path.exists():
        print("❌ 找不到 config.ini 檔案")
        return None
    
    config.read(config_path, encoding='utf-8')
    api_key = config.get('api_keys', 'OPENROUTER_API_KEY', fallback=None)
    
    if not api_key or api_key == 'your_openrouter_api_key_here':
        print("❌ 請在 config.ini 中設定有效的 OPENROUTER_API_KEY")
        return None
    
    return api_key

def extract_questions():
    """從問題檔案中提取所有 20 個問題"""
    questions_file = Path("AQUASKY AEO 監控專案 - 黃金問題庫 V3.0.md")
    
    if not questions_file.exists():
        print(f"❌ 找不到問題檔案: {questions_file}")
        return []
    
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 手動提取所有 20 個問題
        questions = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # 尋找以數字開頭的問題行
            if line and any(line.startswith(f"{i}.") for i in range(1, 21)):
                # 移除問題編號，只保留問題內容
                question = line.split('.', 1)[1].strip()
                # 移除英文翻譯部分（括號內容）
                if '(' in question and ')' in question:
                    question = question.split('(')[0].strip()
                questions.append(question)
        
        print(f"✅ 成功提取 {len(questions)} 個問題")
        return questions
        
    except Exception as e:
        print(f"❌ 讀取問題檔案時發生錯誤: {str(e)}")
        return []

def call_deepseek_api(api_key, question, question_num):
    """呼叫 Deepseek API"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-repo",
        "X-Title": "AQUASKY AIQA Monitor"
    }
    
    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        print(f"🔄 處理問題 {question_num}/20...")
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content']
                usage = result.get('usage', {})
                
                print(f"✅ 問題 {question_num} 完成")
                return {
                    'success': True,
                    'answer': answer,
                    'usage': usage
                }
            else:
                print(f"❌ 問題 {question_num} - API 回應格式異常")
                return {'success': False, 'error': 'Invalid response format'}
        else:
            print(f"❌ 問題 {question_num} - API 錯誤: {response.status_code}")
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        print(f"❌ 問題 {question_num} - 發生錯誤: {str(e)}")
        return {'success': False, 'error': str(e)}

def save_results(questions, results, timestamp):
    """儲存結果到 Excel 和 Markdown"""
    # 確保輸出目錄存在
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # 準備資料
    data = []
    total_input_tokens = 0
    total_output_tokens = 0
    successful_questions = 0
    
    for i, (question, result) in enumerate(zip(questions, results), 1):
        row = {
            '問題編號': i,
            '問題': question,
            '回答': result.get('answer', '處理失敗') if result['success'] else '處理失敗',
            '狀態': '成功' if result['success'] else '失敗',
            '錯誤訊息': result.get('error', '') if not result['success'] else '',
            '輸入Token': result.get('usage', {}).get('prompt_tokens', 0) if result['success'] else 0,
            '輸出Token': result.get('usage', {}).get('completion_tokens', 0) if result['success'] else 0,
            '總Token': result.get('usage', {}).get('total_tokens', 0) if result['success'] else 0
        }
        data.append(row)
        
        if result['success']:
            successful_questions += 1
            total_input_tokens += row['輸入Token']
            total_output_tokens += row['輸出Token']
    
    # 儲存 Excel
    df = pd.DataFrame(data)
    excel_filename = f"AQUASKY_AIQA_deepseek_chat_{timestamp}.xlsx"
    excel_path = output_dir / excel_filename
    df.to_excel(excel_path, index=False, engine='openpyxl')
    
    # 儲存 Markdown
    md_filename = f"AQUASKY_AIQA_deepseek_chat_{timestamp}.md"
    md_path = output_dir / md_filename
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# AQUASKY AIQA Monitor - Deepseek Chat 測試報告\n\n")
        f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**模型**: deepseek/deepseek-chat\n")
        f.write(f"**成功問題數**: {successful_questions}/20\n")
        f.write(f"**總輸入Token**: {total_input_tokens}\n")
        f.write(f"**總輸出Token**: {total_output_tokens}\n")
        f.write(f"**總Token**: {total_input_tokens + total_output_tokens}\n\n")
        
        for i, (question, result) in enumerate(zip(questions, results), 1):
            f.write(f"## 問題 {i}\n\n")
            f.write(f"**問題**: {question}\n\n")
            if result['success']:
                f.write(f"**回答**: {result['answer']}\n\n")
                usage = result.get('usage', {})
                f.write(f"**Token使用**: 輸入 {usage.get('prompt_tokens', 0)}, 輸出 {usage.get('completion_tokens', 0)}, 總計 {usage.get('total_tokens', 0)}\n\n")
            else:
                f.write(f"**狀態**: 處理失敗\n")
                f.write(f"**錯誤**: {result.get('error', '未知錯誤')}\n\n")
            f.write("---\n\n")
    
    print(f"📁 結果已儲存:")
    print(f"   Excel: {excel_path}")
    print(f"   Markdown: {md_path}")
    
    return successful_questions, total_input_tokens + total_output_tokens

def main():
    """主程式"""
    print("🚀 AQUASKY AIQA Monitor - Deepseek 簡化批次處理")
    print("=" * 60)
    
    # 載入配置
    api_key = load_config()
    if not api_key:
        return
    
    # 提取問題
    questions = extract_questions()
    if not questions:
        return
    
    if len(questions) != 20:
        print(f"⚠️ 警告：預期 20 個問題，但只找到 {len(questions)} 個問題")
    
    # 顯示問題預覽
    print(f"\n📋 將處理以下 {len(questions)} 個問題:")
    for i, q in enumerate(questions[:3], 1):
        print(f"  {i}. {q[:50]}...")
    if len(questions) > 3:
        print(f"  ... 還有 {len(questions) - 3} 個問題")
    
    print(f"\n🤖 使用模型: deepseek/deepseek-chat")
    print("=" * 60)
    
    # 開始處理
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []
    
    for i, question in enumerate(questions, 1):
        result = call_deepseek_api(api_key, question, i)
        results.append(result)
        
        # 每個問題之間暫停 2 秒，避免 API 限制
        if i < len(questions):
            time.sleep(2)
    
    # 儲存結果
    successful_count, total_tokens = save_results(questions, results, timestamp)
    
    # 顯示總結
    print("\n" + "=" * 60)
    print("🎉 批次處理完成！")
    print(f"📊 成功處理: {successful_count}/{len(questions)} 個問題")
    print(f"📈 總Token使用: {total_tokens}")
    print(f"📁 結果檔案已儲存至 outputs/ 目錄")
    print("=" * 60)

if __name__ == "__main__":
    main()
