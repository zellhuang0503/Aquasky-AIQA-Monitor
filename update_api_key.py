#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 API Key 並測試腳本
"""

import configparser
from pathlib import Path
import requests

def update_config_api_key():
    """更新配置檔案中的 API Key"""
    print("=== 更新 API Key 配置 ===")
    
    # 提示用戶輸入新的 API Key
    print("請從 OpenRouter 複製您的新 API Key")
    print("格式應該類似：sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    new_api_key = input("請貼上新的 API Key: ").strip()
    
    if not new_api_key:
        print("❌ 未輸入 API Key")
        return False
    
    if not new_api_key.startswith('sk-or-v1-'):
        print("⚠️  警告：API Key 格式可能不正確")
        confirm = input("是否繼續？(y/N): ").strip().lower()
        if confirm != 'y':
            return False
    
    try:
        # 讀取並更新配置檔案
        config = configparser.ConfigParser()
        config_path = Path(__file__).parent / 'config.ini'
        
        if config_path.exists():
            config.read(config_path, encoding='utf-8')
        
        # 確保 api_keys 區段存在
        if 'api_keys' not in config:
            config.add_section('api_keys')
        
        # 更新 API Key
        config.set('api_keys', 'OPENROUTER_API_KEY', new_api_key)
        
        # 確保 settings 區段存在
        if 'settings' not in config:
            config.add_section('settings')
            config.set('settings', 'HTTP_TIMEOUT', '60')
        
        # 寫入檔案
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
        
        print(f"✅ API Key 已更新到 {config_path}")
        return new_api_key
        
    except Exception as e:
        print(f"❌ 更新配置檔案時發生錯誤：{e}")
        return False

def test_new_api_key(api_key):
    """測試新的 API Key"""
    print("\n=== 測試新的 API Key ===")
    
    try:
        # 測試 API Key 有效性
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Zell-Huang/AQUASKY-AIQA-Monitor",
            "X-Title": "AQUASKY AIQA Monitor"
        }
        
        print("正在測試 API Key 有效性...")
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ API Key 有效！可用模型數量：{len(models.get('data', []))}")
            
            # 測試實際的聊天 API
            print("\n正在測試聊天 API...")
            chat_payload = {
                "model": "moonshotai/kimi-k2:free",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant. Please respond in Traditional Chinese."},
                    {"role": "user", "content": "請簡單說聲你好"}
                ],
                "max_tokens": 50,
                "temperature": 0.7,
                "stream": False
            }
            
            chat_response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=chat_payload,
                headers=headers,
                timeout=30
            )
            
            if chat_response.status_code == 200:
                data = chat_response.json()
                content = data["choices"][0]["message"]["content"]
                print(f"✅ 聊天 API 測試成功！")
                print(f"回應：{content}")
                return True
            else:
                print(f"❌ 聊天 API 測試失敗：{chat_response.status_code}")
                print(f"錯誤：{chat_response.text}")
                return False
                
        else:
            print(f"❌ API Key 無效，狀態碼：{response.status_code}")
            print(f"錯誤：{response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤：{e}")
        return False

def main():
    """主要流程"""
    print("🔧 OpenRouter API Key 更新與測試工具\n")
    
    # 步驟 1：更新 API Key
    new_api_key = update_config_api_key()
    
    if not new_api_key:
        print("❌ API Key 更新失敗")
        return
    
    # 步驟 2：測試新的 API Key
    if test_new_api_key(new_api_key):
        print("\n" + "="*50)
        print("🎉 恭喜！API Key 更新成功且測試通過！")
        print("\n現在可以執行主程式：")
        print("python src/main.py")
    else:
        print("\n" + "="*50)
        print("❌ API Key 測試失敗，請檢查：")
        print("1. API Key 是否正確複製")
        print("2. OpenRouter 帳戶是否有足夠餘額")
        print("3. API Key 是否有正確的權限設定")

if __name__ == "__main__":
    main()
