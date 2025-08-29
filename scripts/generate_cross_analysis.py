#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AQUASKY AEO 交叉分析報告生成器
確保每次分析都達到標準化水準
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import re
from typing import Dict, List, Tuple, Any

class CrossAnalysisGenerator:
    """交叉分析報告生成器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.output_dir = self.project_root / "outputs"
        self.cross_analysis_dir = self.output_dir / "cross_analysis"
        self.templates_dir = self.project_root / "templates"
        self.cross_analysis_dir.mkdir(exist_ok=True)
        
        # 模型名稱映射
        self.model_names = {
            'anthropic_claude-3.5-sonnet': 'Claude 3.5 Sonnet',
            'deepseek_deepseek-v3.1-base': 'DeepSeek v3.1 Base',
            'google_gemini-flash-1.5': 'Gemini Flash 1.5',
            'meta-llama_llama-3.1-8b-instruct': 'Llama 3.1 8B',
            'mistralai_mistral-7b-instruct': 'Mistral 7B',
            'openai_gpt-5-mini': 'GPT-5 Mini',
            'perplexity_sonar-pro': 'Perplexity Sonar Pro',
            'x-ai_grok-3-mini-beta': 'Grok 3 Mini Beta'
        }
        
        # 分析關鍵詞
        self.brand_keywords = ['aquasky', 'aqua sky']
        self.website_keywords = ['aquaskyplus.com', 'aquasky.com']
        self.specific_keywords = ['具體', '詳細', '專業', '技術', '規格', '認證', '測試', '品質', '流程', '標準']
        self.generic_keywords = ['無法確認', '建議聯繫', '請聯絡', '無法提供', '不確定', '無相關資訊', '建議查詢']
    
    def load_reports(self, date_pattern: str) -> Dict[str, pd.DataFrame]:
        """載入指定日期的所有報告"""
        all_data = {}
        
        # 尋找匹配的檔案
        pattern = f"*{date_pattern}*.xlsx"
        files = list(self.output_dir.glob(pattern))
        
        for file_path in files:
            try:
                df = pd.read_excel(file_path)
                # 從檔名提取模型key
                filename = file_path.name
                parts = filename.split('_')
                if len(parts) >= 4:
                    model_key = '_'.join(parts[2:4])
                    all_data[model_key] = df
                    print(f'✅ 載入: {self.model_names.get(model_key, model_key)}')
            except Exception as e:
                print(f'❌ 載入失敗 {file_path.name}: {e}')
        
        return all_data
    
    def analyze_answer_quality(self, answer: str) -> Dict[str, bool]:
        """分析單個回答的品質指標"""
        if pd.isna(answer) or answer == '處理失敗':
            return {
                'has_brand_mention': False,
                'has_website_mention': False,
                'has_specific_info': False,
                'is_generic_response': True
            }
        
        answer_lower = str(answer).lower()
        
        return {
            'has_brand_mention': any(keyword in answer_lower for keyword in self.brand_keywords),
            'has_website_mention': any(keyword in answer_lower for keyword in self.website_keywords),
            'has_specific_info': any(keyword in answer_lower for keyword in self.specific_keywords),
            'is_generic_response': any(keyword in answer_lower for keyword in self.generic_keywords)
        }
    
    def calculate_model_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """計算單個模型的指標"""
        success_count = len(df[df['狀態'] == '成功'])
        total_tokens = df['總Token'].sum()
        avg_tokens = total_tokens / len(df) if len(df) > 0 else 0
        
        # 分析回答品質
        brand_mentions = 0
        website_mentions = 0
        specific_info = 0
        generic_responses = 0
        
        for _, row in df.iterrows():
            if row['狀態'] == '成功':
                quality = self.analyze_answer_quality(row['回答'])
                if quality['has_brand_mention']:
                    brand_mentions += 1
                if quality['has_website_mention']:
                    website_mentions += 1
                if quality['has_specific_info']:
                    specific_info += 1
                if quality['is_generic_response']:
                    generic_responses += 1
        
        return {
            'success_count': success_count,
            'total_tokens': total_tokens,
            'avg_tokens': avg_tokens,
            'brand_mention_rate': (brand_mentions / len(df)) * 100,
            'website_mention_rate': (website_mentions / len(df)) * 100,
            'specific_info_rate': (specific_info / len(df)) * 100,
            'generic_response_rate': (generic_responses / len(df)) * 100
        }
    
    def rank_models(self, all_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, List[Tuple[str, Dict[str, Any]]]]:
        """對模型進行各種排名"""
        models_list = [(k, v) for k, v in all_metrics.items()]
        
        return {
            'efficiency': sorted(models_list, key=lambda x: x[1]['total_tokens']),
            'quality': sorted(models_list, key=lambda x: (
                x[1]['brand_mention_rate'] + 
                x[1]['website_mention_rate'] + 
                x[1]['specific_info_rate'] - 
                x[1]['generic_response_rate']
            ), reverse=True),
            'brand_recognition': sorted(models_list, key=lambda x: x[1]['brand_mention_rate'], reverse=True)
        }
    
    def analyze_questions(self, all_data: Dict[str, pd.DataFrame], sample_questions: int = 5) -> str:
        """分析關鍵問題的回答差異"""
        analysis_text = ""
        
        for i in range(1, min(sample_questions + 1, 21)):
            analysis_text += f"### 問題 {i}\n\n"
            
            # 獲取問題內容
            first_model = list(all_data.keys())[0]
            if i <= len(all_data[first_model]):
                question = all_data[first_model].iloc[i-1]['問題']
                analysis_text += f"**問題**: {question}\n\n"
                
                # 收集所有回答的品質指標
                model_qualities = {}
                for model_key, df in all_data.items():
                    if i <= len(df):
                        row = df.iloc[i-1]
                        if row['狀態'] == '成功':
                            quality = self.analyze_answer_quality(row['回答'])
                            model_qualities[model_key] = {
                                'answer': str(row['回答']),
                                'tokens': row['總Token'],
                                'length': len(str(row['回答'])),
                                **quality
                            }
                
                # 品質分析
                analysis_text += "**回答品質評估**:\n"
                
                brand_mentions = [self.model_names.get(k, k) for k, v in model_qualities.items() if v['has_brand_mention']]
                website_mentions = [self.model_names.get(k, k) for k, v in model_qualities.items() if v['has_website_mention']]
                specific_info = [self.model_names.get(k, k) for k, v in model_qualities.items() if v['has_specific_info']]
                generic_responses = [self.model_names.get(k, k) for k, v in model_qualities.items() if v['is_generic_response']]
                
                if brand_mentions:
                    analysis_text += f"- ✅ **提及AQUASKY品牌**: {', '.join(brand_mentions)}\n"
                else:
                    analysis_text += "- ❌ **無模型提及AQUASKY品牌**\n"
                
                if website_mentions:
                    analysis_text += f"- ✅ **提及官網**: {', '.join(website_mentions)}\n"
                else:
                    analysis_text += "- ❌ **無模型提及官網**\n"
                
                if specific_info:
                    analysis_text += f"- ✅ **提供具體資訊**: {', '.join(specific_info)}\n"
                else:
                    analysis_text += "- ❌ **缺乏具體資訊**\n"
                
                if generic_responses:
                    analysis_text += f"- ⚠️ **泛化回答**: {', '.join(generic_responses)}\n"
                
                # 推薦最佳回答
                if model_qualities:
                    best_model = max(model_qualities.items(), key=lambda x: (
                        x[1]['has_brand_mention'] * 3 +
                        x[1]['has_website_mention'] * 2 +
                        x[1]['has_specific_info'] * 1 -
                        x[1]['is_generic_response'] * 2
                    ))
                    analysis_text += f"\n**最佳回答**: {self.model_names.get(best_model[0], best_model[0])}\n"
                
                analysis_text += "\n---\n\n"
        
        return analysis_text
    
    def generate_report(self, date_pattern: str) -> str:
        """生成完整的交叉分析報告"""
        print(f"🚀 開始生成 {date_pattern} 的交叉分析報告...")
        
        # 載入數據
        all_data = self.load_reports(date_pattern)
        if not all_data:
            raise ValueError(f"找不到 {date_pattern} 的報告檔案")
        
        print(f"📊 成功載入 {len(all_data)} 個模型報告")
        
        # 計算各模型指標
        all_metrics = {}
        for model_key, df in all_data.items():
            all_metrics[model_key] = self.calculate_model_metrics(df)
        
        # 排名
        rankings = self.rank_models(all_metrics)
        
        # 計算整體指標
        total_questions = len(list(all_data.values())[0])
        overall_brand_rate = sum(m['brand_mention_rate'] for m in all_metrics.values()) / len(all_metrics)
        overall_website_rate = sum(m['website_mention_rate'] for m in all_metrics.values()) / len(all_metrics)
        overall_specific_rate = sum(m['specific_info_rate'] for m in all_metrics.values()) / len(all_metrics)
        overall_generic_rate = sum(m['generic_response_rate'] for m in all_metrics.values()) / len(all_metrics)
        
        # 生成報告內容
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_content = f"""# AQUASKY AEO 監控專案 - 詳細交叉分析報告

**生成時間**: {timestamp}
**分析模型數**: {len(all_data)}
**分析依據**: {date_pattern} 執行的 {total_questions} 個黃金問題測試結果

## 執行摘要

本次分析發現所有 {len(all_data)} 個 LLM 模型對 AQUASKY 相關問題的回答品質普遍偏低，主要問題包括：
- **品牌識別度低**: 平均只有 {overall_brand_rate:.1f}% 的回答提及 AQUASKY 品牌
- **缺乏具體資訊**: 平均只有 {overall_specific_rate:.1f}% 的回答提供具體資訊
- **無官網引用**: 平均只有 {overall_website_rate:.1f}% 的回答引用官網
- **泛化回答率高**: {overall_generic_rate:.1f}% 的回答為泛化建議

## 模型效能比較

### Token 使用效率排名
"""
        
        for i, (model_key, metrics) in enumerate(rankings['efficiency'], 1):
            model_name = self.model_names.get(model_key, model_key)
            report_content += f"{i}. **{model_name}**: {metrics['success_count']}/20 成功, 總Token: {metrics['total_tokens']:,}, 平均: {metrics['avg_tokens']:.0f}\n"
        
        report_content += "\n### 回答品質排名\n"
        for i, (model_key, metrics) in enumerate(rankings['quality'], 1):
            model_name = self.model_names.get(model_key, model_key)
            quality_score = (metrics['brand_mention_rate'] + metrics['website_mention_rate'] + 
                           metrics['specific_info_rate'] - metrics['generic_response_rate'])
            report_content += f"{i}. **{model_name}**: 品質分數 {quality_score:.1f}, 品牌提及 {metrics['brand_mention_rate']:.1f}%\n"
        
        # 關鍵問題分析
        report_content += "\n## 關鍵問題分析\n\n"
        report_content += self.analyze_questions(all_data)
        
        # 模型表現評級
        best_overall = rankings['quality'][0]
        best_efficiency = rankings['efficiency'][0]
        best_value = rankings['efficiency'][1] if len(rankings['efficiency']) > 1 else rankings['efficiency'][0]
        
        report_content += f"""## 模型表現評級

### 🏆 最佳綜合表現
**{self.model_names.get(best_overall[0], best_overall[0])}**
- 優點: 品質分數最高，回答相對完整
- 缺點: 仍缺乏 AQUASKY 特定資訊

### 🥈 最佳效率表現  
**{self.model_names.get(best_efficiency[0], best_efficiency[0])}**
- 優點: Token 使用最少 ({best_efficiency[1]['total_tokens']:,})
- 缺點: 回答可能較簡短

### 🥉 最佳性價比
**{self.model_names.get(best_value[0], best_value[0])}**
- 優點: 效率與品質平衡
- 缺點: 同樣缺乏品牌特定資訊

## 根本問題診斷

### 1. 內容可發現性問題
- AQUASKY 官網內容未被 LLM 有效索引
- 缺乏結構化的產品資訊頁面
- FAQ 頁面不存在或不完整

### 2. SEO 與 AEO 優化不足
- 缺乏針對「黃金問題」的專門內容頁
- 沒有 Schema.org 結構化標記
- 關鍵資訊分散，難以被 AI 提取

### 3. 品牌權威性建立不足
- 缺乏第三方權威來源的品牌提及
- 產品規格、認證資訊未系統化呈現
- 公司背景、技術優勢描述不清晰

## 網站內容改善建議

### 立即執行 (1-2 週)

#### A. 建立核心資訊頁面
1. **產品線總覽頁** (`/products/overview`)
   - 列出所有主要產品類別
   - 每個產品的核心規格與應用
   - 添加 Product Schema 標記

2. **品質控制頁** (`/quality/control-process`)
   - 詳述 AQUASKY 特有的 QC 流程
   - 包含測試設備、標準、認證流程
   - 添加具體的測試數據與案例

3. **認證與資質頁** (`/certifications`)
   - 列出所有國際認證 (NSF, CE, WRAS, ISO 等)
   - 提供認證證書圖片與編號
   - 說明各認證的意義與適用範圍

#### B. FAQ 頁面建設
建立針對 20 個黃金問題的專門 FAQ 頁面：
- 使用 FAQPage Schema 標記
- 每個問答都要有具體、權威的答案
- 包含內部連結到相關產品頁面

#### C. 技術優化
1. **Schema.org 標記**
   - Organization: 公司基本資訊
   - Product: 產品詳細資訊  
   - FAQPage: 常見問題
   - Article: 技術文章與新聞

2. **內容結構化**
   - 使用清晰的標題層級 (H1-H6)
   - 添加目錄與錨點連結
   - 重要資訊使用列表格式

### 中期優化 (1-2 個月)

#### A. 內容深度建設
1. **技術白皮書**
   - 水處理技術原理說明
   - AQUASKY 獨有技術優勢
   - 與競品的技術對比

2. **案例研究頁面**
   - 成功應用案例
   - 客戶見證與評價
   - 解決方案詳細說明

#### B. 外部權威建設
1. **行業媒體報導**
   - 主動投稿技術文章
   - 參與行業展會與會議
   - 獲得第三方媒體報導

### 長期策略 (3-6 個月)

#### A. AI 友好優化
1. **robots.txt 優化**
   - 允許主流 AI 爬蟲訪問
   - 設定合理的抓取頻率限制

2. **sitemap.xml 完善**
   - 包含所有重要頁面
   - 設定正確的更新頻率
   - 多語言版本支援

## 預期改善效果

### 短期目標 (1 個月內)
- LLM 回答中提及 AQUASKY 品牌: 目標 >60%
- 引用官網資訊: 目標 >40%  
- 具體資訊提供率: 目標 >70%

### 中期目標 (3 個月內)
- 品牌正確識別率: 目標 >80%
- 官網引用率: 目標 >60%
- 回答準確性: 目標 >85%

### 長期目標 (6 個月內)
- 成為水處理設備領域的權威資訊源
- 在相關問題搜尋中排名前 3
- AI 回答品質達到行業領先水準

## 監控與評估

### 關鍵指標 (KPI)
1. **品牌提及率**: LLM 回答中提及 AQUASKY 的比例
2. **官網引用率**: 引用 aquaskyplus.com 的比例
3. **資訊準確性**: 回答內容的正確性評分
4. **回答完整性**: 提供具體資訊而非泛化建議的比例

### 監控頻率
- 每週執行一次完整測試
- 每月生成詳細分析報告
- 每季度進行策略調整

---

**結論**: 目前 AQUASKY 在 AI 搜尋結果中的表現嚴重不足，需要立即開始系統性的 AEO 優化工作。建議優先建設核心資訊頁面與 FAQ，並加強內容的結構化標記，以提升在 AI 回答中的可見度與準確性。
"""
        
        # 保存報告
        report_filename = f"AEO_detailed_cross_analysis_{date_pattern}.md"
        report_path = self.cross_analysis_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📁 詳細交叉分析報告已生成: {report_path}")
        return str(report_path)

def main():
    """主程式"""
    import sys
    
    if len(sys.argv) < 2:
        date_pattern = datetime.now().strftime("%Y%m%d")
        print(f"未指定日期，使用今天: {date_pattern}")
    else:
        date_pattern = sys.argv[1]
    
    try:
        generator = CrossAnalysisGenerator()
        report_path = generator.generate_report(date_pattern)
        print(f"✅ 報告生成完成: {report_path}")
    except Exception as e:
        print(f"❌ 報告生成失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
