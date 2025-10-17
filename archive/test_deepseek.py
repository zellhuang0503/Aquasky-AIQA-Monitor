#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenRouter Deepseek 測試腳本
專門用於測試 OpenRouter 的 Deepseek 模型是否正常工作
"""

import os
import sys
import json
import requests
import configparser
from datetime import datetime
from pathlib import Path

def load_config():
    """載入配置檔案"""
    config = configparser.ConfigParser()
    config_path = Path("config.ini")
    
    if not config_path.exists():
        print("❌ 找不到 config.ini 檔案")
        print("請先複製 config.ini.template 為 config.ini 並設定您的 API Key")
        return None
    
    config.read(config_path, encoding='utf-8')
    
    if 'api_keys' not in config:
        print("❌ config.ini 中找不到 [api_keys] 區段")
        return None
    
    api_key = config.get('api_keys', 'OPENROUTER_API_KEY', fallback=None)
    if not api_key or api_key == 'your_openrouter_api_key_here':
        print("❌ 請在 config.ini 中設定有效的 OPENROUTER_API_KEY")
        return None
    
    return api_key

def test_deepseek_api(api_key, test_question="你好，請簡單介紹一下你自己。"):
    """測試 OpenRouter Deepseek API"""
    
    print(f"🧪 開始測試 OpenRouter Deepseek 模型...")
    print(f"📝 測試問題: {test_question}")
    print("-" * 50)
    
    # API 設定
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-repo",  # 可選
        "X-Title": "AQUASKY AIQA Monitor"  # 可選
    }
    
    # 請求資料
    data = {
        "model": "deepseek/deepseek-chat",  # Deepseek 模型
        "messages": [
            {
                "role": "user",
                "content": test_question
            }
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        print("🔄 發送 API 請求...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 HTTP 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # 提取回答
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content']
                
                print("✅ API 測試成功！")
                print(f"🤖 Deepseek 回答:")
                print("-" * 30)
                print(answer)
                print("-" * 30)
                
                # 顯示使用統計
                if 'usage' in result:
                    usage = result['usage']
                    print(f"📈 Token 使用統計:")
                    print(f"   輸入 Token: {usage.get('prompt_tokens', 'N/A')}")
                    print(f"   輸出 Token: {usage.get('completion_tokens', 'N/A')}")
                    print(f"   總計 Token: {usage.get('total_tokens', 'N/A')}")
                
                return True, answer
            else:
                print("❌ API 回應格式異常，找不到回答內容")
                print(f"完整回應: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return False, None
                
        else:
            print(f"❌ API 請求失敗，狀態碼: {response.status_code}")
            try:
                error_info = response.json()
                print(f"錯誤詳情: {json.dumps(error_info, indent=2, ensure_ascii=False)}")
            except:
                print(f"錯誤內容: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print("❌ API 請求超時")
        return False, None
    except requests.exceptions.ConnectionError:
        print("❌ 網路連線錯誤")
        return False, None
    except Exception as e:
        print(f"❌ 發生未預期的錯誤: {str(e)}")
        return False, None

def save_test_result(success, answer, api_key_preview):
    """儲存測試結果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"deepseek_test_result_{timestamp}.json"
    filepath = Path("outputs") / filename
    
    # 確保輸出目錄存在
    filepath.parent.mkdir(exist_ok=True)
    
    result_data = {
        "timestamp": timestamp,
        "model": "deepseek/deepseek-chat",
        "api_key_preview": api_key_preview,
        "success": success,
        "answer": answer,
        "test_question": "你好，請簡單介紹一下你自己。"
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        print(f"📁 測試結果已儲存至: {filepath}")
    except Exception as e:
        print(f"⚠️ 儲存測試結果時發生錯誤: {str(e)}")

def main():
    """主程式"""
    print("🚀 OpenRouter Deepseek 測試工具")
    print("=" * 50)
    
    # 載入配置
    api_key = load_config()
    if not api_key:
        return
    
    # 顯示 API Key 預覽（隱藏大部分字元）
    api_key_preview = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"🔑 使用 API Key: {api_key_preview}")
    
    # 執行測試
    success, answer = test_deepseek_api(api_key)
    
    # 儲存結果
    save_test_result(success, answer, api_key_preview)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 測試完成！Deepseek 模型運作正常")
        print("💡 您現在可以使用批次處理系統來執行完整的問答任務")
        print("   執行指令: python src/main_batch.py")
    else:
        print("❌ 測試失敗！請檢查：")
        print("   1. API Key 是否正確且有效")
        print("   2. OpenRouter 帳戶是否有足夠餘額")
        print("   3. 網路連線是否正常")
        print("   4. 是否有其他 API 限制")

if __name__ == "__main__":
    main()
