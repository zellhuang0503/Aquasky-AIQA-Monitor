#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的 Perplexity API 測試腳本
用於確認正確的模型名稱和 API 連接
"""

import requests
import json
import configparser
from pathlib import Path

def test_perplexity_models():
    """測試不同的 Perplexity 模型名稱"""
    
    # 載入 API Key
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    api_key = config.get('api_keys', 'PERPLEXITY_API_KEY', fallback=None)
    
    if not api_key or api_key == 'your_perplexity_api_key_here':
        print("❌ 請設定 PERPLEXITY_API_KEY")
        return
    
    print(f"🔑 API Key: {api_key[:10]}...")
    
    # 正確的 Perplexity 模型名稱（根據官方文檔）
    models_to_test = [
        "sonar-pro",           # 最新的高級模型
        "sonar",               # 基礎模型
        "sonar-small-chat",    # 小型聊天模型
        "sonar-medium-chat",   # 中型聊天模型
        "sonar-small-online",  # 小型線上模型
        "sonar-medium-online", # 中型線上模型
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    test_message = {
        "messages": [
            {
                "role": "user",
                "content": "Hello, please respond with 'OK'"
            }
        ],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    print(f"\n🧪 測試 {len(models_to_test)} 個模型...")
    print("=" * 60)
    
    working_models = []
    
    for i, model_name in enumerate(models_to_test, 1):
        print(f"\n{i:2d}. 測試模型: {model_name}")
        
        data = test_message.copy()
        data["model"] = model_name
        
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            print(f"    HTTP 狀態: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    answer = result['choices'][0]['message']['content']
                    print(f"    ✅ 成功! 回應: {answer}")
                    working_models.append(model_name)
                else:
                    print(f"    ❌ 回應格式異常")
            else:
                try:
                    error = response.json()
                    error_type = error.get('error', {}).get('type', 'unknown')
                    error_message = error.get('error', {}).get('message', 'No message')
                    print(f"    ❌ 錯誤: {error_type} - {error_message}")
                except:
                    print(f"    ❌ HTTP {response.status_code}: {response.text[:100]}")
                    
        except Exception as e:
            print(f"    ❌ 異常: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"🎉 測試完成!")
    print(f"✅ 可用模型數量: {len(working_models)}")
    
    if working_models:
        print("\n🔥 可用的模型:")
        for model in working_models:
            print(f"  - {model}")
    else:
        print("\n😞 沒有找到可用的模型")
        print("💡 建議檢查:")
        print("  1. API Key 是否正確")
        print("  2. Perplexity 帳戶是否有餘額")
        print("  3. 是否需要特殊權限")

if __name__ == "__main__":
    print("🚀 Perplexity 模型測試工具")
    print("=" * 60)
    test_perplexity_models()
