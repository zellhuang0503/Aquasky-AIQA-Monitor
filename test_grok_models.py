#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grok 模型可用性測試腳本
測試 OpenRouter 中的 Grok 模型是否可以正常運作
"""

import os
import json
import requests
import configparser
import time
from datetime import datetime
from pathlib import Path

class GrokModelTester:
    """Grok 模型測試器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.output_dir = self.project_root / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        # 要測試的 Grok 模型
        self.grok_models = [
            {
                "id": "x-ai/grok-4",
                "name": "Grok 4",
                "description": "最新推理模型，支援多模態"
            },
            {
                "id": "x-ai/grok-beta",
                "name": "Grok Beta", 
                "description": "實驗性模型，先進推理能力"
            },
            {
                "id": "x-ai/grok-3-mini-beta",
                "name": "Grok 3 Mini Beta",
                "description": "輕量級思考型模型"
            }
        ]
        
        self.openrouter_api_key = None
        self.test_question = "請用繁體中文回答：什麼是人工智慧？請簡潔回答。"
        
    def load_config(self):
        """載入配置檔案"""
        print("🔍 載入配置檔案...")
        config = configparser.ConfigParser()
        config_path = Path("config.ini")
        
        if not config_path.exists():
            print("❌ 找不到 config.ini 檔案")
            return False
        
        config.read(config_path, encoding='utf-8')
        
        # 載入 OpenRouter API Key
        self.openrouter_api_key = config.get('api_keys', 'OPENROUTER_API_KEY', fallback=None)
        
        if not self.openrouter_api_key or self.openrouter_api_key == 'your_openrouter_api_key_here':
            print("❌ 請在 config.ini 中設定有效的 OPENROUTER_API_KEY")
            return False
        
        print("✅ 配置檔案載入成功")
        return True
    
    def test_single_model(self, model_info):
        """測試單一模型"""
        model_id = model_info["id"]
        model_name = model_info["name"]
        
        print(f"\n🧪 測試模型：{model_name} ({model_id})")
        
        # 準備 API 請求
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/zellhuang0503/Aquasky-AIQA-Monitor",
            "X-Title": "AQUASKY AIQA Monitor - Grok Test"
        }
        
        data = {
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": self.test_question
                }
            ],
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        try:
            print(f"   📡 發送 API 請求...")
            start_time = time.time()
            response = requests.post(url, headers=headers, json=data, timeout=30)
            end_time = time.time()
            
            response_time = round(end_time - start_time, 2)
            
            if response.status_code == 200:
                result = response.json()
                
                # 提取回應內容
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    
                    # 提取 token 使用量
                    usage = result.get('usage', {})
                    prompt_tokens = usage.get('prompt_tokens', 0)
                    completion_tokens = usage.get('completion_tokens', 0)
                    total_tokens = usage.get('total_tokens', 0)
                    
                    print(f"   ✅ 測試成功！")
                    print(f"   ⏱️  回應時間：{response_time} 秒")
                    print(f"   🎯 Token 使用：輸入 {prompt_tokens}，輸出 {completion_tokens}，總計 {total_tokens}")
                    print(f"   💬 回應內容：{content[:100]}...")
                    
                    return {
                        "success": True,
                        "model_id": model_id,
                        "model_name": model_name,
                        "response_time": response_time,
                        "tokens": {
                            "prompt": prompt_tokens,
                            "completion": completion_tokens,
                            "total": total_tokens
                        },
                        "content": content,
                        "error": None
                    }
                else:
                    print(f"   ❌ API 回應格式異常")
                    return {
                        "success": False,
                        "model_id": model_id,
                        "model_name": model_name,
                        "error": "API 回應格式異常"
                    }
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json()
                    if 'error' in error_detail:
                        error_msg += f": {error_detail['error'].get('message', '未知錯誤')}"
                except:
                    error_msg += f": {response.text[:200]}"
                
                print(f"   ❌ API 請求失敗：{error_msg}")
                return {
                    "success": False,
                    "model_id": model_id,
                    "model_name": model_name,
                    "error": error_msg
                }
                
        except requests.exceptions.Timeout:
            print(f"   ❌ 請求超時（30秒）")
            return {
                "success": False,
                "model_id": model_id,
                "model_name": model_name,
                "error": "請求超時"
            }
        except Exception as e:
            print(f"   ❌ 發生錯誤：{str(e)}")
            return {
                "success": False,
                "model_id": model_id,
                "model_name": model_name,
                "error": str(e)
            }
    
    def run_tests(self):
        """執行所有 Grok 模型測試"""
        print("🚀 開始 Grok 模型可用性測試")
        print(f"📝 測試問題：{self.test_question}")
        print("=" * 60)
        
        if not self.load_config():
            return False
        
        results = []
        successful_models = []
        failed_models = []
        
        for model_info in self.grok_models:
            result = self.test_single_model(model_info)
            results.append(result)
            
            if result["success"]:
                successful_models.append(result)
            else:
                failed_models.append(result)
            
            # 避免 API 限制，稍作延遲
            time.sleep(2)
        
        # 生成測試報告
        self.generate_report(results, successful_models, failed_models)
        
        return True
    
    def generate_report(self, results, successful_models, failed_models):
        """生成測試報告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("\n" + "=" * 60)
        print("📊 Grok 模型測試結果摘要")
        print("=" * 60)
        
        print(f"✅ 成功模型：{len(successful_models)} 個")
        for model in successful_models:
            print(f"   • {model['model_name']} - {model['response_time']}秒")
        
        print(f"\n❌ 失敗模型：{len(failed_models)} 個")
        for model in failed_models:
            print(f"   • {model['model_name']} - {model['error']}")
        
        # 儲存詳細報告到 JSON 檔案
        report_file = self.output_dir / f"grok_test_report_{timestamp}.json"
        report_data = {
            "test_timestamp": timestamp,
            "test_question": self.test_question,
            "total_models": len(results),
            "successful_count": len(successful_models),
            "failed_count": len(failed_models),
            "results": results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細報告已儲存至：{report_file}")
        
        # 生成 Markdown 報告
        self.generate_markdown_report(report_data, timestamp)
    
    def generate_markdown_report(self, report_data, timestamp):
        """生成 Markdown 格式報告"""
        md_file = self.output_dir / f"grok_test_report_{timestamp}.md"
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# Grok 模型可用性測試報告\n\n")
            f.write(f"**測試時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**測試問題：** {report_data['test_question']}\n\n")
            
            f.write(f"## 📊 測試摘要\n\n")
            f.write(f"- 總測試模型：{report_data['total_models']} 個\n")
            f.write(f"- 成功模型：{report_data['successful_count']} 個\n")
            f.write(f"- 失敗模型：{report_data['failed_count']} 個\n\n")
            
            f.write(f"## ✅ 成功模型詳情\n\n")
            for result in report_data['results']:
                if result['success']:
                    f.write(f"### {result['model_name']}\n")
                    f.write(f"- **模型 ID：** `{result['model_id']}`\n")
                    f.write(f"- **回應時間：** {result['response_time']} 秒\n")
                    f.write(f"- **Token 使用：** 輸入 {result['tokens']['prompt']}，輸出 {result['tokens']['completion']}，總計 {result['tokens']['total']}\n")
                    f.write(f"- **回應內容：** {result['content'][:200]}...\n\n")
            
            f.write(f"## ❌ 失敗模型詳情\n\n")
            for result in report_data['results']:
                if not result['success']:
                    f.write(f"### {result['model_name']}\n")
                    f.write(f"- **模型 ID：** `{result['model_id']}`\n")
                    f.write(f"- **錯誤原因：** {result['error']}\n\n")
        
        print(f"📄 Markdown 報告已儲存至：{md_file}")

def main():
    """主程式"""
    tester = GrokModelTester()
    tester.run_tests()

if __name__ == "__main__":
    main()
