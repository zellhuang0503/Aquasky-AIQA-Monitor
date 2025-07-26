#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AQUASKY AIQA Monitor - Perplexity 直接 API 測試腳本
使用 Perplexity 官方 API 而非 OpenRouter
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

class PerplexityDirectTest:
    """Perplexity 直接 API 測試器"""
    
    def __init__(self):
        print(f"📁 初始化 Perplexity 測試器 - 工作目錄: {Path.cwd()}")
        self.project_root = Path.cwd()
        self.output_dir = self.project_root / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        print(f"📂 輸出目錄: {self.output_dir}")
        
        # Perplexity 模型配置（使用正確的官方模型名稱）
        self.perplexity_models = [
            {
                "id": "llama-3.1-sonar-small-128k-online",
                "name": "Perplexity Sonar Small 128K",
                "api_endpoint": "https://api.perplexity.ai/chat/completions",
                "status": "primary"
            },
            {
                "id": "llama-3.1-sonar-large-128k-online",
                "name": "Perplexity Sonar Large 128K",
                "api_endpoint": "https://api.perplexity.ai/chat/completions",
                "status": "alternative"
            },
            {
                "id": "llama-3.1-sonar-huge-128k-online",
                "name": "Perplexity Sonar Huge 128K",
                "api_endpoint": "https://api.perplexity.ai/chat/completions",
                "status": "premium"
            },
            {
                "id": "sonar-small-online",
                "name": "Perplexity Sonar Small (Legacy)",
                "api_endpoint": "https://api.perplexity.ai/chat/completions",
                "status": "legacy"
            }
        ]
        
        self.openrouter_api_key = None
        self.perplexity_api_key = None
        self.questions = []
        
    def load_config(self):
        """載入配置檔案"""
        print("\n🔍 開始載入配置檔案...")
        config = configparser.ConfigParser()
        config_path = Path("config.ini")
        
        if not config_path.exists():
            print("❌ 找不到 config.ini 檔案")
            print("💡 請複製 config.ini.template 為 config.ini 並設定 API Keys")
            return False
        
        config.read(config_path, encoding='utf-8')
        
        # 調試輸出：顯示所有可用的 section 和 key
        print(f"🔍 配置檔案節區: {config.sections()}")
        if 'api_keys' in config.sections():
            print(f"🔑 api_keys 節區的所有鍵: {list(config['api_keys'].keys())}")
        
        # 載入 OpenRouter API Key
        self.openrouter_api_key = config.get('api_keys', 'OPENROUTER_API_KEY', fallback=None)
        print(f"🔍 OpenRouter API Key 讀取結果: {self.openrouter_api_key[:10] + '...' if self.openrouter_api_key and len(self.openrouter_api_key) > 10 else self.openrouter_api_key}")
        
        # 載入 Perplexity API Key
        self.perplexity_api_key = config.get('api_keys', 'PERPLEXITY_API_KEY', fallback=None)
        print(f"🔍 Perplexity API Key 讀取結果: {self.perplexity_api_key[:10] + '...' if self.perplexity_api_key and len(self.perplexity_api_key) > 10 else self.perplexity_api_key}")
        
        if not self.perplexity_api_key or self.perplexity_api_key == 'your_perplexity_api_key_here':
            print("❌ 請在 config.ini 中設定有效的 PERPLEXITY_API_KEY")
            print("💡 請到 https://www.perplexity.ai/ 註冊並取得 API Key")
            print("📝 請確認 config.ini 檔案中有以下格式:")
            print("[api_keys]")
            print("PERPLEXITY_API_KEY = your_actual_api_key_here")
            return False
        
        print("✅ 配置檔案載入成功")
        print(f"🔑 OpenRouter API Key: {'已設定' if self.openrouter_api_key else '未設定'}")
        print(f"🔑 Perplexity API Key: {'已設定' if self.perplexity_api_key else '未設定'}")
        return True
    
    def extract_questions(self):
        """從問題檔案中提取所有 20 個問題"""
        print("\n🔍 開始提取問題...")
        questions_file = Path("AQUASKY AEO 監控專案 - 黃金問題庫 V2.0.md")
        
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
    
    def find_working_perplexity_model(self):
        """尋找可用的 Perplexity 模型"""
        print(f"\n🧪 測試 Perplexity 模型可用性...")
        print(f"📋 將測試 {len(self.perplexity_models)} 個模型")
        
        for i, model in enumerate(self.perplexity_models, 1):
            print(f"\n🔄 測試模型 {i}/{len(self.perplexity_models)}: {model['name']}")
            print(f"🌐 API 端點: {model['api_endpoint']}")
            print(f"🤖 模型 ID: {model['id']}")
            
            if self.test_single_perplexity_model(model):
                print(f"✅ 找到可用的 Perplexity 模型: {model['name']}")
                return model
            else:
                print(f"❌ 模型 {model['name']} 不可用，嘗試下一個...")
        
        print("❌ 所有 Perplexity 模型都不可用")
        return None
    
    def test_single_perplexity_model(self, model):
        """測試單一 Perplexity 模型是否可用"""
        
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        
        # 使用簡單的測試問題
        data = {
            "model": model["id"],
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
            response = requests.post(
                model["api_endpoint"], 
                headers=headers, 
                json=data, 
                timeout=30
            )
            
            print(f"  📊 HTTP 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  📋 完整回應: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if 'choices' in result and len(result['choices']) > 0:
                    answer = result['choices'][0]['message']['content']
                    print(f"  ✅ 模型可用，回應: {answer}")
                    return True
                else:
                    print(f"  ❌ 模型回應格式異常")
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
    
    def call_perplexity_api(self, model, question, question_num):
        """呼叫 Perplexity API"""
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model["id"],
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
            response = requests.post(
                model["api_endpoint"], 
                headers=headers, 
                json=data, 
                timeout=60
            )
            
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
    
    def process_perplexity_model(self):
        """處理 Perplexity 模型的所有問題"""
        # 尋找可用的 Perplexity 模型
        working_model = self.find_working_perplexity_model()
        if not working_model:
            print(f"❌ 沒有可用的 Perplexity 模型，無法處理")
            return False, 0, 0
        
        # 使用找到的可用模型
        self.current_model = working_model
        model_name = working_model["name"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n{'='*80}")
        print(f"🤖 開始處理模型: {model_name}")
        print(f"📝 模型 ID: {working_model['id']}")
        print(f"🌐 API 端點: {working_model['api_endpoint']}")
        print(f"{'='*80}")
        
        print(f"\n✅ {model_name} 模型可用，開始處理 20 個問題...")
        
        results = []
        successful_count = 0
        total_tokens = 0
        
        for i, question in enumerate(self.questions, 1):
            result = self.call_perplexity_api(working_model, question, i)
            results.append(result)
            
            if result['success']:
                successful_count += 1
                total_tokens += result.get('usage', {}).get('total_tokens', 0)
            
            # 每個問題之間暫停 3 秒
            if i < len(self.questions):
                time.sleep(3)
        
        # 儲存結果
        self.save_results(working_model, model_name, results, timestamp)
        
        print(f"\n📊 {model_name} 處理完成:")
        print(f"  ✅ 成功: {successful_count}/20 個問題")
        print(f"  📈 總Token: {total_tokens}")
        print(f"{'='*80}")
        
        return True, successful_count, total_tokens
    
    def save_results(self, model, model_name, results, timestamp):
        """儲存結果"""
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
        
        # 生成檔案名稱
        safe_model_name = "perplexity_sonar_direct"
        
        # 儲存 Excel
        df = pd.DataFrame(data)
        excel_filename = f"AQUASKY_AIQA_{safe_model_name}_{timestamp}.xlsx"
        excel_path = self.output_dir / excel_filename
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        # 儲存 Markdown
        md_filename = f"AQUASKY_AIQA_{safe_model_name}_{timestamp}.md"
        md_path = self.output_dir / md_filename
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# AQUASKY AIQA Monitor - {model_name} 測試報告 (直接 API)\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**模型**: {model['id']}\n")
            f.write(f"**模型名稱**: {model_name}\n")
            f.write(f"**API 端點**: {model['api_endpoint']}\n\n")
            
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
        print("🚀 AQUASKY AIQA Monitor - Perplexity 直接 API 測試系統")
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
        
        print(f"\n📋 將測試 {len(self.perplexity_models)} 個 Perplexity 模型:")
        for i, model in enumerate(self.perplexity_models, 1):
            print(f"  {i}. 🔴 {model['name']} ({model['id']})")
        
        print(f"\n💡 將找到第一個可用的模型並處理 20 個問題，完成後自動儲存結果")
        print("=" * 80)
        
        # 處理 Perplexity 模型
        try:
            success, successful, tokens = self.process_perplexity_model()
            
            # 顯示總結
            print(f"\n🎉 Perplexity 測試完成！")
            if success:
                print(f"📊 成功處理: ✅")
                print(f"📈 成功問題數: {successful}/20")
                print(f"💰 總Token使用: {tokens}")
            else:
                print(f"📊 處理結果: ❌ 失敗")
            print(f"📁 結果檔案已儲存至 outputs/ 目錄")
            print("=" * 80)
            
            return success
                
        except KeyboardInterrupt:
            print(f"\n⏸️ 使用者中斷處理")
            return False
        except Exception as e:
            print(f"\n❌ 處理 Perplexity 模型時發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主程式"""
    print("===== 開始執行 Perplexity 直接 API 測試 =====")
    print(f"🕰️ 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 工作目錄: {Path.cwd()}")
    
    try:
        print("🚀 初始化 Perplexity 測試器...")
        tester = PerplexityDirectTest()
        print("✅ 測試器初始化成功")
        
        print("📝 開始執行 Perplexity 測試...")
        result = tester.run_test()
        print(f"🏁 測試結果: {'Success' if result else 'Failed'}")
        
    except Exception as e:
        import traceback
        print(f"\n❌❌❌ 發生未捕獲的錯誤: {str(e)}")
        print("詳細錯誤追蹤:")
        traceback.print_exc()
    
    print("===== Perplexity 測試執行結束 =====")
    print(f"🕰️ 結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
