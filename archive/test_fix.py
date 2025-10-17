#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復後的 API 呼叫
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_client import get_client, LLMError

def test_single_question():
    """測試單一問題的 API 呼叫"""
    print("=== 測試修復後的 API 呼叫 ===")
    
    try:
        # 使用與 main.py 相同的方式獲取客戶端
        print("正在初始化 kimi-k2-free 客戶端...")
        client = get_client("kimi-k2-free")
        
        # 使用與 main.py 相同的訊息格式
        messages = [
            {"role": "system", "content": "You are a professional assistant for the water systems industry. Please respond exclusively in Traditional Chinese (請務必使用繁體中文回答)."},
            {"role": "user", "content": "請簡單介紹 AQUASKY 公司"}
        ]
        
        print("正在發送請求...")
        answer = client.chat(messages)
        
        print("✅ 請求成功！")
        print(f"回應長度: {len(answer)} 字元")
        print(f"回應內容: {answer[:200]}...")
        
        return True
        
    except LLMError as e:
        print(f"❌ LLM 錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 未預期錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主要測試"""
    print("🧪 測試修復後的程式碼...\n")
    
    success = test_single_question()
    
    print("\n" + "="*50)
    if success:
        print("✅ 修復成功！API 呼叫正常工作")
        print("\n現在可以執行主程式:")
        print("python src/main.py")
    else:
        print("❌ 修復未完全成功，需要進一步調查")

if __name__ == "__main__":
    main()
