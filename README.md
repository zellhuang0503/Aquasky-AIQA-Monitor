# AQUASKY AIQA Monitor

以固定題庫測試多家 LLM API 的品牌提及與網站引用，保存原始證據。這是 API 觀測，不等於 ChatGPT 網頁版、Gemini App 或 Google AI Overviews 的結果。

## 2026-09-24 客戶會議

- [26 頁離線 HTML 簡報](presentations/20260924/AQUASKY_AIQA_客戶會議簡報_20260924.html)：包含完整十二題、A／B 分類比較、72 筆可搜尋問答、補強建議與外部佐證渠道。從 GitHub 下載檔案後用瀏覽器開啟。
- [客戶寄送 ZIP](presentations/20260924/AQUASKY_AIQA_客戶會議資料_20260924.zip)：只有 HTML 與客戶使用說明，先解壓縮再開啟。
- [逐頁講稿](presentations/20260924/逐頁講稿.md)、[操作與更新方式](presentations/20260924/使用說明.md)。
- [簡報證據複核](docs/20260923_簡報證據複核.md)、[保留的完整測試批次](outputs/runs/combined_20260922_012711_656878/)。

**72/72 是 API 回傳狀態，不是回答正確率。**簡報另標記 Grok 四筆僅開場、Perplexity B7 錯認品牌、Gemini A4 名稱誤寫。A 組文字提及為 11/30；排除網址後的 AQUASKY Plus 正文提及為 3/72，皆在已點名品牌的 B 組。提及不等於正確推薦。

本次只將已複核的合併批次納入版控，其他執行輸出、金鑰及本機環境仍排除。歷史指標的限制另見遠端既有的 `指標勘誤與重算說明.md`，不要與本次基準混算。

## 本次題庫

使用者於 2026-09-22 指定 `Aquasky Edge AEO On Cloudflare Project/docs/28-AI引用實測問句-會議討論稿.md`。
已完整複製為 `config/questions_20260922.md`，來源與 SHA-256 記錄於 `config/question_source.json`。
文件雖註記「候選 12 題圈 10 題」，目前沒有圈選標記，因此使用完整 12 題：A1–A5（無品牌）、B1–B7（有品牌）。原始問題文字保持不變，每題獨立對話。

## 執行（PowerShell）

在倉庫根目錄執行。本機已確認 `.venv312` 的 requests、pandas、openpyxl 可載入；舊 `.venv` 的 NumPy 載入失敗。

```powershell
# 本機預檢：不呼叫 API
.\.venv312\Scripts\python.exe working_models_processor.py --dry-run

# 預設六家，各 12 題（會產生 API 與搜尋費用）
.\.venv312\Scripts\python.exe -u working_models_processor.py --run

# 只測指定題目與模型
.\.venv312\Scripts\python.exe working_models_processor.py --run --models google,perplexity --question-ids A1,B1

# 明確指定六家（與預設相同）
.\.venv312\Scripts\python.exe working_models_processor.py --run --models all

# 中斷續跑：題庫、模型、提示詞與 token 上限必須與原執行一致
# 若續跑舊三家批次，需加 --models openai,google,perplexity
.\.venv312\Scripts\python.exe working_models_processor.py --run --resume outputs/runs/<執行目錄>
# 如要重新嘗試先前失敗或截斷項目，加 --retry-failed
```

不帶 `--run` 預設只做本機預檢。`src/main.py`、`src/main_batch.py` 都轉交同一個維護中的入口，不再使用舊測試模式與舊進度。

API Key 放在未納入 Git 的 `config.ini`：`[api_keys] openrouter_api_key`、`perplexity_api_key`。
新電腦先用 Python 3.12 建立虛擬環境，再 `pip install -r requirements.txt`。

## 模型設定

單一設定來源：`config/working_models.json`。六家全部預設啟用：OpenAI、Google Gemini、Perplexity、Claude、Grok、DeepSeek。
詳細清單與選擇理由見 `docs/LLM測試清單_20260922.md`。

OpenAI、Google 透過 OpenRouter 明確要求原廠 native 搜尋；Perplexity 使用官方 Sonar API。
DeepSeek 採 Exa 搜尋，必須分開標示，不能當成 DeepSeek 消費者產品的搜尋結果。
模型出現在公開目錄不表示本機金鑰有使用權限；以每次 API 回應為準。

## 輸出與指標

每次建立新的 `outputs/runs/YYYYMMDD_HHMMSS_microseconds/`，不覆蓋歷史報告：

- `manifest.json`：題庫全文、模型、搜尋引擎、提示詞、參數、雜湊與時間。
- `raw/<model>_<question>.json`：送出的請求內容與完整 API 回應（不含金鑰／HTTP headers）。
- `results.json`：每題完成後立即存檔的結構化結果。
- `report.md`：分組統計及逐題回答、引用來源。
- `answers.xlsx`：可篩選的回答與引用明細。

成功分母為實際預定題數，輸出截斷與空回答不算完整成功。
A 組統計品牌提及與官方引用；B 組統計官方引用，回答正確性仍需人工對照官網／客戶提供資料。
品牌提及不等於推薦或 Share of Voice。官方引用只計結構化 citations/annotations 中的 `aquaskyplus.com` 及其子網域，普通回答文字中的網址另存，不當作來源證據。
比例的分母為各組完整回答數；失敗與截斷另列，不把服務錯誤當成品牌不存在。
Google 搜尋引用的跳轉網址會以 HEAD 查核 Location，不抓取目標網站；原始網址與解析目標均保留，未解析成功的筆數另列。
搜尋已啟用不保證每題都有引用；無結構化引用也不能推論模型沒有執行搜尋。

本輪題庫與模型已更新，應視為新基準；不直接與 2025 年舊題库混算趨勢。
舊 `run_standardized_analysis.py` 和 `scripts/generate_cross_analysis.py` 保留給歷史資料，仍有固定 20 題與啟發式敘述，勿用來分析本輪。

## 驗證

```powershell
.\.venv312\Scripts\python.exe -m unittest discover -s tests -v
```

修復前檔案備份於 `outputs/repair_backup_20260922/`。本次沒有更動外部 Cloudflare 專案或舊問答輸出。

## 分批結果整合

`scripts/combine_runs.py` 可整合不同模型的批次；會核對題庫、提示詞、token 上限與目標網域一致，拒絕重複模型或尚未跑完的批次。整合報告保留來源批次時間與每筆原始回應，不能用於 `--resume`。

```powershell
.\.venv312\Scripts\python.exe scripts/combine_runs.py outputs/runs/<批次一> outputs/runs/<批次二>
```
