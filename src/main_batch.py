#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AQUASKY AIQA Monitor - 多 LLM 自動化批次處理主程式
支援 8 種 LLM 自動化處理、斷點續跑、智能檔案命名等功能
"""

import os
import re
import sys
from pathlib import Path
from typing import List

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent))

from batch_processor import BatchProcessor


def load_questions(file_path: str) -> List[str]:
    """從 Markdown 檔案載入問題列表
    
    Args:
        file_path: 問題檔案路徑
        
    Returns:
        問題列表
    """
    if not os.path.exists(file_path):
        print(f"❌ 錯誤: 找不到問題檔案 {file_path}")
        return []

    print(f"📖 載入問題檔案: {file_path}")
    questions = []
    
    # 正則表達式匹配以數字開頭的問題行，例如 "1. ..."
    question_pattern = re.compile(r"^\d+\.\s.*")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if question_pattern.match(line):
                    # 移除開頭的數字和點，例如 "1. "
                    question_text = re.sub(r"^\d+\.\s", "", line)
                    questions.append(question_text)
        
        print(f"✅ 成功載入 {len(questions)} 個問題")
        return questions
        
    except Exception as e:
        print(f"❌ 讀取問題檔案失敗: {e}")
        return []


def get_user_model_selection(available_models: List[str]) -> List[str]:
    """讓用戶選擇要使用的模型
    
    Args:
        available_models: 可用模型列表
        
    Returns:
        用戶選擇的模型列表
    """
    print(f"\n🤖 可用的 LLM 模型:")
    for i, model in enumerate(available_models, 1):
        print(f"  {i}. {model}")
    
    print(f"\n選擇選項:")
    print(f"  A. 使用所有 {len(available_models)} 個模型")
    print(f"  B. 自訂選擇模型")
    print(f"  C. 使用預設模型 (前 3 個)")
    
    while True:
        choice = input("\n請選擇 (A/B/C): ").strip().upper()
        
        if choice == 'A':
            return available_models
        elif choice == 'C':
            return available_models[:3]
        elif choice == 'B':
            return get_custom_model_selection(available_models)
        else:
            print("❌ 無效選擇，請輸入 A、B 或 C")


def get_custom_model_selection(available_models: List[str]) -> List[str]:
    """讓用戶自訂選擇模型
    
    Args:
        available_models: 可用模型列表
        
    Returns:
        用戶選擇的模型列表
    """
    print(f"\n請輸入要使用的模型編號 (用逗號分隔，例如: 1,3,5):")
    
    while True:
        try:
            input_str = input("模型編號: ").strip()
            if not input_str:
                print("❌ 請輸入至少一個模型編號")
                continue
                
            # 解析用戶輸入
            indices = [int(x.strip()) for x in input_str.split(',')]
            
            # 驗證編號範圍
            if any(i < 1 or i > len(available_models) for i in indices):
                print(f"❌ 編號必須在 1-{len(available_models)} 範圍內")
                continue
            
            # 轉換為模型名稱
            selected_models = [available_models[i-1] for i in indices]
            
            print(f"✅ 已選擇 {len(selected_models)} 個模型:")
            for model in selected_models:
                print(f"  - {model}")
            
            return selected_models
            
        except ValueError:
            print("❌ 請輸入有效的數字，用逗號分隔")


def show_progress_info(processor: BatchProcessor):
    """顯示進度資訊"""
    progress = processor.progress
    
    if progress.get("completed"):
        completed_count = len(progress["completed"])
        total_tasks = progress.get("total_questions", 0) * len(progress.get("target_models", []))
        
        print(f"\n📊 進度資訊:")
        print(f"  已完成任務: {completed_count}")
        print(f"  總任務數: {total_tasks}")
        if total_tasks > 0:
            print(f"  完成率: {completed_count/total_tasks*100:.1f}%")
        
        if progress.get("failed"):
            print(f"  失敗任務: {len(progress['failed'])}")


def main():
    """主程式執行函數"""
    print("🚀 AQUASKY AIQA Monitor - 多 LLM 自動化批次處理系統")
    print("=" * 60)
    
    # 1. 設定專案路徑
    project_root = Path(__file__).parent.parent
    print(f"📁 專案根目錄: {project_root}")
    
    # 2. 載入問題
            question_file = project_root / "AQUASKY AEO 監控專案 - 黃金問題庫 V3.0.md"    questions = load_questions(str(question_file))
    
    if not questions:
        print("❌ 沒有載入到問題，程式結束")
        return

    # --- 臨時測試修改：只使用第一個問題 ---
    questions = questions[:1]
    print("⚠️  注意：已啟用臨時測試模式，僅使用 1 個問題。")
    # --- 臨時測試修改結束 ---
    
    # 3. 初始化批次處理器
    processor = BatchProcessor(str(project_root))
    
    # 4. 顯示現有進度
    show_progress_info(processor)
    
    # 5. 選擇模型 (臨時測試修改：自動選擇所有模型)
    target_models = processor.available_models
    print("⚠️  注意：已啟用臨時測試模式，自動選擇所有可用模型。")
    
    # 6. 確認開始處理
    print(f"\n🎯 處理摘要:")
    print(f"  問題數量: {len(questions)}")
    print(f"  目標模型: {len(target_models)} 個")
    print(f"  總任務數: {len(questions) * len(target_models)}")
    print(f"  預估時間: {len(questions) * len(target_models) * 10 / 60:.1f} 分鐘")
    
    print(f"\n📋 目標模型列表:")
    for i, model in enumerate(target_models, 1):
        print(f"  {i}. {model}")
    
    # 確認開始 (臨時測試修改：自動開始)
    print("⚠️  注意：已啟用臨時測試模式，自動開始處理。")
    # while True:
    #     confirm = input(f"\n是否開始批次處理？(y/n): ").strip().lower()
    #     if confirm in ['y', 'yes', '是']:
    #         break
    #     elif confirm in ['n', 'no', '否']:
    #         print("❌ 用戶取消操作")
    #         return
    #     else:
    #         print("❌ 請輸入 y 或 n")
    
    # 7. 開始批次處理
    print(f"\n🔄 開始批次處理...")
    print(f"💡 提示: 程式支援斷點續跑，可以隨時按 Ctrl+C 中斷")
    print(f"💾 自動存檔: 每 {processor.config['auto_save_interval']} 個問題自動保存")
    print(f"📁 輸出目錄: {processor.output_dir}")
    print(f"📝 日誌目錄: {processor.log_dir}")
    
    try:
        results = processor.run_batch_processing(questions, target_models)
        
        # 8. 顯示結果摘要
        print(f"\n🎉 批次處理完成！")
        print(f"📊 結果摘要:")
        
        total_success = 0
        total_tasks = 0
        
        for model_name, model_results in results.items():
            success_count = len([r for r in model_results if not r["answer"].startswith("ERROR:")])
            total_success += success_count
            total_tasks += len(model_results)
            
            print(f"  {model_name}: {success_count}/{len(model_results)} 成功")
        
        print(f"  總成功率: {total_success}/{total_tasks} ({total_success/total_tasks*100:.1f}%)")
        
        # 9. 清理進度檔案 (臨時測試修改：自動跳過)
        print("⚠️  注意：已啟用臨時測試模式，自動跳過清理進度檔案的步驟。")
        # cleanup = input(f"\n是否清理進度檔案？(y/n): ").strip().lower()
        # if cleanup in ['y', 'yes', '是']:
        #     processor.cleanup_progress()
        #     print("✅ 進度檔案已清理")
        
        print(f"\n📁 請檢查輸出目錄中的結果檔案: {processor.output_dir}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  用戶中斷程式")
        print(f"💾 進度已保存，可以稍後繼續執行")
        print(f"📁 部分結果已保存至: {processor.output_dir}")
        
    except Exception as e:
        print(f"\n❌ 批次處理失敗: {e}")
        processor.logger.error(f"批次處理失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
