#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AQUASKY AIQA Monitor - 簡化數據收集器
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

class SimpleCollector:
    """簡化的數據收集器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.output_dir = self.project_root / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        # 簡化模型列表
        self.working_models = [
            {
                "id": "deepseek/deepseek-chat-v3.1:free",
                "name": "DeepSeek Chat v3.1 Free",
                "provider": "openrouter",
                "status": "verified"
            },
            {
                "id": "anthropic/claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet", 
                "provider": "openrouter",
                "status": "verified"
            },
            {
                "id": "google/gemini-flash-1.5",
                "name": "Gemini Flash 1.5",
                "provider": "openrouter", 
                "status": "verified"
            },
            {
                "id": "openai/gpt-5-mini",
                "name": "GPT-5 Mini",
                "provider": "openrouter",
                "status": "verified"
            }
        ]
        
        self.openrouter_api_key = None
        self.questions = []
        
    def load_config(self):
        """載入配置檔案"""
        print("LOADING: 載入配置檔案...")
        config = configparser.ConfigParser()
        config_path = Path("config.ini")
        
        if not config_path.exists():
            print("ERROR: 找不到 config.ini 檔案")
            return False
        
        try:
            config.read(config_path, encoding='utf-8')
            self.openrouter_api_key = config.get('api_keys', 'openrouter_api_key', fallback=None)
            
            if not self.openrouter_api_key or self.openrouter_api_key == 'your_openrouter_api_key_here':
                print("ERROR: 請在 config.ini 中設定有效的 openrouter_api_key")
                return False
                
            print("SUCCESS: 配置檔案載入成功")
            return True
        except Exception as e:
            print(f"ERROR: 載入配置檔案時發生錯誤: {str(e)}")
            return False
    
    def extract_questions(self):
        """從黃金問題庫提取問題"""
        print("LOADING: 提取問題...")
        questions_file = self.project_root / "AQUASKY AEO 監控專案 - 黃金問題庫 V3.0.md"
        
        if not questions_file.exists():
            print(f"ERROR: 找不到問題檔案: {questions_file}")
            return False
            
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            questions = []
            
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('1') or line.startswith('2')):
                    if '.' in line and len(line) > 10:
                        # 提取問題文字
                        parts = line.split('.', 1)
                        if len(parts) > 1:
                            question_text = parts[1].strip()
                            if question_text and len(question_text) > 10:
                                questions.append(question_text)
            
            self.questions = questions[:20]  # 限制為20個問題
            print(f"SUCCESS: 成功提取 {len(self.questions)} 個問題")
            return True
            
        except Exception as e:
            print(f"ERROR: 讀取問題檔案時發生錯誤: {str(e)}")
            return False
    
    def call_openrouter_api(self, model_id, question, question_num):
        """呼叫 OpenRouter API"""
        headers = {
            'Authorization': f'Bearer {self.openrouter_api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/anthropics/claude-code',
            'X-Title': 'AQUASKY AIQA Monitor'
        }
        
        data = {
            'model': model_id,
            'messages': [
                {
                    'role': 'user',
                    'content': question
                }
            ]
        }
        
        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    content = response_data['choices'][0]['message']['content']
                    usage = response_data.get('usage', {})
                    print(f"  SUCCESS: 問題 {question_num} 完成 (Token: {usage.get('total_tokens', 0)})")
                    return content, usage
                else:
                    print(f"  ERROR: 問題 {question_num} - API 回應格式異常")
                    return None, {}
            else:
                print(f"  ERROR: 問題 {question_num} - API 錯誤: {response.status_code}")
                return None, {}
                
        except Exception as e:
            print(f"  ERROR: 問題 {question_num} - 發生錯誤: {str(e)}")
            return None, {}
    
    def process_model(self, model_info):
        """處理單個模型"""
        model_id = model_info['id']
        model_name = model_info['name']
        
        print(f"\nPROCESSING: 開始處理模型: {model_name} ({model_id})")
        
        results = []
        successful_count = 0
        total_tokens = 0
        
        for i, question in enumerate(self.questions, 1):
            response_content, usage = self.call_openrouter_api(model_id, question, i)
            
            if response_content:
                successful_count += 1
                total_tokens += usage.get('total_tokens', 0)
                
                results.append({
                    '問題編號': i,
                    '問題': question,
                    '回答': response_content,
                    'Token使用量': usage.get('total_tokens', 0),
                    '完成時間': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            
            # 暫停避免API限制
            time.sleep(2)
        
        print(f"\nRESULT: {model_name} 處理完成:")
        print(f"  SUCCESS: {successful_count}/20 個問題")
        print(f"  TOKENS: {total_tokens}")
        
        # 儲存結果
        if results:
            self.save_results(model_name, model_id, results)
        
        return successful_count, total_tokens
    
    def save_results(self, model_name, model_id, results):
        """儲存結果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_model_name = model_id.replace('/', '_')
        
        # 儲存為 Excel
        excel_filename = f"AQUASKY_AIQA_{safe_model_name}_{timestamp}.xlsx"
        excel_path = self.output_dir / excel_filename
        
        df = pd.DataFrame(results)
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        # 儲存為 Markdown
        md_filename = f"AQUASKY_AIQA_{safe_model_name}_{timestamp}.md"
        md_path = self.output_dir / md_filename
        
        md_content = f"# AQUASKY AIQA 監控報告 - {model_name}\n\n"
        md_content += f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        md_content += f"**模型**: {model_name} ({model_id})\n"
        md_content += f"**處理問題數**: {len(results)}/20\n\n"
        
        for result in results:
            md_content += f"## 問題 {result['問題編號']}\n\n"
            md_content += f"**問題**: {result['問題']}\n\n"
            md_content += f"**回答**: {result['回答']}\n\n"
            md_content += f"**Token使用**: {result['Token使用量']}\n\n"
            md_content += "---\n\n"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"  SAVED: 結果已儲存:")
        print(f"    Excel: {excel_filename}")
        print(f"    Markdown: {md_filename}")
    
    def run_processing(self):
        """執行處理"""
        print("AQUASKY AIQA Monitor - 簡化數據收集系統")
        print("=" * 60)
        
        # 載入配置
        if not self.load_config():
            return False
        
        # 提取問題
        if not self.extract_questions():
            return False
        
        print(f"\n將依序處理以下模型:")
        for i, model in enumerate(self.working_models, 1):
            print(f"  {i}. {model['name']} ({model['id']})")
        
        print(f"\n每個模型將處理 20 個問題，完成後自動儲存結果")
        print("=" * 60)
        
        # 開始處理每個模型
        total_successful = 0
        total_tokens = 0
        processed_models = 0
        
        for model_info in self.working_models:
            try:
                successful, tokens = self.process_model(model_info)
                total_successful += successful
                total_tokens += tokens
                processed_models += 1
                
                # 模型間暫停
                if processed_models < len(self.working_models):
                    print(f"PAUSE: 暫停 5 秒後處理下一個模型...")
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                print(f"\nINTERRUPTED: 使用者中斷處理，已完成 {processed_models} 個模型")
                break
            except Exception as e:
                print(f"\nERROR: 處理模型 {model_info['name']} 時發生錯誤: {str(e)}")
                continue
        
        print(f"\nCOMPLETED: 處理完成！")
        print(f"MODELS: 成功處理模型數: {processed_models}")
        print(f"QUESTIONS: 總成功問題數: {total_successful}")
        print(f"TOKENS: 總Token使用: {total_tokens}")
        print(f"SAVED: 所有結果檔案已儲存至 outputs/ 目錄")
        
        return True

def main():
    print("===== 開始執行 simple_collector.py =====")
    try:
        collector = SimpleCollector()
        collector.run_processing()
    except Exception as e:
        import traceback
        print(f"\nERROR: 發生未捕獲的錯誤: {str(e)}")
        print("詳細錯誤追蹤:")
        traceback.print_exc()
    print("===== 腳本執行結束 =====")

if __name__ == "__main__":
    main()