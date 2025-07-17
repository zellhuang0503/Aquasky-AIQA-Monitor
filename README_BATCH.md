# AQUASKY AIQA Monitor - 多 LLM 自動化批次處理系統

## 🚀 系統特色

### ✨ 核心功能
- **8 種 LLM 自動化處理**：支援多種主流 AI 模型同時處理問題
- **智能檔案命名**：自動包含日期、時間、LLM 名稱的檔案命名
- **斷點續跑**：程式中斷後可從上次停止的地方繼續執行
- **自動存檔**：每處理 5 個問題自動保存，避免資料遺失
- **錯誤重試**：API 調用失敗時自動重試，提高成功率
- **進度追蹤**：實時顯示處理進度和統計資訊

### 🤖 支援的 LLM 模型
1. **月之暗面 Kimi K2** (免費版) - `kimi-k2-free`
2. **DeepSeek Chimera** (免費版) - `deepseek-chimera-free`
3. **Google Gemini 2.5 Flash Lite** - `gemini-2.5-flash-lite`
4. **OpenAI GPT-4o Mini** (高品質) - `gpt-4o-mini-high`
5. **Anthropic Claude Sonnet 4** - `claude-sonnet-4`
6. **Mistral Devstral** (中等版本) - `devstral-medium`
7. **xAI Grok 3** - `grok-3`
8. **Perplexity Sonar Pro** - `perplexity-sonar-pro`

## 📁 檔案結構

```
AQUASKY-AIQA-Monitor/
├── src/
│   ├── main_batch.py          # 新的批次處理主程式
│   ├── batch_processor.py     # 批次處理核心邏輯
│   ├── llm_client.py          # LLM 客戶端（已修復）
│   └── report_generator.py    # 報告生成器（已增強）
├── batch_config.py            # 批次處理配置檔案
├── batch_progress.json        # 進度追蹤檔案（自動生成）
├── outputs/                   # 輸出目錄
│   ├── AQUASKY_AIQA_kimi_k2_free_20250718_010000.xlsx
│   ├── AQUASKY_AIQA_kimi_k2_free_20250718_010000.md
│   ├── AQUASKY_AIQA_SUMMARY_20250718_010000.xlsx
│   └── AQUASKY_AIQA_STATS_20250718_010000.json
└── logs/                      # 日誌目錄
    └── batch_process_20250718_010000.log
```

## 🔧 使用方法

### 1. 基本使用
```bash
# 執行新的批次處理系統
python src/main_batch.py
```

### 2. 互動式選擇
程式會提供以下選項：
- **A. 使用所有 8 個模型**：完整測試所有支援的 LLM
- **B. 自訂選擇模型**：手動選擇特定的模型組合
- **C. 使用預設模型**：快速開始（前 3 個推薦模型）

### 3. 斷點續跑
如果程式中斷（網路問題、手動停止等）：
```bash
# 重新執行相同命令，程式會自動檢測並繼續
python src/main_batch.py
```

## 📊 輸出檔案說明

### 單一模型報告
每個 LLM 模型會生成獨立的報告檔案：
- **Excel 格式**：`AQUASKY_AIQA_{模型名}_{時間戳}.xlsx`
- **Markdown 格式**：`AQUASKY_AIQA_{模型名}_{時間戳}.md`

### 綜合報告
處理完成後會生成：
- **綜合 Excel**：`AQUASKY_AIQA_SUMMARY_{時間戳}.xlsx`
- **綜合 Markdown**：`AQUASKY_AIQA_SUMMARY_{時間戳}.md`
- **統計報告**：`AQUASKY_AIQA_STATS_{時間戳}.json`

### 檔案命名規則
```
格式：AQUASKY_AIQA_{模型名稱}_{YYYYMMDD}_{HHMMSS}.{副檔名}
範例：AQUASKY_AIQA_kimi_k2_free_20250718_013045.xlsx
```

## ⚙️ 系統配置

### 重要設定（在 `batch_config.py` 中）
```python
BATCH_SETTINGS = {
    "max_retries": 3,                    # 最大重試次數
    "retry_delay": 5,                    # 重試間隔（秒）
    "pause_between_questions": 2,        # 問題間暫停（秒）
    "pause_between_models": 3,           # 模型間暫停（秒）
    "auto_save_interval": 5,             # 每 5 個問題自動存檔
}
```

### 自訂系統訊息
可以根據不同需求選擇系統訊息類型：
- `default`：通用助理
- `technical`：技術專家
- `sales`：銷售顧問
- `comparison`：行業分析師

## 🔍 監控和日誌

### 進度追蹤
- 即時顯示處理進度
- 自動保存進度到 `batch_progress.json`
- 支援中斷後繼續執行

### 日誌系統
- 詳細的執行日誌保存在 `logs/` 目錄
- 包含成功/失敗統計
- 錯誤詳情和重試記錄

## 🛠️ 故障排除

### 常見問題

1. **API Key 錯誤**
   ```bash
   # 使用 API Key 更新工具
   python update_api_key.py
   ```

2. **程式卡住**
   - 按 `Ctrl+C` 安全中斷
   - 重新執行會自動繼續

3. **檢查進度**
   ```bash
   # 使用監控工具
   python simple_monitor.py
   ```

### 效能優化建議
- 網路穩定時可減少暫停時間
- 大量處理時建議分批執行
- 定期清理舊的輸出檔案

## 📈 預期執行時間

### 時間估算
- **單個問題單個模型**：約 10-30 秒
- **20 個問題 × 8 個模型**：約 30-60 分鐘
- **實際時間**：取決於網路狀況和 API 回應速度

### 建議執行策略
1. **測試階段**：先用 3 個模型測試
2. **正式執行**：使用全部 8 個模型
3. **定期執行**：每週或每月更新問題庫

## 🎯 最佳實踐

### 執行前準備
1. 確認網路連線穩定
2. 檢查 API Key 有效性
3. 確保有足夠的磁碟空間

### 執行中監控
1. 觀察日誌輸出
2. 檢查錯誤率
3. 必要時調整暫停時間

### 執行後分析
1. 檢查統計報告
2. 比較不同模型的回答品質
3. 根據結果調整問題庫

## 🔄 版本控制建議

完成重要階段後建議提交到 GitHub：
```bash
git add .
git commit -m "完成多 LLM 批次處理 - 處理 X 個問題"
git push
```

## 📞 技術支援

如遇到問題，請檢查：
1. 日誌檔案中的錯誤訊息
2. 進度檔案中的狀態
3. API Key 的有效性

---

*此系統專為 AQUASKY AIQA 監控專案設計，支援大規模自動化 AI 問答處理。*
