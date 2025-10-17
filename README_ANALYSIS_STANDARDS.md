# AQUASKY AEO 交叉分析標準作業（SOP）

## 概述
定義 AQUASKY AEO 專案中交叉分析報告的標準流程與品質門檻，確保每次輸出達到一致且可比較的水準。

## 指標與品質標準

### 主要指標（量化）
- 品牌識別度：優 >= 80、良 >= 60、差 < 60
- 官網引用比例：優 >= 60、良 >= 40、差 < 40
- 特定資訊覆蓋：優 >= 80、良 >= 60、差 < 60
- 泛化回避（避免空泛建議）：優 >= 80、良 >= 60、差 < 60

### 報告最低品質要求（定性）
- 最少字數：5,000 字
- 必備章節：至少 8 個主要段落
- 視覺呈現：3–5 個表格或圖示
- 模型比較：至少 3 種比較方式（品質、成本、可用性等）
- 改進建議：至少 10 條可操作建議

## 相關檔案結構

```
AQUASKY-AIQA-Monitor/
├─ templates/
│  └─ cross_analysis_template.md     # 報告模板
├─ scripts/
│  ├─ generate_cross_analysis.py     # 產出交叉分析
│  ├─ analysis_config.py             # 參數與關鍵詞
│  └─ quality_validator.py           # 品質驗證工具
├─ outputs/cross_analysis/
│  ├─ AEO_detailed_cross_analysis_*.md
│  └─ *_quality_check.md
└─ run_standardized_analysis.py      # 主執行器
```

## 使用方式

### 1) 快速執行（推薦）
```bash
python run_standardized_analysis.py
```

### 2) 指定日期執行
```bash
python run_standardized_analysis.py --date 20250829
```

### 3) 逐步執行
```bash
cd scripts
python generate_cross_analysis.py 20250829
python quality_validator.py
```

## 標準流程
1. 載入資料
   - 掃描輸出目錄，尋找各模型報告
   - 驗證資料完整（至少 6 個模型）與命名一致
2. 指標計算
   - 計算品牌識別、官網引用、特定資訊覆蓋等
   - 品質面（正確性、可重現性）與 Token 用量統計
3. 多維比較
   - 成本/效能/品質/辨識度等多維度評比
4. 深度對比
   - 對 5 個關鍵問題進行逐題比較，標示優缺點
5. 報告生成
   - 依模板輸出，含追蹤指標、改善建議與摘要
6. 品質驗證
   - 檢查章節齊備與字數門檻
   - 計算品質分數（0–100）；輸出質檢報告

## 參數設定（`scripts/analysis_config.py`）
```python
# 品牌關鍵詞
brand_keywords = ['aquasky', 'aqua sky', 'AQUASKY']

# 官網關鍵詞
website_keywords = ['aquaskyplus.com', 'aquasky.com']

# 特定資訊關鍵詞
specific_keywords = ['規格', '詳細', '專業', '步驟', '案例']

# 泛化回避關鍵詞（避免空話）
generic_keywords = ['不確定', '建議聯繫', '請聯絡']

# 品質門檻
QUALITY_STANDARDS = {
    'brand_recognition': {'excellent': 80, 'good': 60, 'poor': 40},
    'website_mention':   {'excellent': 60, 'good': 40, 'poor': 20},
    'specific_info':     {'excellent': 80, 'good': 60, 'poor': 40},
}
```

## KPI 目標
- 短期（1 週）：識別度 > 60%，官網引用 > 40%，特定資訊 > 70%
- 中期（3 週）：識別度 > 80%，官網引用 > 60%，特定資訊 > 85%
- 長期（6 週）：識別度 > 90%，官網引用 > 80%，特定資訊 > 95%

## 品質檢查清單
必檢項目：
1. 內容字數 >= 5,000
2. 章節完整（>= 8 章）
3. 表格/圖表 >= 3
4. 比較維度 >= 3
5. 改進建議 >= 10
6. KPI 指標計算齊全
7. 結論章節完整

評分等級：
- 90–100：優秀
- 80–89：良好
- 70–79：合格
- 60–69：待改善
- <60：不合格

## 疑難排解
1. 找不到指定日期輸出
   ```bash
   ls outputs/*20250829*
   ```
2. 模型名稱映射錯誤
   - 檢查 `analysis_config.py` 中的 `MODEL_NAME_MAPPING`
3. 品質分數偏低
   - 補齊缺失章節或數據、增加具體建議
4. 編碼問題
   ```bash
   # 確保使用 UTF-8
   python -c "import locale; print(locale.getpreferredencoding())"
   ```

## 定期運行
- 每週執行並回顧趨勢
- Windows 範例：
```bash
schtasks /create /tn "AQUASKY_Analysis" /tr "python run_standardized_analysis.py" /sc weekly /d MON /st 10:00
```

## 版本資訊
- 維護單位：AQUASKY AEO 團隊
- 最後更新：2025-08-29
- 版本：1.0

