#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AQUASKY AIQA Monitor - 批次處理配置檔案
集中管理所有批次處理相關的設定參數
"""

from typing import List, Dict, Any

class BatchConfig:
    """批次處理配置類別"""
    
    # 支援的 LLM 模型列表（使用 llm_client.py 中定義的內部名稱）
    AVAILABLE_MODELS: List[str] = [
        "kimi-k2-free",
        "devstral-medium",
        "deepseek-chimera-free",
        "gemini-2.5-flash-lite",
        "grok-3",
        "claude-sonnet-4",
        "gpt-4o-mini-high",
        "perplexity-sonar-pro",
    ]

    # 預設模型組合（用於快速開始，選擇高效模型）
    DEFAULT_MODELS: List[str] = [
        "deepseek-chimera-free",    # 最穩定的模型
        "grok-3",                   # 最快的 Grok 模型
        "gpt-4o-mini-high",         # 高品質 OpenAI 模型
    ]
    
    # 推薦的完整測試模型組合
    RECOMMENDED_MODELS: List[str] = [
        "kimi-k2-free",
        "deepseek-chimera-free",
        "gemini-2.5-flash-lite",
        "gpt-4o-mini-high",
        "claude-sonnet-4"
    ]
    
    # 批次處理設定
    BATCH_SETTINGS: Dict[str, Any] = {
        # 重試設定
        "max_retries": 3,                    # 最大重試次數
        "retry_delay": 5,                    # 重試間隔（秒）
        "exponential_backoff": True,         # 是否使用指數退避
        
        # 暫停設定
        "pause_between_questions": 2,        # 問題間暫停（秒）
        "pause_between_models": 3,           # 模型間暫停（秒）
        "pause_on_error": 10,               # 錯誤後暫停（秒）
        
        # 自動存檔設定
        "auto_save_interval": 5,             # 每 N 個問題自動存檔
        "save_individual_models": True,      # 是否為每個模型單獨存檔
        "save_combined_report": True,        # 是否生成綜合報告
        
        # 檔案命名設定
        "include_timestamp": True,           # 檔案名包含時間戳
        "include_model_name": True,          # 檔案名包含模型名稱
        "filename_format": "AQUASKY_AIQA_{model}_{timestamp}",  # 檔案名格式
        
        # 日誌設定
        "log_level": "INFO",                 # 日誌等級
        "log_to_file": True,                 # 是否記錄到檔案
        "log_to_console": True,              # 是否輸出到控制台
        
        # 進度追蹤設定
        "enable_progress_tracking": True,    # 是否啟用進度追蹤
        "progress_file": "batch_progress.json",  # 進度檔案名
        "cleanup_on_completion": False,      # 完成後是否清理進度檔案
    }
    
    # 系統訊息模板
    SYSTEM_MESSAGES: Dict[str, str] = {
        "default": "You are a professional assistant for the water systems industry. Please respond exclusively in Traditional Chinese (請務必使用繁體中文回答).",
        
        "technical": "You are a technical expert in water treatment systems, with deep knowledge of AQUASKY products. Please provide detailed technical responses in Traditional Chinese (請務必使用繁體中文回答).",
        
        "sales": "You are a sales consultant for water treatment systems, focusing on AQUASKY products. Please provide persuasive and informative responses in Traditional Chinese (請務必使用繁體中文回答).",
        
        "comparison": "You are an industry analyst specializing in water treatment systems. Please provide objective comparisons and analysis in Traditional Chinese (請務必使用繁體中文回答)."
    }
    
    # 問題分類設定
    QUESTION_CATEGORIES: Dict[str, List[str]] = {
        "產品特色": ["advantage", "feature", "benefit", "特色", "優勢", "好處"],
        "技術規格": ["specification", "technical", "spec", "規格", "技術", "參數"],
        "市場競爭": ["competition", "competitor", "market", "競爭", "市場", "對手"],
        "客戶服務": ["service", "support", "warranty", "服務", "支援", "保固"],
        "價格成本": ["price", "cost", "budget", "價格", "成本", "預算"],
        "安裝維護": ["installation", "maintenance", "安裝", "維護", "保養"]
    }
    
    # 輸出格式設定
    OUTPUT_FORMATS: Dict[str, Dict[str, Any]] = {
        "excel": {
            "enabled": True,
            "engine": "openpyxl",
            "columns": ["question_id", "question", "model", "answer", "timestamp", "category"],
            "formatting": {
                "auto_width": True,
                "wrap_text": True,
                "freeze_panes": (1, 0)
            }
        },
        
        "markdown": {
            "enabled": True,
            "include_toc": True,
            "group_by_question": True,
            "include_metadata": True
        },
        
        "json": {
            "enabled": False,
            "pretty_print": True,
            "include_metadata": True
        },
        
        "csv": {
            "enabled": False,
            "encoding": "utf-8-sig",
            "separator": ","
        }
    }
    
    # API 設定
    API_SETTINGS: Dict[str, Any] = {
        "timeout": 60,                       # API 超時時間（秒）
        "max_tokens": 4000,                  # 最大 token 數
        "temperature": 0.7,                  # 回應創意度
        "top_p": 0.9,                        # 核心採樣參數
        
        # 速率限制設定
        "rate_limit": {
            "requests_per_minute": 20,       # 每分鐘請求數限制
            "tokens_per_minute": 40000,      # 每分鐘 token 數限制
            "concurrent_requests": 1,        # 並發請求數
        }
    }
    
    @classmethod
    def get_model_display_name(cls, model_name: str) -> str:
        """取得模型的顯示名稱"""
        display_names = {
            "kimi-k2-free": "月之暗面 Kimi K2 (免費版)",
            "deepseek-chimera-free": "DeepSeek Chimera (免費版)",
            "gemini-2.5-flash-lite": "Google Gemini 2.5 Flash Lite",
            "gpt-4o-mini-high": "OpenAI GPT-4o Mini (高品質)",
            "claude-sonnet-4": "Anthropic Claude Sonnet 4",
            "devstral-medium": "Mistral Devstral (中等版本)",
            "grok-3": "xAI Grok 3",
            "perplexity-sonar-pro": "Perplexity Sonar Pro"
        }
        return display_names.get(model_name, model_name)
    
    @classmethod
    def get_safe_filename(cls, model_name: str) -> str:
        """取得安全的檔案名稱（移除特殊字元）"""
        return model_name.replace("-", "_").replace(".", "_").replace(" ", "_")
    
    @classmethod
    def validate_models(cls, models: List[str]) -> List[str]:
        """驗證模型列表，移除不支援的模型"""
        valid_models = []
        for model in models:
            if model in cls.AVAILABLE_MODELS:
                valid_models.append(model)
            else:
                print(f"⚠️  警告: 模型 '{model}' 不在支援列表中，已跳過")
        return valid_models
    
    @classmethod
    def get_system_message(cls, message_type: str = "default") -> str:
        """取得系統訊息"""
        return cls.SYSTEM_MESSAGES.get(message_type, cls.SYSTEM_MESSAGES["default"])
    
    @classmethod
    def categorize_question(cls, question: str) -> str:
        """根據問題內容分類"""
        question_lower = question.lower()
        
        for category, keywords in cls.QUESTION_CATEGORIES.items():
            if any(keyword in question_lower for keyword in keywords):
                return category
        
        return "其他"
