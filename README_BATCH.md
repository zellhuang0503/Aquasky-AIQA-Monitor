# AQUASKY AIQA 批次執行

2026-09-22 起以根目錄 `working_models_processor.py` 為唯一維護入口。
`src/main.py` 與 `src/main_batch.py` 為相容轉接入口，參數完全相同。

完整操作說明見 [README.md](README.md)，模型清單見 [LLM測試清單](docs/LLM測試清單_20260922.md)。

```powershell
.\.venv312\Scripts\python.exe working_models_processor.py --dry-run
.\.venv312\Scripts\python.exe working_models_processor.py --run
```

預設 12 題 × 6 家（OpenAI、Google、Perplexity、Claude、Grok、DeepSeek），共 72 次提問。每題立即保存；使用 `--resume outputs/runs/<執行目錄>` 續跑，輸入不符時拒絕混用歷史結果。
認證或餘額錯誤會停止該 API 路由的後續請求，暫時性 HTTP 錯誤至多重試三次。
網路逾時不自動重送，以免重複計費；可檢查後用 `--retry-failed` 明確重試。
每次輸出獨立的 JSON 證據、Markdown 報告與 Excel 明細；不再讀取舊 `batch_progress.json`。

OpenRouter 若在 HTTP 200 內回傳 `finish_reason=error` 且錯誤碼為 429／500／502／503／504，也會至多嘗試三次；中間失敗回應保存在原始證據的 `retry_responses`。
