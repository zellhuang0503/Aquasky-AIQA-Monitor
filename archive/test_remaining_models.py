#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AQUASKY AIQA Monitor - 測試剩餘模型腳本
專門測試 Perplexity Sonar、Grok Beta、Grok 2 這三個模型
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

class RemainingModelsTest:
    """測試剩餘模型的處理器"""
    
    def __init__(self):
        print(f"📁 初始化測試器 - 工作目錄: {Path.cwd()}")
        self.project_root = Path.cwd()
        self.output_dir = self.project_root / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        print(f"📂 輸出目錄: {self.output_dir}")
        
        # 需要測試的三個模型
        self.test_models = [
            {
                "id": "perplexity/llama-3.1-sonar-small-128k-online",
                "name": "Perplexity Sonar",
                "status": "required"   # 必需模型
            },
            {
                "id": "x-ai/grok-beta",
                "name": "Grok Beta",
                "status": "testing"   # 待測試
            },
            {
                "id": "x-ai/grok-2",
                "name": "Grok 2",
                "status": "testing"   # 備用 Grok 模型
            }
        ]
        
        self.api_key = None
        self.questions = []
        
    def load_config(self):
        """載入配置檔案"""
        print("\n🔍 開始載入配置檔案...")
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
        
        print("✅ 配置檔案載入成功")
        return True
    
    def extract_questions(self):
        """從問題檔案中提取所有 20 個問題"""
        print("\n🔍 開始提取問題...")
        questions_file = Path("AQUASKY AEO 監控專案 - 黃金問題庫 V3.0.md")
        
        if not questions_file.exists():
            print(f"❌ 找不到問題檔案: {questions_file}")
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
            print(f"✅ 成功提取 {len(questions)} 個問題")
            return len(questions) == 20
            
        except Exception as e:
            print(f"❌ 讀取問題檔案時發生錯誤: {str(e)}")
            return False
    
    def test_model_availability(self, model_id):
        """測試模型是否可用"""
        print(f"\n🧪 測試模型 {model_id} 是否可用...")
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/aquasky-aiqa-monitor",
            "X-Title": "AQUASKY AIQA Monitor"
        }
        
        # 使用簡單的測試問題
        data = {
            "model": model_id,
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
            print(f"  🔄 發送測試請求...")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            print(f"  📊 HTTP 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    answer = result['choices'][0]['message']['content']
                    print(f"  ✅ 模型可用，回應: {answer}")
                    return True
                else:
                    print(f"  ❌ 模型回應格式異常: {result}")
                    return False
            else:
                print(f"  ❌ 模型不可用 (HTTP {response.status_code})")
                try:
                    error_info = response.json()
                    print(f"      錯誤詳情: {json.dumps(error_info, indent=2, ensure_ascii=False)}")
                except:
                    print(f"      錯誤內容: {response.text}")
                return False
                
        except Exception as e:
            print(f"  ❌ 測試模型時發生錯誤: {str(e)}")
            return False
    
    def call_llm_api(self, model_id, question, question_num):
        """呼叫 LLM API"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/aquasky-aiqa-monitor",
            "X-Title": "AQUASKY AIQA Monitor"
        }
        
        data = {
            "model": model_id,
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
            print(f"  🔄 處理問題 {question_num}/20...")
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
                    print(f"      錯誤詳情: {json.dumps(error_info, indent=2, ensure_ascii=False)}")
                    return {'success': False, 'error': f'HTTP {response.status_code}: {error_info}'}
                except:
                    return {'success': False, 'error': f'HTTP {response.status_code}: {response.text}'}
                    
        except Exception as e:
            print(f"  ❌ 問題 {question_num} - 發生錯誤: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_single_model(self, model_info):
        """處理單一模型的所有問題"""
        model_id = model_info["id"]
        model_name = model_info["name"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n{'='*80}")
        print(f"🤖 開始處理模型: {model_name}")
        print(f"📝 模型ID: {model_id}")
        print(f"🔖 狀態: {model_info['status']}")
        print(f"{'='*80}")
        
        # 先測試模型可用性
        if not self.test_model_availability(model_id):
            print(f"❌ 模型 {model_name} 不可用，跳過處理")
            return False, 0, 0
        
        print(f"\n✅ 模型 {model_name} 可用，開始處理 20 個問題...")
        
        results = []
        successful_count = 0
        total_tokens = 0
        
        for i, question in enumerate(self.questions, 1):
            result = self.call_llm_api(model_id, question, i)
            results.append(result)
            
            if result['success']:
                successful_count += 1
                total_tokens += result.get('usage', {}).get('total_tokens', 0)
            
            # 每個問題之間暫停 3 秒
            if i < len(self.questions):
                time.sleep(3)
        
        # 儲存結果
        self.save_model_results(model_id, model_name, results, timestamp)
        
        print(f"\n📊 {model_name} 處理完成:")
        print(f"  ✅ 成功: {successful_count}/20 個問題")
        print(f"  📈 總Token: {total_tokens}")
        print(f"{'='*80}")
        
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
        safe_model_name = model_id.replace('/', '_').replace('\\', '_')
        
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
        
        print(f"  📁 結果已儲存:")
        print(f"    Excel: {excel_filename}")
        print(f"    Markdown: {md_filename}")
    
    def run_test(self):
        """執行測試"""
        print("🚀 AQUASKY AIQA Monitor - 剩餘模型測試系統")
        print("=" * 80)
        print(f"🕰️ 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 載入配置
        print("🔄 步驟 1: 載入配置檔案")
        if not self.load_config():
            print("❌ 載入配置失敗")
            return False
        
        # 提取問題
        print("🔄 步驟 2: 提取問題")
        if not self.extract_questions():
            print("❌ 提取問題失敗")
            return False
        
        print(f"\n📋 將測試以下 {len(self.test_models)} 個模型:")
        for i, model in enumerate(self.test_models, 1):
            status_icon = "🔴" if model["status"] == "required" else "🧪"
            print(f"  {i}. {status_icon} {model['name']} ({model['id']})")
        
        print(f"\n💡 每個模型將處理 20 個問題，完成後自動儲存結果")
        print("=" * 80)
        
        # 開始處理每個模型
        total_successful = 0
        total_tokens = 0
        processed_models = 0
        
        for i, model_info in enumerate(self.test_models, 1):
            print(f"\n🔄 進度: {i}/{len(self.test_models)}")
            
            try:
                success, successful, tokens = self.process_single_model(model_info)
                
                if success:
                    processed_models += 1
                    total_successful += successful
                    total_tokens += tokens
                
                # 模型之間暫停 10 秒（增加暫停時間避免頻率限制）
                if i < len(self.test_models):
                    print(f"⏸️ 暫停 10 秒後處理下一個模型...")
                    time.sleep(10)
                    
            except KeyboardInterrupt:
                print(f"\n⏸️ 使用者中斷處理，已完成 {processed_models} 個模型")
                break
            except Exception as e:
                print(f"\n❌ 處理模型 {model_info['name']} 時發生錯誤: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        # 顯示總結
        print(f"\n🎉 測試完成！")
        print(f"📊 成功處理模型數: {processed_models}")
        print(f"📈 總成功問題數: {total_successful}")
        print(f"💰 總Token使用: {total_tokens}")
        print(f"📁 所有結果檔案已儲存至 outputs/ 目錄")
        print("=" * 80)
        
        return True

def main():
    """主程式"""
    print("===== 開始執行剩餘模型測試 =====")
    print(f"🕰️ 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 工作目錄: {Path.cwd()}")
    
    try:
        print("🚀 初始化測試器...")
        tester = RemainingModelsTest()
        print("✅ 測試器初始化成功")
        
        print("📝 開始執行測試...")
        result = tester.run_test()
        print(f"🏁 測試結果: {'Success' if result else 'Failed'}")
        
    except Exception as e:
        import traceback
        print(f"\n❌❌❌ 發生未捕獲的錯誤: {str(e)}")
        print("詳細錯誤追蹤:")
        traceback.print_exc()
    
    print("===== 測試執行結束 =====")
    print(f"🕰️ 結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
