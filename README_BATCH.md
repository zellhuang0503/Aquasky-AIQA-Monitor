# AQUASKY AIQA Monitor — 多 LLM 批次分析系統

## 系統特色

- 8 款主流 LLM 並行批次測試與統計
- 問題、日期、模型代號自動化命名輸出
- 中斷續跑與自動儲存，降低資料遺失
- 失敗重試與進度追蹤，附詳細日誌

## 支援的 LLM 模型（代號）
1. DeepSeek Chat v3.1 `deepseek/deepseek-chat-v3.1`
2. GPT-5 Mini `openai/gpt-5-mini`
3. Gemini 2.5 Flash `google/gemini-2.5-flash`
4. Claude Sonnet 4 `anthropic/claude-sonnet-4`
5. Llama 3.1 8B `meta-llama/llama-3.1-8b-instruct`
6. Mistral Small 3.2 24B `mistralai/mistral-small-3.2-24b-instruct`
7. Perplexity Sonar Pro `perplexity/sonar-pro`
8. Grok 3 Mini Beta `x-ai/grok-3-mini-beta`

## 專案結構

```
AQUASKY-AIQA-Monitor/
├─ src/
│  ├─ main_batch.py          # 批次主程式
│  ├─ batch_processor.py     # 批次流程邏輯
│  ├─ llm_client.py          # LLM 客戶端
│  └─ report_generator.py    # 報告彙整器
├─ batch_config.py           # 批次設定
├─ batch_progress.json       # 進度追蹤（自動維護）
├─ outputs/                  # 輸出（xlsx/md/json）
├─ logs/                     # 執行日誌
└─ requirements.txt          # 相依套件
```

## 使用方式

### 1) 基本執行
```bash
python src/main_batch.py
```

### 2) 互動式選單
- A. 使用預設 8 款模型跑測試
- B. 手動選擇模型組合
- C. 使用推薦 3 款模型快速開始

### 3) 續跑／中斷恢復
```bash
# 直接執行即可自動檢測並續跑
python src/main_batch.py
```

## 輸出檔說明

### 單一模型輸出
- Excel：`AQUASKY_AIQA_{模型}_{時間戳}.xlsx`
- Markdown：`AQUASKY_AIQA_{模型}_{時間戳}.md`

### 總結輸出
- 綜合 Excel：`AQUASKY_AIQA_SUMMARY_{時間戳}.xlsx`
- 綜合 Markdown：`AQUASKY_AIQA_SUMMARY_{時間戳}.md`
- 統計 JSON：`AQUASKY_AIQA_STATS_{時間戳}.json`

### 檔名規則
```
樣式：AQUASKY_AIQA_{模型名稱}_{YYYYMMDD}_{HHMMSS}.{副檔名}
範例：AQUASKY_AIQA_kimi_k2_free_20250718_013045.xlsx
```

## 批次設定（`batch_config.py`）
```python
BATCH_SETTINGS = {
    "max_retries": 3,             # 最大重試次數
    "retry_delay": 5,             # 重試延遲（秒）
    "pause_between_questions": 2, # 題與題之間的暫停（秒）
    "pause_between_models": 3,    # 模型之間的暫停（秒）
    "auto_save_interval": 5,      # 每 5 題自動儲存
}
```

### 系統訊息型態
- `default`：通用
- `technical`：技術諮詢
- `sales`：銷售顧問
- `comparison`：產業顧問

## 進度與日誌
- 進度：即時顯示，並持久化於 `batch_progress.json`
- 日誌：詳細執行紀錄儲存於 `logs/`

## 疑難排解
1. API Key 錯誤
   ```bash
   python update_api_key.py
   ```
2. 程式中斷
   - 使用 `Ctrl+C` 安全中斷
   - 重新執行將自動續跑
3. 檢查進度
   ```bash
   python simple_monitor.py
   ```

## 效能建議與策略
- 先小量測試（推薦 3 模型），再擴大到 8 模型
- 批次期間保持網路穩定，並預留磁碟空間
- 定期清理歷史輸出檔以加速檔案操作

## 時間估算（參考）
- 單題單模型：10–30 秒
- 20 題 × 8 模型：30–60 分鐘（視網路與 API 擁塞度而定）

## 版本控制建議
```bash
git add .
git commit -m "完成多 LLM 批次分析：測試集 X 次數 Y"
git push
```

---

此系統用於大規模多模型問答測試與彙整分析，支援可重現、可比較、可追蹤的自動化流程。

