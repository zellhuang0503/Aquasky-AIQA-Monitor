#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交叉分析配置檔案
定義分析標準、品質指標與報告結構
"""

# 分析品質標準
QUALITY_STANDARDS = {
    # 品牌識別度標準
    'brand_recognition': {
        'excellent': 80,  # 80% 以上為優秀
        'good': 60,       # 60-80% 為良好
        'poor': 40,       # 40-60% 為普通
        'critical': 0     # 40% 以下為嚴重不足
    },
    
    # 官網引用率標準
    'website_mention': {
        'excellent': 60,
        'good': 40,
        'poor': 20,
        'critical': 0
    },
    
    # 具體資訊提供率標準
    'specific_info': {
        'excellent': 80,
        'good': 60,
        'poor': 40,
        'critical': 0
    },
    
    # 泛化回答率標準 (越低越好)
    'generic_response': {
        'excellent': 20,  # 20% 以下為優秀
        'good': 40,       # 20-40% 為良好
        'poor': 60,       # 40-60% 為普通
        'critical': 100   # 60% 以上為嚴重問題
    }
}

# 分析關鍵詞配置
ANALYSIS_KEYWORDS = {
    'brand_keywords': [
        'aquasky', 'aqua sky', 'AQUASKY', 'Aquasky',
        '愛克斯凱', '愛克斯', 'AquaSky'
    ],
    
    'website_keywords': [
        'aquaskyplus.com', 'aquasky.com', 'www.aquaskyplus.com',
        'aquaskyplus', 'aquasky官網', 'aquasky網站'
    ],
    
    'specific_keywords': [
        '具體', '詳細', '專業', '技術', '規格', '認證', '測試',
        '品質', '流程', '標準', '數據', '參數', '性能', '功能',
        'NSF', 'CE', 'ISO', 'WRAS', 'FDA', 'SGS', 'TUV',
        '過濾', '淨化', '殺菌', '消毒', '軟化', '逆滲透'
    ],
    
    'generic_keywords': [
        '無法確認', '建議聯繫', '請聯絡', '無法提供', '不確定',
        '無相關資訊', '建議查詢', '請參考官網', '聯繫廠商',
        '無法得知', '不清楚', '無法回答', '建議諮詢',
        '一般來說', '通常', '可能', '或許', '大概'
    ]
}

# 模型名稱標準化映射
MODEL_NAME_MAPPING = {
    'anthropic_claude-3.5-sonnet': 'Claude 3.5 Sonnet',
    'deepseek_deepseek-v3.1-base': 'DeepSeek v3.1 Base',
    'google_gemini-flash-1.5': 'Gemini Flash 1.5',
    'meta-llama_llama-3.1-8b-instruct': 'Llama 3.1 8B',
    'mistralai_mistral-7b-instruct': 'Mistral 7B',
    'openai_gpt-5-mini': 'GPT-5 Mini',
    'perplexity_sonar-pro': 'Perplexity Sonar Pro',
    'x-ai_grok-3-mini-beta': 'Grok 3 Mini Beta'
}

# 報告結構配置
REPORT_STRUCTURE = {
    'sections': [
        'executive_summary',
        'model_performance',
        'question_analysis',
        'model_ranking',
        'problem_diagnosis',
        'improvement_suggestions',
        'expected_results',
        'monitoring_evaluation'
    ],
    
    'required_metrics': [
        'brand_mention_rate',
        'website_mention_rate',
        'specific_info_rate',
        'generic_response_rate',
        'token_efficiency',
        'success_rate'
    ],
    
    'sample_questions': 5,  # 分析前5個問題的詳細回答
    'min_models': 6,        # 最少需要6個模型的數據
    'max_token_threshold': 50000  # 單模型最大Token使用量閾值
}

# 改善建議模板
IMPROVEMENT_TEMPLATES = {
    'immediate_actions': {
        'core_pages': [
            '產品線總覽頁 (`/products/overview`)',
            '品質控制頁 (`/quality/control-process`)',
            '認證與資質頁 (`/certifications`)'
        ],
        'faq_development': [
            '建立針對20個黃金問題的專門FAQ頁面',
            '使用FAQPage Schema標記',
            '提供具體權威答案'
        ],
        'technical_optimization': [
            'Schema.org標記 (Organization, Product, FAQPage)',
            '內容結構化 (清晰標題層級、錨點連結)',
            '重要資訊列表格式化'
        ]
    },
    
    'medium_term_actions': {
        'content_depth': [
            '技術白皮書建設',
            '案例研究頁面',
            '新聞與動態更新'
        ],
        'authority_building': [
            '行業媒體報導',
            '合作夥伴展示',
            '第三方認證展示'
        ]
    },
    
    'long_term_actions': {
        'ai_optimization': [
            'robots.txt優化',
            'sitemap.xml完善',
            'AI爬蟲友好設定'
        ],
        'multilingual': [
            '英文版核心頁面',
            '其他目標市場語言版本',
            'hreflang標記設定'
        ]
    }
}

# KPI 目標設定
KPI_TARGETS = {
    'short_term': {  # 1個月內
        'brand_mention_rate': 60,
        'website_mention_rate': 40,
        'specific_info_rate': 70,
        'generic_response_rate': 30
    },
    
    'medium_term': {  # 3個月內
        'brand_mention_rate': 80,
        'website_mention_rate': 60,
        'specific_info_rate': 85,
        'generic_response_rate': 20
    },
    
    'long_term': {  # 6個月內
        'brand_mention_rate': 90,
        'website_mention_rate': 80,
        'specific_info_rate': 95,
        'generic_response_rate': 10
    }
}

# 報告品質檢查標準
QUALITY_CHECKS = {
    'min_content_length': 5000,    # 報告最少字數
    'required_sections': 8,        # 必需章節數
    'min_question_analysis': 3,    # 最少分析問題數
    'required_rankings': 3,        # 必需排名類型數
    'min_suggestions': 10          # 最少改善建議數
}
