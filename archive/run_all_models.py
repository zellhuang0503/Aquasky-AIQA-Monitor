#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動化執行所有 LLM 模型的批次處理腳本
避免互動式輸入，直接執行所有 8 個模型
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加 src 目錄到路徑
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from batch_processor import BatchProcessor
    from batch_config import BatchConfig
except ImportError as e:
    print(f"❌ 無法導入必要模組: {e}")
    print("請確保 src/ 目錄中有相關檔案")
    sys.exit(1)

def main():
    """主程式 - 自動執行所有模型的批次處理"""
    print("🚀 AQUASKY AIQA Monitor - 自動化批次處理")
    print("=" * 60)
    
    # 設定專案根目錄
    project_root = Path(__file__).parent
    print(f"📁 專案根目錄: {project_root}")
    
    # 使用所有可用的模型
    selected_models = BatchConfig.AVAILABLE_MODELS
    print(f"🤖 將使用 {len(selected_models)} 個 LLM 模型:")
    for i, model in enumerate(selected_models, 1):
        print(f"  {i}. {model}")
    
    print("\n" + "=" * 60)
    print("🔄 開始自動化批次處理...")
    print("💡 提示：處理過程中會自動保存進度，可隨時中斷後繼續")
    print("=" * 60)
    
    try:
        # 建立批次處理器
        processor = BatchProcessor(project_root=str(project_root))
        
        # 執行批次處理（使用所有可用模型）
        success = processor.run_batch_processing(selected_models)
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 批次處理完成！")
            print("📊 請查看 outputs/ 目錄中的報告檔案")
            print("📈 統計資料和詳細結果已自動生成")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ 批次處理過程中遇到問題")
            print("📋 請查看日誌檔案了解詳細錯誤資訊")
            print("💡 可以重新執行此腳本繼續未完成的處理")
            print("=" * 60)
            
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("⏸️ 使用者中斷處理")
        print("💡 進度已保存，可重新執行此腳本繼續處理")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 發生未預期的錯誤: {str(e)}")
        print("📋 請檢查配置檔案和 API Key 設定")
        print("💡 如果問題持續，請查看日誌檔案")

if __name__ == "__main__":
    main()
