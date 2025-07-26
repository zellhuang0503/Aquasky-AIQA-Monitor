#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AQUASKY AIQA Monitor - 順序處理 LLM 腳本
每次只處理一個 LLM 模型的 20 個問題，完成並儲存後再進行下一個模型
避免 API 過於頻繁，提供更好的控制和穩定性
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

class SequentialLLMProcessor:
    """順序處理 LLM 的處理器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.output_dir = self.project_root / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        # 支援的 LLM 模型清單（已驗證可用）
        self.available_models = [
            "deepseek/deepseek-chat",           # DeepSeek Chat
            "anthropic/claude-3.5-sonnet",     # Claude 3.5 Sonnet
            "openai/gpt-4o-mini",              # GPT-4o Mini
            "google/gemini-flash-1.5",         # Gemini Flash 1.5
            "meta-llama/llama-3.1-8b-instruct", # Llama 3.1 8B
            "mistralai/mistral-7b-instruct",   # Mistral 7B
            "perplexity/sonar-pro",            # Perplexity Sonar Pro
            "x-ai/grok-3-mini-beta"            # Grok 3 Mini Beta (✅ 已驗證)
        ]
        
        # 模型顯示名稱
        self.model_display_names = {
            "deepseek/deepseek-chat": "DeepSeek Chat",
            "anthropic/claude-3.5-sonnet": "Claude 3.5 Sonnet",
            "openai/gpt-4o-mini": "GPT-4o Mini",
            "google/gemini-flash-1.5": "Gemini Flash 1.5",
            "meta-llama/llama-3.1-8b-instruct": "Llama 3.1 8B",
            "mistralai/mistral-7b-instruct": "Mistral 7B",
            "perplexity/sonar-pro": "Perplexity Sonar Pro",
            "x-ai/grok-4": "Grok 4",
            "x-ai/grok-3-mini-beta": "Grok 3 Mini Beta"
        }
        
        self.api_key = None
        self.questions = []
        
    def load_config(self):
        """載入配置檔案"""
        config = configparser.ConfigParser()
        config_path = Path("config.ini")
        
        if not config_path.exists():
            print("❌ 找不到 config.ini 檔案")
            return False
        
        config.read(config_path, encoding='utf-8')
        self.api_key = config.get('api_keys', 'OPENROUTER_API_KEY', fallback=None)
        
        if not self.api_key or self.api_key == 'your_openrouter_api_key_here':
            print("❌ 請在 config.ini 中設定有效的 OPENROUTER_API_KEY")
            return False
        
        return True
    
    def extract_questions(self):
        """從問題檔案中提取所有 20 個問題"""
        questions_file = Path("AQUASKY AEO 監控專案 - 黃金問題庫 V2.0.md")
        
        if not questions_file.exists():
            print(f"❌ 找不到問題檔案: {questions_file}")
            return False
        
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
            
            self.questions = questions
            print(f"✅ 成功提取 {len(questions)} 個問題")
            return len(questions) == 20
            
        except Exception as e:
            print(f"❌ 讀取問題檔案時發生錯誤: {str(e)}")
            return False
    
    def call_llm_api(self, model, question, question_num):
        """呼叫 LLM API"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/aquasky-aiqa-monitor",
            "X-Title": "AQUASKY AIQA Monitor"
        }
        
        data = {
            "model": model,
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
            print(f"  🔄 處理問題 {question_num}/20: {question[:50]}...")
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    answer = result['choices'][0]['message']['content']
                    usage = result.get('usage', {})
                    
                    print(f"  ✅ 問題 {question_num} 完成 (Token: {usage.get('total_tokens', 0)})")
                    return {
                        'success': True,
                        'answer': answer,
                        'usage': usage
                    }
                else:
                    print(f"  ❌ 問題 {question_num} - API 回應格式異常")
                    return {'success': False, 'error': 'Invalid response format'}
            else:
                print(f"  ❌ 問題 {question_num} - API 錯誤: {response.status_code}")
                try:
                    error_info = response.json()
                    return {'success': False, 'error': f'HTTP {response.status_code}: {error_info}'}
                except:
                    return {'success': False, 'error': f'HTTP {response.status_code}: {response.text}'}
                    
        except Exception as e:
            print(f"  ❌ 問題 {question_num} - 發生錯誤: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_single_model(self, model):
        """處理單一模型的所有問題"""
        model_name = self.model_display_names.get(model, model)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n🤖 開始處理模型: {model_name}")
        print(f"📝 模型ID: {model}")
        print("=" * 60)
        
        results = []
        successful_count = 0
        total_tokens = 0
        
        for i, question in enumerate(self.questions, 1):
            result = self.call_llm_api(model, question, i)
            results.append(result)
            
            if result['success']:
                successful_count += 1
                total_tokens += result.get('usage', {}).get('total_tokens', 0)
            
            # 每個問題之間暫停 3 秒，避免 API 限制
            if i < len(self.questions):
                time.sleep(3)
        
        # 儲存結果
        self.save_model_results(model, model_name, results, timestamp)
        
        print(f"\n📊 {model_name} 處理完成:")
        print(f"  ✅ 成功: {successful_count}/20 個問題")
        print(f"  📈 總Token: {total_tokens}")
        print("=" * 60)
        
        return successful_count, total_tokens
    
    def save_model_results(self, model, model_name, results, timestamp):
        """儲存單一模型的結果"""
        # 準備資料
        data = []
        
        for i, (question, result) in enumerate(zip(self.questions, results), 1):
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
        
        # 生成檔案名稱（使用安全的檔案名稱）
        safe_model_name = model.replace('/', '_').replace('\\', '_')
        
        # 儲存 Excel
        df = pd.DataFrame(data)
        excel_filename = f"AQUASKY_AIQA_{safe_model_name}_{timestamp}.xlsx"
        excel_path = self.output_dir / excel_filename
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        # 儲存 Markdown
        md_filename = f"AQUASKY_AIQA_{safe_model_name}_{timestamp}.md"
        md_path = self.output_dir / md_filename
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# AQUASKY AIQA Monitor - {model_name} 測試報告\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**模型**: {model}\n")
            f.write(f"**模型名稱**: {model_name}\n\n")
            
            # 統計資訊
            successful_count = sum(1 for r in results if r['success'])
            total_input_tokens = sum(r.get('usage', {}).get('prompt_tokens', 0) for r in results if r['success'])
            total_output_tokens = sum(r.get('usage', {}).get('completion_tokens', 0) for r in results if r['success'])
            
            f.write(f"## 統計資訊\n\n")
            f.write(f"- **成功問題數**: {successful_count}/20\n")
            f.write(f"- **總輸入Token**: {total_input_tokens}\n")
            f.write(f"- **總輸出Token**: {total_output_tokens}\n")
            f.write(f"- **總Token**: {total_input_tokens + total_output_tokens}\n\n")
            
            # 問題和回答
            for i, (question, result) in enumerate(zip(self.questions, results), 1):
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
        
        print(f"  📁 結果已儲存:")
        print(f"    Excel: {excel_filename}")
        print(f"    Markdown: {md_filename}")
    
    def run_sequential_processing(self):
        """執行順序處理"""
        print("🚀 AQUASKY AIQA Monitor - 順序 LLM 處理系統")
        print("=" * 60)
        
        # 載入配置
        if not self.load_config():
            return False
        
        # 提取問題
        if not self.extract_questions():
            return False
        
        print(f"\n📋 將依序處理 {len(self.available_models)} 個 LLM 模型:")
        for i, model in enumerate(self.available_models, 1):
            model_name = self.model_display_names.get(model, model)
            print(f"  {i}. {model_name} ({model})")
        
        print(f"\n💡 每個模型將處理 20 個問題，完成後自動儲存結果")
        print(f"⏱️ 預估總時間: 約 {len(self.available_models) * 20 * 3 / 60:.0f} 分鐘")
        print("=" * 60)
        
        # 詢問是否開始
        try:
            confirm = input("\n是否開始順序處理？(y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 使用者取消處理")
                return False
        except KeyboardInterrupt:
            print("\n❌ 使用者中斷處理")
            return False
        
        # 開始處理每個模型
        total_successful = 0
        total_tokens = 0
        
        for i, model in enumerate(self.available_models, 1):
            print(f"\n🔄 進度: {i}/{len(self.available_models)}")
            
            try:
                successful, tokens = self.process_single_model(model)
                total_successful += successful
                total_tokens += tokens
                
                # 模型之間暫停 5 秒
                if i < len(self.available_models):
                    print(f"⏸️ 暫停 5 秒後處理下一個模型...")
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                print(f"\n⏸️ 使用者中斷處理，已完成 {i-1} 個模型")
                break
            except Exception as e:
                print(f"\n❌ 處理模型 {model} 時發生錯誤: {str(e)}")
                continue
        
        # 顯示總結
        print(f"\n🎉 順序處理完成！")
        print(f"📊 總成功問題數: {total_successful}")
        print(f"📈 總Token使用: {total_tokens}")
        print(f"📁 所有結果檔案已儲存至 outputs/ 目錄")
        print("=" * 60)
        
        return True

def main():
    """主程式"""
    processor = SequentialLLMProcessor()
    processor.run_sequential_processing()

if __name__ == "__main__":
    main()
