#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的程式狀態監控腳本
"""

import os
import time
from pathlib import Path

def check_output_files():
    """檢查輸出檔案狀態"""
    print("=== 輸出檔案狀態 ===")
    
    project_root = Path(__file__).parent
    output_dir = project_root / "outputs"
    
    if not output_dir.exists():
        print("❌ outputs 資料夾不存在")
        return False
    
    print(f"輸出資料夾: {output_dir}")
    
    files = list(output_dir.glob("*"))
    if not files:
        print("📁 outputs 資料夾為空 - 程式可能還在運行中")
        return False
    else:
        print(f"✅ 找到 {len(files)} 個檔案:")
        for file in files:
            stat = file.stat()
            size_mb = stat.st_size / 1024 / 1024
            mod_time = time.ctime(stat.st_mtime)
            print(f"  📄 {file.name} - {size_mb:.2f} MB - {mod_time}")
        return True

def test_api_quick():
    """快速測試 API 連線"""
    print("\n=== 快速 API 測試 ===")
    
    try:
        import sys
        sys.path.append(str(Path(__file__).parent / 'src'))
        from llm_client import get_client
        
        print("正在測試 API 連線...")
        client = get_client("kimi-k2-free")
        
        messages = [
            {"role": "user", "content": "測試"}
        ]
        
        start_time = time.time()
        response = client.chat(messages)
        end_time = time.time()
        
        print(f"✅ API 連線正常")
        print(f"回應時間: {end_time - start_time:.2f} 秒")
        return True
        
    except Exception as e:
        print(f"❌ API 連線測試失敗: {e}")
        return False

def check_question_file():
    """檢查問題檔案"""
    print("\n=== 問題檔案檢查 ===")
    
    project_root = Path(__file__).parent
    question_file = project_root / "AQUASKY AEO 監控專案 - 黃金問題庫 V3.0.md"
    
    if not question_file.exists():
        print("❌ 問題檔案不存在")
        return False
    
    try:
        with open(question_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 計算問題數量
        import re
        questions = re.findall(r'^\d+\.\s', content, re.MULTILINE)
        print(f"✅ 問題檔案存在，包含 {len(questions)} 個問題")
        return True
        
    except Exception as e:
        print(f"❌ 讀取問題檔案失敗: {e}")
        return False

def main():
    """主要檢查流程"""
    print("🔍 AQUASKY AIQA Monitor 簡單狀態檢查\n")
    
    # 檢查問題檔案
    question_ok = check_question_file()
    
    # 檢查輸出檔案
    output_ready = check_output_files()
    
    # 測試 API
    api_ok = test_api_quick()
    
    print("\n" + "="*50)
    print("狀態總結:")
    print(f"問題檔案: {'✅ 正常' if question_ok else '❌ 異常'}")
    print(f"API 連線: {'✅ 正常' if api_ok else '❌ 異常'}")
    print(f"輸出檔案: {'✅ 已生成' if output_ready else '⏳ 處理中'}")
    
    if not output_ready and api_ok:
        print("\n💡 程式狀態分析:")
        print("- API 連線正常")
        print("- 輸出檔案尚未生成")
        print("- 程式可能正在處理問題中")
        print("- 建議繼續等待或檢查主程式輸出")
    elif output_ready:
        print("\n🎉 程式執行完成！")
        print("可以檢查 outputs 資料夾中的結果檔案")

if __name__ == "__main__":
    main()
