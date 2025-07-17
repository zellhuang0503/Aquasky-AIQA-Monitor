#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置檢查腳本 - 診斷 Open Router API Key 問題
此腳本會檢查：
1. config.ini 檔案是否存在
2. API Key 是否正確設定
3. API Key 是否有效
"""

import os
import configparser
from pathlib import Path
import requests

def check_config_file():
    """檢查 config.ini 檔案是否存在並可讀取"""
    print("=== 檢查 config.ini 檔案 ===")
    
    config_path = Path(__file__).parent / 'config.ini'
    print(f"配置檔案路徑: {config_path}")
    
    if not config_path.exists():
        print("❌ 錯誤：config.ini 檔案不存在！")
        print("解決方案：")
        print("1. 複製 config.ini.template 為 config.ini")
        print("2. 在 config.ini 中填入您的 OpenRouter API Key")
        return False
    
    print("✅ config.ini 檔案存在")
    return True

def check_api_key():
    """檢查 API Key 是否正確設定"""
    print("\n=== 檢查 API Key 設定 ===")
    
    try:
        config = configparser.ConfigParser()
        config_path = Path(__file__).parent / 'config.ini'
        config.read(config_path, encoding='utf-8')
        
        # 檢查 api_keys 區段是否存在
        if 'api_keys' not in config:
            print("❌ 錯誤：config.ini 中缺少 [api_keys] 區段")
            return None
        
        # 檢查 OPENROUTER_API_KEY 是否存在
        api_key = config.get('api_keys', 'OPENROUTER_API_KEY', fallback=None)
        
        if not api_key:
            print("❌ 錯誤：OPENROUTER_API_KEY 未設定")
            return None
        
        if api_key == 'your_openrouter_api_key_here':
            print("❌ 錯誤：OPENROUTER_API_KEY 仍為預設值，請填入真實的 API Key")
            return None
        
        # 檢查 API Key 格式（OpenRouter API Key 通常以 sk- 開頭）
        if not api_key.startswith('sk-'):
            print("⚠️  警告：API Key 格式可能不正確（通常以 'sk-' 開頭）")
        
        print(f"✅ API Key 已設定（前10字元：{api_key[:10]}...）")
        return api_key
        
    except Exception as e:
        print(f"❌ 讀取配置檔案時發生錯誤：{e}")
        return None

def test_api_key(api_key):
    """測試 API Key 是否有效"""
    print("\n=== 測試 API Key 有效性 ===")
    
    if not api_key:
        print("❌ 無法測試：API Key 未設定")
        return False
    
    try:
        # 使用 OpenRouter 的模型列表 API 來測試 Key 是否有效
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        print("正在測試 API Key...")
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ API Key 有效！")
            models = response.json()
            print(f"可用模型數量：{len(models.get('data', []))}")
            return True
        elif response.status_code == 401:
            print("❌ API Key 無效或已過期")
            print("請檢查您的 OpenRouter API Key 是否正確")
            return False
        else:
            print(f"❌ API 請求失敗，狀態碼：{response.status_code}")
            print(f"回應內容：{response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 請求超時，請檢查網路連線")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 網路請求錯誤：{e}")
        return False
    except Exception as e:
        print(f"❌ 測試過程中發生未預期錯誤：{e}")
        return False

def main():
    """主要檢查流程"""
    print("🔍 開始診斷 OpenRouter API Key 問題...\n")
    
    # 步驟 1：檢查配置檔案
    if not check_config_file():
        return
    
    # 步驟 2：檢查 API Key 設定
    api_key = check_api_key()
    
    # 步驟 3：測試 API Key 有效性
    if api_key:
        test_api_key(api_key)
    
    print("\n" + "="*50)
    print("診斷完成！")
    
    if not api_key:
        print("\n📋 解決步驟：")
        print("1. 前往 https://openrouter.ai/ 註冊帳號")
        print("2. 在 API Keys 頁面創建新的 API Key")
        print("3. 複製 config.ini.template 為 config.ini")
        print("4. 在 config.ini 中填入您的 API Key")
        print("5. 重新執行此檢查腳本")

if __name__ == "__main__":
    main()
