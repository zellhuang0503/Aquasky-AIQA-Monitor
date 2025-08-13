#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 調試腳本 - 測試 OpenRouterChatClient 的實際行為
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_client import get_client, LLMError

def test_openrouter_client():
    """測試 OpenRouterChatClient 的實際請求"""
    print("=== 測試 OpenRouterChatClient ===")
    
    try:
        # 獲取客戶端
        print("正在初始化 kimi-k2-free 客戶端...")
        client = get_client("kimi-k2-free")
        
        # 檢查客戶端屬性
        print(f"客戶端類型: {type(client).__name__}")
        print(f"模型名稱: {client.model}")
        print(f"API Key 前10字元: {client.api_key[:10]}...")
        
        # 檢查 session headers
        print(f"Session headers:")
        for key, value in client.session.headers.items():
            if key.lower() == 'authorization':
                print(f"  {key}: Bearer {value[7:17]}...")  # 只顯示前10字元
            else:
                print(f"  {key}: {value}")
        
        # 測試簡單請求
        print("\n正在發送測試請求...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Please respond in Traditional Chinese."},
            {"role": "user", "content": "請簡單介紹一下自己"}
        ]
        
        response = client.chat(messages)
        print(f"✅ 請求成功！")
        print(f"回應長度: {len(response)} 字元")
        print(f"回應前100字元: {response[:100]}...")
        
        return True
        
    except LLMError as e:
        print(f"❌ LLM 錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 未預期錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_loading():
    """測試配置載入"""
    print("=== 測試配置載入 ===")
    
    try:
        import configparser
        from pathlib import Path
        
        config = configparser.ConfigParser()
        config_path = Path(__file__).parent / 'config.ini'
        
        print(f"配置檔案路徑: {config_path}")
        print(f"檔案存在: {config_path.exists()}")
        
        if config_path.exists():
            config.read(config_path, encoding='utf-8')
            
            # 檢查區段
            sections = config.sections()
            print(f"配置區段: {sections}")
            
            # 檢查 API Key
            if 'api_keys' in config:
                api_key = config.get('api_keys', 'OPENROUTER_API_KEY', fallback=None)
                if api_key:
                    print(f"✅ OPENROUTER_API_KEY 已設定 (前10字元: {api_key[:10]}...)")
                else:
                    print("❌ OPENROUTER_API_KEY 未設定")
            else:
                print("❌ [api_keys] 區段不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置載入錯誤: {e}")
        return False

def main():
    """主要測試流程"""
    print("🔧 開始 API 調試...\n")
    
    # 測試配置載入
    config_ok = test_config_loading()
    print()
    
    # 測試 OpenRouter 客戶端
    if config_ok:
        client_ok = test_openrouter_client()
    else:
        print("❌ 配置載入失敗，跳過客戶端測試")
        client_ok = False
    
    print("\n" + "="*50)
    print("調試完成！")
    
    if not client_ok:
        print("\n🔍 可能的問題:")
        print("1. API Key 在程式中沒有正確傳遞到請求 headers")
        print("2. Session 設定有問題")
        print("3. 請求格式不符合 OpenRouter 要求")

if __name__ == "__main__":
    main()
