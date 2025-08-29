# AQUASKY AEO 交叉分析標準化指南

## 概述

本指南定義了 AQUASKY AEO 監控專案交叉分析報告的標準化流程，確保每次分析都達到一致的高品質水準。

## 🎯 品質標準

### 核心指標
- **品牌識別度**: 優秀 ≥80%, 良好 ≥60%, 普通 ≥40%
- **官網引用率**: 優秀 ≥60%, 良好 ≥40%, 普通 ≥20%  
- **具體資訊率**: 優秀 ≥80%, 良好 ≥60%, 普通 ≥40%
- **泛化回答率**: 優秀 ≤20%, 良好 ≤40%, 普通 ≤60%

### 報告品質要求
- **最少字數**: 5,000 字
- **必需章節**: 8 個主要章節
- **問題分析**: 至少分析 3-5 個關鍵問題
- **模型排名**: 至少 3 種排名方式
- **改善建議**: 至少 10 個具體建議

## 📁 檔案結構

```
AQUASKY-AIQA-Monitor/
├── templates/
│   └── cross_analysis_template.md      # 報告模板
├── scripts/
│   ├── generate_cross_analysis.py      # 報告生成器
│   ├── analysis_config.py              # 分析配置
│   └── quality_validator.py            # 品質驗證器
├── outputs/cross_analysis/
│   ├── AEO_detailed_cross_analysis_*.md
│   └── *_quality_check.md
└── run_standardized_analysis.py        # 主執行器
```

## 🚀 使用方法

### 1. 快速執行 (推薦)
```bash
python run_standardized_analysis.py
```

### 2. 指定日期執行
```bash
python run_standardized_analysis.py --date 20250829
```

### 3. 手動執行各步驟

#### 生成報告
```bash
cd scripts
python generate_cross_analysis.py 20250829
```

#### 驗證品質
```bash
cd scripts  
python quality_validator.py
```

## 📊 標準化流程

### 步驟 1: 數據載入與驗證
- 自動尋找指定日期的所有模型報告檔案
- 驗證數據完整性 (至少 6 個模型)
- 標準化模型名稱映射

### 步驟 2: 指標計算與分析
- 計算品牌識別度、官網引用率等核心指標
- 分析回答品質 (具體性、泛化程度)
- Token 使用效率統計

### 步驟 3: 多維度排名
- **效率排名**: 按 Token 使用量排序
- **品質排名**: 按綜合品質分數排序  
- **品牌識別排名**: 按品牌提及率排序

### 步驟 4: 問題深度分析
- 選取前 5 個關鍵問題進行詳細分析
- 比較各模型回答差異
- 識別最佳與最差回答

### 步驟 5: 報告生成
- 使用標準化模板生成完整報告
- 包含執行摘要、數據分析、改善建議
- 自動計算預期改善效果

### 步驟 6: 品質驗證
- 檢查報告完整性 (章節、字數、數據)
- 計算品質分數 (0-100)
- 生成品質檢查報告

## 🔧 配置說明

### 關鍵詞配置 (`analysis_config.py`)
```python
# 品牌關鍵詞
brand_keywords = ['aquasky', 'aqua sky', 'AQUASKY']

# 官網關鍵詞  
website_keywords = ['aquaskyplus.com', 'aquasky.com']

# 具體資訊關鍵詞
specific_keywords = ['具體', '詳細', '專業', '技術', '規格']

# 泛化回答關鍵詞
generic_keywords = ['無法確認', '建議聯繫', '請聯絡']
```

### 品質標準配置
```python
QUALITY_STANDARDS = {
    'brand_recognition': {'excellent': 80, 'good': 60, 'poor': 40},
    'website_mention': {'excellent': 60, 'good': 40, 'poor': 20},
    'specific_info': {'excellent': 80, 'good': 60, 'poor': 40}
}
```

## 📈 KPI 目標設定

### 短期目標 (1個月內)
- 品牌提及率: >60%
- 官網引用率: >40%
- 具體資訊率: >70%

### 中期目標 (3個月內)  
- 品牌提及率: >80%
- 官網引用率: >60%
- 具體資訊率: >85%

### 長期目標 (6個月內)
- 品牌提及率: >90%
- 官網引用率: >80%
- 具體資訊率: >95%

## 🔍 品質檢查項目

### 必需檢查
1. **內容長度**: ≥5,000 字
2. **章節完整性**: 8 個必需章節
3. **數據指標**: ≥10 個量化數據
4. **模型排名**: ≥3 種排名方式
5. **改善建議**: ≥10 個具體建議
6. **KPI 目標**: 短中長期目標設定
7. **結論完整性**: 完整的結論章節

### 品質分數計算
- 90-100: 🏆 優秀
- 80-89: 🥈 良好  
- 70-79: 🥉 及格
- 60-69: ⚠️ 待改善
- <60: ❌ 不及格

## 🛠️ 故障排除

### 常見問題

#### 1. 找不到報告檔案
```bash
# 檢查 outputs 目錄是否存在對應日期的檔案
ls outputs/*20250829*
```

#### 2. 模型名稱映射錯誤
- 檢查 `analysis_config.py` 中的 `MODEL_NAME_MAPPING`
- 確保檔名格式符合預期

#### 3. 品質分數過低
- 檢查必需章節是否完整
- 確認數據指標是否充足
- 補充具體的改善建議

#### 4. 編碼問題
```bash
# 確保使用 UTF-8 編碼
python -c "import locale; print(locale.getpreferredencoding())"
```

## 📅 執行排程

### 建議執行頻率
- **每週執行**: 跟隨模型批次處理後立即執行
- **月度回顧**: 比較多週數據趨勢
- **季度評估**: 檢視 KPI 達成情況

### 自動化設定
```bash
# Windows 工作排程器
schtasks /create /tn "AQUASKY_Analysis" /tr "python run_standardized_analysis.py" /sc weekly /d MON /st 10:00
```

## 🔄 版本更新

### v1.0 特性
- 標準化報告模板
- 自動品質驗證
- 多維度模型排名
- 詳細問題分析
- 具體改善建議

### 未來規劃
- 趨勢分析功能
- 自動化排程
- 多語言支援
- API 整合

---

**維護者**: AQUASKY AEO 監控團隊  
**最後更新**: 2025-08-29  
**版本**: 1.0
