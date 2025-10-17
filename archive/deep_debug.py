#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度診斷腳本 - 逐步檢查每個環節
"""

import sys
import os
import requests
import configparser
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_direct_api_call():
    """直接測試 OpenRouter API 呼叫，不透過我們的客戶端"""
    print("=== 直接測試 OpenRouter API ===")
    
    try:
        # 直接讀取 API Key
        config = configparser.ConfigParser()
        config_path = Path(__file__).parent / 'config.ini'
        config.read(config_path, encoding='utf-8')
        api_key = config.get('api_keys', 'OPENROUTER_API_KEY')
        
        print(f"使用 API Key: {api_key[:10]}...")
        
        # 直接呼叫 OpenRouter API
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Zell-Huang/AQUASKY-AIQA-Monitor",
            "X-Title": "AQUASKY AIQA Monitor"
        }
        
        payload = {
            "model": "moonshotai/kimi-k2:free",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Please respond in Traditional Chinese."},
                {"role": "user", "content": "請簡單介紹一下自己"}
            ],
            "max_tokens": 100,
            "temperature": 0.7,
            "stream": False
        }
        
        print("正在發送直接 API 請求...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"狀態碼: {response.status_code}")
        print(f"回應 headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            print(f"✅ 直接 API 呼叫成功！")
            print(f"回應內容: {content[:100]}...")
            return True
        else:
            print(f"❌ 直接 API 呼叫失敗")
            print(f"錯誤內容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 直接 API 呼叫發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_our_client():
    """測試我們的客戶端實作"""
    print("\n=== 測試我們的客戶端實作 ===")
    
    try:
        from llm_client import OpenRouterChatClient
        
        # 直接創建客戶端實例
        client = OpenRouterChatClient("moonshotai/kimi-k2:free")
        
        print(f"客戶端 API Key: {client.api_key[:10]}...")
        print(f"客戶端模型: {client.model}")
        
        # 測試請求
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Please respond in Traditional Chinese."},
            {"role": "user", "content": "請簡單介紹一下自己"}
        ]
        
        print("正在透過客戶端發送請求...")
        response = client.chat(messages)
        
        print(f"✅ 客戶端請求成功！")
        print(f"回應內容: {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ 客戶端請求失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_factory_function():
    """測試工廠函數"""
    print("\n=== 測試工廠函數 ===")
    
    try:
        from llm_client import get_client
        
        client = get_client("kimi-k2-free")
        print(f"工廠函數返回的客戶端類型: {type(client).__name__}")
        print(f"模型: {client.model}")
        print(f"API Key: {client.api_key[:10]}...")
        
        # 測試請求
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Please respond in Traditional Chinese."},
            {"role": "user", "content": "請簡單介紹一下自己"}
        ]
        
        print("正在透過工廠函數客戶端發送請求...")
        response = client.chat(messages)
        
        print(f"✅ 工廠函數客戶端請求成功！")
        print(f"回應內容: {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ 工廠函數客戶端請求失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主要診斷流程"""
    print("🔬 開始深度診斷...\n")
    
    # 測試 1: 直接 API 呼叫
    direct_ok = test_direct_api_call()
    
    # 測試 2: 我們的客戶端
    client_ok = test_our_client()
    
    # 測試 3: 工廠函數
    factory_ok = test_factory_function()
    
    print("\n" + "="*60)
    print("診斷結果總結:")
    print(f"直接 API 呼叫: {'✅ 成功' if direct_ok else '❌ 失敗'}")
    print(f"客戶端實作: {'✅ 成功' if client_ok else '❌ 失敗'}")
    print(f"工廠函數: {'✅ 成功' if factory_ok else '❌ 失敗'}")
    
    if direct_ok and not client_ok:
        print("\n🔍 問題出在客戶端實作")
    elif direct_ok and client_ok and not factory_ok:
        print("\n🔍 問題出在工廠函數")
    elif not direct_ok:
        print("\n🔍 問題出在 API Key 或網路連線")
    elif direct_ok and client_ok and factory_ok:
        print("\n✅ 所有測試都通過，問題可能已解決！")

if __name__ == "__main__":
    main()
