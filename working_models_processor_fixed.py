#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AQUASKY AIQA Monitor - 已驗證可用模型處理器 (編碼修復版)
專注於已知可用的模型，避免卡在不可用的模型上
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

class WorkingModelsProcessor:
    """已驗證可用模型的處理器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.output_dir = self.project_root / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        # 已驗證可用的模型（根據用戶需求調整）
        self.working_models = [
            # 已成功測試過的模型
            {
                "id": "deepseek/deepseek-v3.1-base",
                "name": "DeepSeek v3.1 Base",
                "status": "verified"  # 已驗證可用
            },
            {
                "id": "openai/gpt-5-mini",
                "name": "GPT-5 Mini",
                "status": "verified"   # 已驗證可用
            },
            # 使用者要求移除 Claude 3 Haiku
            {
                "id": "google/gemini-flash-1.5",
                "name": "Gemini Flash 1.5",
                "status": "verified"   # 已驗證可用
            },
            # 其它已驗證可用的模型
            {
                "id": "anthropic/claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "status": "verified"   # 已驗證可用
            },
            {
                "id": "meta-llama/llama-3.1-8b-instruct",
                "name": "Llama 3.1 8B",
                "status": "verified"   # 已驗證可用
            },
            {
                "id": "mistralai/mistral-7b-instruct",
                "name": "Mistral 7B",
                "status": "verified"   # 已驗證可用
            },
            # 使用者指定必需的 Perplexity 模型（已驗證可用）
            {
                "id": "perplexity/sonar-pro",
                "name": "Perplexity Sonar Pro",
                "status": "verified",   # 已驗證可用
                "api_type": "perplexity"  # 使用 Perplexity 直接 API
            },
            # OpenRouter 可用的 Grok 模型（已測試 2025-07-26）
            {
                "id": "x-ai/grok-3-mini-beta",
                "name": "Grok 3 Mini Beta",
                "status": "verified"   # [VERIFIED] 已驗證可用，2.74秒回應（最快）
            },
        ]
        
        self.openrouter_api_key = None
        self.perplexity_api_key = None
        self.questions = []
        
    def load_config(self):
        """載入配置檔案"""
        print("\n[LOADING] 開始載入配置檔案...")
        config = configparser.ConfigParser()
        config_path = Path("config.ini")
        
        if not config_path.exists():
            print("[ERROR] 找不到 config.ini 檔案")
            return False
        
        config.read(config_path, encoding='utf-8')
        
        # 載入 OpenRouter API Key
        self.openrouter_api_key = config.get('api_keys', 'openrouter_api_key', fallback=None)
        
        # 載入 Perplexity API Key
        self.perplexity_api_key = config.get('api_keys', 'PERPLEXITY_API_KEY', fallback=None)
        
        if not self.openrouter_api_key or self.openrouter_api_key == 'your_openrouter_api_key_here':
            print("[ERROR] 請在 config.ini 中設定有效的 openrouter_api_key")
            return False
        
        if not self.perplexity_api_key or self.perplexity_api_key == 'your_perplexity_api_key_here':
            print("[ERROR] 請在 config.ini 中設定有效的 PERPLEXITY_API_KEY")
            return False
        
        return True
    
    def extract_questions(self):
        """從問題檔案中提取所有 20 個問題"""
        print("\n[LOADING] 開始提取問題...")
        questions_file = Path("AQUASKY AEO 監控專案 - 黃金問題庫 V2.0.md")
        
        if not questions_file.exists():
            print(f"[ERROR] 找不到問題檔案: {questions_file}")
            return False
        
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            questions = []
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, 21)):
                    question = line.split('.', 1)[1].strip()
                    if '(' in question and ')' in question:
                        question = question.split('(')[0].strip()
                    questions.append(question)
            
            self.questions = questions
            print(f"[SUCCESS] 成功提取 {len(questions)} 個問題")
            return len(questions) == 20
            
        except Exception as e:
            print(f"[ERROR] 讀取問題檔案時發生錯誤: {str(e)}")
            return False
    
    def test_model_availability(self, model_info):
        """測試模型是否可用（支援 OpenRouter 和 Perplexity）"""
        model_id = model_info["id"]
        api_type = model_info.get("api_type", "openrouter")
        
        print(f"\\n[TEST] 測試模型 {model_id} 是否可用...")
        
        if api_type == "perplexity":
            # 使用 Perplexity 直接 API
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            actual_model_id = model_id.replace("perplexity/", "")
        else:
            # 使用 OpenRouter API
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/zellhuang0503/Aquasky-AIQA-Monitor",
                "X-Title": "AQUASKY AIQA Monitor"
            }
            actual_model_id = model_id
        
        # 使用簡單的測試問題
        data = {
            "model": actual_model_id,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, please respond with 'OK' if you can understand this message."
                }
            ],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        try:
            print(f"  [TEST] 測試模型可用性...")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    print(f"  [SUCCESS] 模型可用")
                    return True
                else:
                    print(f"  [ERROR] 模型回應格式異常")
                    return False
            else:
                print(f"  [ERROR] 模型不可用 (HTTP {response.status_code})")
                try:
                    error_info = response.json()
                    print(f"      錯誤詳情: {error_info}")
                except:
                    print(f"      錯誤內容: {response.text}")
                return False
                
        except Exception as e:
            print(f"  [ERROR] 測試模型時發生錯誤: {str(e)}")
            return False
    
    def call_llm_api(self, model_info, question, question_num):
        """呼叫 LLM API（支援 OpenRouter 和 Perplexity）"""
        model_id = model_info["id"]
        api_type = model_info.get("api_type", "openrouter")
        
        if api_type == "perplexity":
            # 使用 Perplexity 直接 API
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            # Perplexity 模型 ID 需要移除 perplexity/ 前綴
            actual_model_id = model_id.replace("perplexity/", "")
        else:
            # 使用 OpenRouter API
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/zellhuang0503/Aquasky-AIQA-Monitor",
                "X-Title": "AQUASKY AIQA Monitor"
            }
            actual_model_id = model_id
        
        data = {
            "model": actual_model_id,
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
            print(f"  [PROCESSING] 處理問題 {question_num}/20...")
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    answer = result['choices'][0]['message']['content']
                    usage = result.get('usage', {})
                    
                    print(f"  [SUCCESS] 問題 {question_num} 完成 (Token: {usage.get('total_tokens', 0)})")
                    return {
                        'success': True,
                        'answer': answer,
                        'usage': usage
                    }
                else:
                    print(f"  [ERROR] 問題 {question_num} - API 回應格式異常")
                    return {'success': False, 'error': 'Invalid response format'}
            else:
                print(f"  [ERROR] 問題 {question_num} - API 錯誤: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                    
        except Exception as e:
            print(f"  [ERROR] 問題 {question_num} - 發生錯誤: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_single_model(self, model_info):
        """處理單一模型的所有問題"""
        model_id = model_info["id"]
        model_name = model_info["name"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"\\n[PROCESSING] 開始處理模型: {model_name} ({model_id})")
        
        print(f"\\n[MODEL] 開始處理模型: {model_name}")
        print(f"[ID] 模型ID: {model_id}")
        print("=" * 60)
        
        # 如果不是已驗證的模型，先測試可用性
        if model_info["status"] != "verified":
            if not self.test_model_availability(model_info):
                print(f"[ERROR] 模型 {model_name} 不可用，跳過處理")
                return False, 0, 0
        
        results = []
        successful_count = 0
        total_tokens = 0
        
        for i, question in enumerate(self.questions, 1):
            result = self.call_llm_api(model_info, question, i)
            results.append(result)
            
            if result['success']:
                successful_count += 1
                total_tokens += result.get('usage', {}).get('total_tokens', 0)
            
            # 每個問題之間暫停 3 秒
            if i < len(self.questions):
                time.sleep(3)
        
        # 儲存結果
        self.save_model_results(model_id, model_name, results, timestamp)
        
        print(f"\\n[RESULT] {model_name} 處理完成:")
        print(f"  [SUCCESS] 成功: {successful_count}/20 個問題")
        print(f"  [TOKENS] 總Token: {total_tokens}")
        print("=" * 60)
        
        return True, successful_count, total_tokens
    
    def save_model_results(self, model_id, model_name, results, timestamp):
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
        
        # 生成安全的檔案名稱
        safe_model_name = model_id.replace('/', '_').replace('\\\\', '_')
        
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
            f.write(f"**模型**: {model_id}\n")
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
        
        print(f"  [SAVED] 結果已儲存:")
        print(f"    Excel: {excel_filename}")
        print(f"    Markdown: {md_filename}")
    
    def run_processing(self):
        """執行處理"""
        print("[START] AQUASKY AIQA Monitor - 可用模型處理系統")
        print("=" * 60)
        
        # 載入配置
        if not self.load_config():
            return False
        
        # 提取問題
        if not self.extract_questions():
            return False
        
        print(f"\n[MODELS] 將依序處理以下模型:")
        for i, model in enumerate(self.working_models, 1):
            status_icon = "[VERIFIED]" if model["status"] == "verified" else "[TEST]"
            print(f"  {i}. {status_icon} {model['name']} ({model['id']})")
        
        print(f"\\n[INFO] 每個模型將處理 20 個問題，完成後自動儲存結果")
        print("=" * 60)
        
        # 開始處理每個模型
        total_successful = 0
        total_tokens = 0
        processed_models = 0
        
        for i, model_info in enumerate(self.working_models, 1):
            print(f"\\n[PROGRESS] 進度: {i}/{len(self.working_models)}")
            
            try:
                success, successful, tokens = self.process_single_model(model_info)
                
                if success:
                    processed_models += 1
                    total_successful += successful
                    total_tokens += tokens
                
                # 模型之間暫停 5 秒
                if i < len(self.working_models):
                    print(f"[PAUSE] 暫停 5 秒後處理下一個模型...")
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                print(f"\\n[INTERRUPTED] 使用者中斷處理，已完成 {processed_models} 個模型")
                break
            except Exception as e:
                print(f"\\n[ERROR] 處理模型 {model_info['name']} 時發生錯誤: {str(e)}")
                continue
        
        # 顯示總結
        print(f"\\n[COMPLETED] 處理完成！")
        print(f"[MODELS] 成功處理模型數: {processed_models}")
        print(f"[QUESTIONS] 總成功問題數: {total_successful}")
        print(f"[TOKENS] 總Token使用: {total_tokens}")
        print(f"[SAVED] 所有結果檔案已儲存至 outputs/ 目錄")
        print("=" * 60)
        
        return True

def main():
    """主程式"""
    print("===== 開始執行 working_models_processor_fixed.py =====")
    try:
        processor = WorkingModelsProcessor()
        processor.run_processing()
    except Exception as e:
        import traceback
        print(f"\\n[ERROR] 發生未捕獲的錯誤: {str(e)}")
        print("詳細錯誤追蹤:")
        traceback.print_exc()
    print("===== 腳本執行結束 =====")

if __name__ == "__main__":
    main()