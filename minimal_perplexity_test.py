#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最簡化的 Perplexity API 測試
"""

import requests
import json
import configparser

def test_perplexity():
    # 載入 API Key
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    api_key = config.get('api_keys', 'PERPLEXITY_API_KEY', fallback=None)
    
    print(f"🔑 API Key: {api_key[:15]}..." if api_key else "❌ 沒有 API Key")
    
    if not api_key:
        return
    
    # 測試最基本的模型
    models = ["sonar-pro", "sonar"]
    
    for model in models:
        print(f"\n🧪 測試模型: {model}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=15
            )
            
            print(f"  狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result:
                    answer = result['choices'][0]['message']['content']
                    print(f"  ✅ 成功! 回應: {answer}")
                    return model  # 返回第一個成功的模型
                else:
                    print(f"  ❌ 回應格式異常: {result}")
            else:
                print(f"  ❌ 失敗: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
    
    print("\n❌ 所有模型都失敗了")
    return None

if __name__ == "__main__":
    print("🚀 最簡化 Perplexity 測試")
    print("=" * 40)
    working_model = test_perplexity()
    if working_model:
        print(f"\n🎉 找到可用模型: {working_model}")
    else:
        print("\n😞 沒有可用模型")
