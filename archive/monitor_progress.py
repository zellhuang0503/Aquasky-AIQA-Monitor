#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
監控程式運行狀態腳本
"""

import os
import time
import psutil
from pathlib import Path

def check_python_processes():
    """檢查 Python 程序狀態"""
    print("=== Python 程序狀態 ===")
    
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
        try:
            if proc.info['name'] == 'python.exe':
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'main.py' in cmdline:
                    python_processes.append(proc)
                    print(f"PID: {proc.info['pid']}")
                    print(f"命令行: {cmdline}")
                    print(f"CPU 使用率: {proc.cpu_percent()}%")
                    print(f"記憶體使用: {proc.info['memory_info'].rss / 1024 / 1024:.1f} MB")
                    print(f"狀態: {proc.status()}")
                    print("-" * 40)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return python_processes

def check_output_files():
    """檢查輸出檔案狀態"""
    print("\n=== 輸出檔案狀態 ===")
    
    project_root = Path(__file__).parent
    output_dir = project_root / "outputs"
    
    if not output_dir.exists():
        print("❌ outputs 資料夾不存在")
        return
    
    print(f"輸出資料夾: {output_dir}")
    
    files = list(output_dir.glob("*"))
    if not files:
        print("📁 outputs 資料夾為空")
    else:
        print(f"檔案數量: {len(files)}")
        for file in files:
            stat = file.stat()
            print(f"  📄 {file.name} - {stat.st_size} bytes - {time.ctime(stat.st_mtime)}")

def check_log_files():
    """檢查日誌檔案"""
    print("\n=== 日誌檔案檢查 ===")
    
    project_root = Path(__file__).parent
    log_files = list(project_root.glob("*.log"))
    
    if not log_files:
        print("📝 沒有找到日誌檔案")
    else:
        for log_file in log_files:
            print(f"📝 {log_file.name}")
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"  最後幾行:")
                        for line in lines[-5:]:
                            print(f"    {line.strip()}")
            except Exception as e:
                print(f"  讀取錯誤: {e}")

def test_api_connectivity():
    """測試 API 連線狀態"""
    print("\n=== API 連線測試 ===")
    
    try:
        import sys
        sys.path.append(str(Path(__file__).parent / 'src'))
        from llm_client import get_client
        
        print("正在測試 API 連線...")
        client = get_client("kimi-k2-free")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "請簡單說聲你好"}
        ]
        
        start_time = time.time()
        response = client.chat(messages)
        end_time = time.time()
        
        print(f"✅ API 連線正常")
        print(f"回應時間: {end_time - start_time:.2f} 秒")
        print(f"回應內容: {response[:100]}...")
        
    except Exception as e:
        print(f"❌ API 連線測試失敗: {e}")

def main():
    """主要監控流程"""
    print("🔍 AQUASKY AIQA Monitor 狀態檢查\n")
    
    # 檢查 Python 程序
    processes = check_python_processes()
    
    # 檢查輸出檔案
    check_output_files()
    
    # 檢查日誌檔案
    check_log_files()
    
    # 測試 API 連線
    test_api_connectivity()
    
    print("\n" + "="*50)
    print("監控完成！")
    
    if processes:
        print(f"\n發現 {len(processes)} 個相關的 Python 程序正在運行")
        print("如果程式看起來卡住了，您可以:")
        print("1. 等待更長時間（API 回應可能較慢）")
        print("2. 按 Ctrl+C 中斷程式")
        print("3. 檢查網路連線狀況")
    else:
        print("\n沒有發現運行中的主程式")

if __name__ == "__main__":
    main()
