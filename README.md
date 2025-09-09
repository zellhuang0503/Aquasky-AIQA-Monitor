# AQUASKY AI/QA 監控系統

> 自動化多 LLM 品牌監控與問答質量分析平台

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 🚀 專案概述

AQUASKY AI/QA 監控系統是一個自動化品牌監控解決方案，定期向多個大型語言模型（LLMs）發送「黃金問題庫」，監控 AQUASKY 品牌在各 AI 模型中的回覆品質與競品比較結果。

### 🎯 主要目標

- **品牌聲量監控**：追蹤 AQUASKY 在各 AI 模型中的品牌提及情況
- **競品分析**：自動化收集各模型對競品比較的回覆
- **質量分析**：量化評估不同 AI 模型的回答品質和準確度
- **決策支援**：為行銷、技術、採購團隊提供數據化決策依據

## ✨ 核心功能

### 🤖 多 LLM 支援
支援 8 種主流 AI 模型同時處理：
- **月之暗面 Kimi K2** (免費版)
- **DeepSeek Chimera** (免費版) 
- **Google Gemini 2.5 Flash Lite**
- **OpenAI GPT-4o Mini** (高品質)
- **Anthropic Claude Sonnet 4**
- **Mistral Devstral** (中等版本)
- **xAI Grok 3**
- **Perplexity Sonar Pro**

### 📊 智能分析系統
- **品牌識別度**分析：量化品牌提及率
- **官網引用率**統計：追蹤官方網站被提及程度
- **交叉分析報告**：多維度模型比較
- **質量評分系統**：自動化回答品質評估

### 🔄 自動化流程
- **定時執行**：支援週期性自動運行
- **斷點續跑**：程式中斷後可從上次停止處繼續
- **自動存檔**：每處理 5 個問題自動保存
- **錯誤重試**：API 調用失敗時自動重試

## 📁 專案結構

```
AQUASKY-AIQA-Monitor/
├── src/                              # 核心程式碼
│   ├── main_batch.py                 # 批次處理主程式
│   ├── batch_processor.py            # 批次處理核心邏輯
│   ├── llm_client.py                 # LLM 客戶端
│   └── report_generator.py           # 報告生成器
├── scripts/                          # 分析腳本
│   ├── generate_cross_analysis.py    # 交叉分析生成器
│   ├── analysis_config.py            # 分析配置
│   └── quality_validator.py          # 品質驗證器
├── templates/                        # 報告模板
│   └── cross_analysis_template.md    # 交叉分析模板
├── outputs/                          # 輸出目錄
│   ├── cross_analysis/              # 交叉分析報告
│   └── *.xlsx, *.md                 # 各種格式報告
├── logs/                            # 系統日誌
├── config.ini                       # 配置檔案
├── requirements.txt                 # Python 依賴套件
├── batch_config.py                  # 批次處理配置
├── batch_progress.json              # 進度追蹤檔案
└── run_standardized_analysis.py     # 標準化分析執行器
```

## 🛠️ 安裝與設定

### 1. 環境需求
- Python 3.11+
- 穩定的網路連線
- 約 500MB 磁碟空間

### 2. 安裝步驟

```bash
# 1. 克隆專案
git clone <repository-url>
cd Aquasky-AIQA-Monitor

# 2. 安裝依賴套件
pip install -r requirements.txt

# 3. 配置 API Keys
cp config.ini.template config.ini
# 編輯 config.ini 填入您的 API Keys
```

### 3. API Keys 配置

編輯 `config.ini` 檔案：

```ini
[api_keys]
# OpenRouter API Key
openrouter_api_key = your_openrouter_api_key_here

# Perplexity API Key  
PERPLEXITY_API_KEY = your_perplexity_api_key_here

# Google Gemini API Key
gemini_api_key = your_gemini_api_key_here

[settings]
http_timeout = 60
```

## 🚀 使用方法

### 快速開始

```bash
# 執行多 LLM 批次處理
python src/main_batch.py

# 執行標準化交叉分析
python run_standardized_analysis.py
```

### 互動式選擇

程式啟動後會提供以下選項：
- **A. 使用所有 8 個模型**：完整測試所有支援的 LLM
- **B. 自訂選擇模型**：手動選擇特定的模型組合  
- **C. 使用預設模型**：快速開始（前 3 個推薦模型）

### 進階使用

```bash
# 指定日期執行分析
python run_standardized_analysis.py --date 20250829

# 監控執行進度
python simple_monitor.py

# 更新 API Key
python update_api_key.py

# 檢查配置
python check_config.py
```

## 📊 輸出報告

### 單一模型報告
每個 LLM 模型會生成：
- **Excel 格式**：`AQUASKY_AIQA_{模型名}_{時間戳}.xlsx`
- **Markdown 格式**：`AQUASKY_AIQA_{模型名}_{時間戳}.md`

### 綜合分析報告
- **交叉分析報告**：`AEO_detailed_cross_analysis_{日期}.md`
- **統計報告**：`AQUASKY_AIQA_STATS_{時間戳}.json`
- **品質檢查報告**：`*_quality_check.md`

### 檔案命名規則
```
格式：AQUASKY_AIQA_{模型名稱}_{YYYYMMDD}_{HHMMSS}.{副檔名}
範例：AQUASKY_AIQA_kimi_k2_free_20250718_013045.xlsx
```

## 📈 核心指標

### 品質評估標準
- **品牌識別度**: 優秀 ≥80%, 良好 ≥60%, 普通 ≥40%
- **官網引用率**: 優秀 ≥60%, 良好 ≥40%, 普通 ≥20%  
- **具體資訊率**: 優秀 ≥80%, 良好 ≥60%, 普通 ≥40%
- **泛化回答率**: 優秀 ≤20%, 良好 ≤40%, 普通 ≤60%

### KPI 目標設定
- **短期目標 (1個月)**：品牌提及率 >60%，官網引用率 >40%
- **中期目標 (3個月)**：品牌提及率 >80%，官網引用率 >60%
- **長期目標 (6個月)**：品牌提及率 >90%，官網引用率 >80%

## ⚙️ 系統配置

### 批次處理設定 (`batch_config.py`)
```python
BATCH_SETTINGS = {
    "max_retries": 3,                    # 最大重試次數
    "retry_delay": 5,                    # 重試間隔（秒）
    "pause_between_questions": 2,        # 問題間暫停（秒）
    "pause_between_models": 3,           # 模型間暫停（秒）
    "auto_save_interval": 5,             # 每 5 個問題自動存檔
}
```

### 系統訊息類型
- `default`：通用助理
- `technical`：技術專家  
- `sales`：銷售顧問
- `comparison`：行業分析師

## 🔍 監控與日誌

### 進度追蹤
- 即時顯示處理進度
- 自動保存進度到 `batch_progress.json`
- 支援中斷後繼續執行

### 日誌系統
- 詳細的執行日誌保存在 `logs/` 目錄
- 包含成功/失敗統計
- 錯誤詳情和重試記錄

## 📅 執行時間預估

- **單個問題單個模型**：約 10-30 秒
- **20 個問題 × 8 個模型**：約 30-60 分鐘
- **實際時間**：取決於網路狀況和 API 回應速度

## 🛠️ 故障排除

### 常見問題

1. **API Key 錯誤**
   ```bash
   python update_api_key.py
   ```

2. **程式中斷**
   - 按 `Ctrl+C` 安全中斷
   - 重新執行會自動繼續

3. **找不到報告檔案**
   ```bash
   ls outputs/*日期*
   ```

4. **效能優化**
   - 網路穩定時可減少暫停時間
   - 大量處理時建議分批執行
   - 定期清理舊的輸出檔案

## 👥 使用者角色

| 角色 | 需求 |
|------|------|
| 行銷/品牌團隊 | 監控市場聲量與品牌一致性 |
| 產品/技術主管 | 了解技術問題的回答正確度 |
| 採購/業務 | 評估競品比較與商業優勢 |

## 🔄 版本更新

### v2.0 特性
- 支援 8 種 LLM 模型
- 標準化交叉分析系統
- 自動品質驗證機制
- 斷點續跑功能
- 智能檔案命名系統

### 未來規劃
- 趨勢分析功能
- 自動化排程系統
- 多語言支援
- Web 介面管理

## 📞 技術支援

如遇到問題，請按順序檢查：
1. 日誌檔案中的錯誤訊息 (`logs/` 目錄)
2. 進度檔案中的狀態 (`batch_progress.json`)
3. API Key 的有效性 (`config.ini`)
4. 網路連線狀態

## 📄 相關文檔

- [PRD_自動黃金問題問答工具.md](PRD_自動黃金問題問答工具.md) - 產品需求文檔
- [README_BATCH.md](README_BATCH.md) - 批次處理系統說明
- [README_ANALYSIS_STANDARDS.md](README_ANALYSIS_STANDARDS.md) - 分析標準化指南
- [AQUASKY AEO 監控專案 - 黃金問題庫 V2.0.md](AQUASKY%20AEO%20監控專案%20-%20黃金問題庫%20V2.0.md) - 問題庫

## 📜 授權條款

本專案採用 MIT 授權條款。詳見 [LICENSE](LICENSE) 檔案。

---

**維護者**: AQUASKY AEO 監控團隊  
**最後更新**: 2025-09-09  
**版本**: 2.0  

*專為 AQUASKY 品牌監控與 AI 問答質量分析而設計的企業級解決方案。*