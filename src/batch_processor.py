#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AQUASKY AIQA Monitor - 多 LLM 自動化批次處理系統
支援斷點續跑、自動存檔、錯誤重試等功能
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import traceback

from llm_client import get_client, LLMError
from report_generator import save_to_excel, save_to_markdown


class BatchProcessor:
    """多 LLM 批次處理管理器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.progress_file = self.project_root / "batch_progress.json"
        self.output_dir = self.project_root / "outputs"
        self.log_dir = self.project_root / "logs"
        
        # 確保目錄存在
        self.output_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        
        # 設定日誌
        self.setup_logging()
        
        # 預設配置
        self.config = {
            "max_retries": 3,
            "retry_delay": 5,  # 秒
            "pause_between_questions": 2,  # 秒
            "pause_between_models": 1,  # 秒
            "auto_save_interval": 5,  # 每 5 個問題自動存檔
        }
        
        # 支援的 LLM 模型列表
        self.available_models = [
            "kimi-k2-free",
            "devstral-medium", 
            "deepseek-chimera-free",
            "gemini-2.5-flash-lite",
            "grok-3",
            "claude-sonnet-4",
            "gpt-4o-mini-high",
            "perplexity-sonar-pro",
        ]
        
        # 進度追蹤
        self.progress = self.load_progress()
        
    def setup_logging(self):
        """設定日誌系統"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"batch_process_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_progress(self) -> Dict[str, Any]:
        """載入進度檔案"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                self.logger.info(f"載入進度檔案: {len(progress.get('completed', []))} 個已完成的任務")
                return progress
            except Exception as e:
                self.logger.error(f"載入進度檔案失敗: {e}")
        
        return {
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "completed": [],
            "failed": [],
            "current_question": 0,
            "current_model": 0,
            "total_questions": 0,
            "target_models": []
        }
    
    def save_progress(self):
        """保存進度檔案"""
        try:
            self.progress["last_update"] = datetime.now().isoformat()
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存進度檔案失敗: {e}")
    
    def is_task_completed(self, question_id: int, model_name: str) -> bool:
        """檢查任務是否已完成"""
        task_key = f"{question_id}_{model_name}"
        return task_key in [item["task_key"] for item in self.progress["completed"]]
    
    def add_completed_task(self, question_id: int, model_name: str, result: Dict[str, Any]):
        """添加已完成的任務"""
        task_key = f"{question_id}_{model_name}"
        self.progress["completed"].append({
            "task_key": task_key,
            "question_id": question_id,
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        self.save_progress()
    
    def add_failed_task(self, question_id: int, model_name: str, error: str):
        """添加失敗的任務"""
        task_key = f"{question_id}_{model_name}"
        self.progress["failed"].append({
            "task_key": task_key,
            "question_id": question_id,
            "model": model_name,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        self.save_progress()
    
    def get_model_filename(self, model_name: str, file_type: str = "xlsx") -> str:
        """生成模型專用的檔案名稱"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model_name = model_name.replace("-", "_").replace(".", "_")
        return f"AQUASKY_AIQA_{safe_model_name}_{timestamp}.{file_type}"
    
    def ask_llm_with_retry(self, model_name: str, messages: List[Dict[str, str]]) -> str:
        """帶重試機制的 LLM 調用"""
        for attempt in range(self.config["max_retries"]):
            try:
                client = get_client(model_name)
                answer = client.chat(messages)
                return answer
            except Exception as e:
                self.logger.warning(f"模型 {model_name} 第 {attempt + 1} 次嘗試失敗: {e}")
                if attempt < self.config["max_retries"] - 1:
                    time.sleep(self.config["retry_delay"])
                else:
                    raise e
    
    def save_model_results(self, model_name: str, results: List[Dict[str, Any]]):
        """為單個模型保存結果"""
        if not results:
            return
            
        try:
            # Excel 格式
            excel_filename = self.get_model_filename(model_name, "xlsx")
            excel_path = self.output_dir / excel_filename
            save_to_excel(results, str(self.output_dir), excel_filename)
            
            # Markdown 格式
            md_filename = self.get_model_filename(model_name, "md")
            md_path = self.output_dir / md_filename
            save_to_markdown(results, str(self.output_dir), md_filename)
            
            self.logger.info(f"模型 {model_name} 結果已保存: {excel_filename}, {md_filename}")
            
        except Exception as e:
            self.logger.error(f"保存模型 {model_name} 結果失敗: {e}")
    
    def process_single_model(self, model_name: str, questions: List[str]) -> List[Dict[str, Any]]:
        """處理單個模型的所有問題"""
        self.logger.info(f"開始處理模型: {model_name}")
        model_results = []
        
        for i, question in enumerate(questions):
            question_id = i + 1
            
            # 檢查是否已完成
            if self.is_task_completed(question_id, model_name):
                self.logger.info(f"跳過已完成的任務: Q{question_id} - {model_name}")
                # 從進度中找到結果
                for completed in self.progress["completed"]:
                    if completed["question_id"] == question_id and completed["model"] == model_name:
                        model_results.append(completed["result"])
                        break
                continue
            
            self.logger.info(f"處理問題 {question_id}/{len(questions)}: {question[:50]}...")
            
            try:
                # 準備訊息
                messages = [
                    {"role": "system", "content": "You are a professional assistant for the water systems industry. Please respond exclusively in Traditional Chinese (請務必使用繁體中文回答)."},
                    {"role": "user", "content": question}
                ]
                
                # 調用 LLM
                answer = self.ask_llm_with_retry(model_name, messages)
                
                # 準備結果
                result = {
                    "question_id": question_id,
                    "question": question,
                    "model": model_name,
                    "answer": answer,
                    "timestamp": datetime.now().isoformat()
                }
                
                model_results.append(result)
                self.add_completed_task(question_id, model_name, result)
                
                self.logger.info(f"完成: Q{question_id} - {model_name}")
                
                # 自動存檔檢查
                if question_id % self.config["auto_save_interval"] == 0:
                    self.save_model_results(model_name, model_results)
                    self.logger.info(f"自動存檔: {model_name} (已完成 {question_id} 個問題)")
                
            except Exception as e:
                error_msg = f"處理失敗: {str(e)}"
                self.logger.error(f"Q{question_id} - {model_name}: {error_msg}")
                self.logger.error(traceback.format_exc())
                
                # 記錄錯誤結果
                error_result = {
                    "question_id": question_id,
                    "question": question,
                    "model": model_name,
                    "answer": f"ERROR: {error_msg}",
                    "timestamp": datetime.now().isoformat()
                }
                
                model_results.append(error_result)
                self.add_failed_task(question_id, model_name, error_msg)
            
            # 問題間暫停
            if i < len(questions) - 1:
                time.sleep(self.config["pause_between_questions"])
        
        # 最終保存
        self.save_model_results(model_name, model_results)
        self.logger.info(f"模型 {model_name} 處理完成，共 {len(model_results)} 個結果")
        
        return model_results
    
    def run_batch_processing(self, questions: List[str], target_models: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """執行批次處理"""
        if target_models is None:
            target_models = self.available_models
        
        # 更新進度資訊
        self.progress["total_questions"] = len(questions)
        self.progress["target_models"] = target_models
        self.save_progress()
        
        self.logger.info(f"開始批次處理: {len(questions)} 個問題 × {len(target_models)} 個模型")
        self.logger.info(f"目標模型: {', '.join(target_models)}")
        
        all_results = {}
        
        for model_idx, model_name in enumerate(target_models):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"處理模型 {model_idx + 1}/{len(target_models)}: {model_name}")
            self.logger.info(f"{'='*60}")
            
            try:
                model_results = self.process_single_model(model_name, questions)
                all_results[model_name] = model_results
                
                # 模型間暫停
                if model_idx < len(target_models) - 1:
                    self.logger.info(f"模型間暫停 {self.config['pause_between_models']} 秒...")
                    time.sleep(self.config["pause_between_models"])
                    
            except Exception as e:
                self.logger.error(f"模型 {model_name} 處理失敗: {e}")
                self.logger.error(traceback.format_exc())
                all_results[model_name] = []
        
        # 生成綜合報告
        self.generate_summary_report(all_results)
        
        # 完成處理
        self.progress["end_time"] = datetime.now().isoformat()
        self.progress["status"] = "completed"
        self.save_progress()
        
        self.logger.info("批次處理完成！")
        return all_results
    
    def generate_summary_report(self, all_results: Dict[str, List[Dict[str, Any]]]):
        """生成綜合比較報告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 合併所有結果
            combined_results = []
            for model_name, results in all_results.items():
                combined_results.extend(results)
            
            if combined_results:
                # 綜合 Excel 報告
                summary_excel = f"AQUASKY_AIQA_SUMMARY_{timestamp}.xlsx"
                save_to_excel(combined_results, str(self.output_dir), summary_excel)
                
                # 綜合 Markdown 報告
                summary_md = f"AQUASKY_AIQA_SUMMARY_{timestamp}.md"
                save_to_markdown(combined_results, str(self.output_dir), summary_md)
                
                self.logger.info(f"綜合報告已生成: {summary_excel}, {summary_md}")
                
                # 生成統計報告
                self.generate_statistics_report(all_results, timestamp)
                
        except Exception as e:
            self.logger.error(f"生成綜合報告失敗: {e}")
    
    def generate_statistics_report(self, all_results: Dict[str, List[Dict[str, Any]]], timestamp: str):
        """生成統計報告"""
        try:
            stats = {
                "處理時間": timestamp,
                "總問題數": len(next(iter(all_results.values()), [])),
                "模型數量": len(all_results),
                "模型統計": {}
            }
            
            for model_name, results in all_results.items():
                success_count = len([r for r in results if not r["answer"].startswith("ERROR:")])
                error_count = len(results) - success_count
                
                stats["模型統計"][model_name] = {
                    "成功": success_count,
                    "失敗": error_count,
                    "成功率": f"{success_count/len(results)*100:.1f}%" if results else "0%"
                }
            
            # 保存統計報告
            stats_file = self.output_dir / f"AQUASKY_AIQA_STATS_{timestamp}.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"統計報告已生成: {stats_file.name}")
            
        except Exception as e:
            self.logger.error(f"生成統計報告失敗: {e}")
    
    def cleanup_progress(self):
        """清理進度檔案"""
        if self.progress_file.exists():
            self.progress_file.unlink()
            self.logger.info("進度檔案已清理")
