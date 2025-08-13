# AQUASKY AEO 交叉分析報告（依據《AQUASKY 客戶 AEO 監控系統建構方案-20250716.md》）

說明：我先讀取並比對了以下三個檔案，依方案中的目標與評估準則進行交叉分析，並整理成一份可執行的行動建議。
- 文件目標與準則：`E:\CascadeProjects\Aquasky-AIQA-Monitor\AQUASKY 客戶 AEO 監控系統建構方案-20250716.md`
- LLM 問答量化：`E:\CascadeProjects\Aquasky-AIQA-Monitor\outputs\aiqa_report_data.csv`
- 伺服器/爬蟲日誌分析：`E:\CascadeProjects\Aquasky-AIQA-Monitor\outputs\log_analysis\report.md`

我也有參考你提供的專案目的記憶（每週以固定 20 題向多個 LLM 詢問、產生 Markdown/Excel 報告等），以確保分析方向一致。

---

## 一、執行摘要（Executive Summary）

- 依 `aiqa_report_data.csv` 顯示，多數 LLM 回答對 AQUASKY 的專屬資訊掌握度低，常出現「無法確認/建議聯繫官方」的泛化回應，缺少明確引用 `aquaskyplus.com` 或相關官方來源。
- 依 `log_analysis/report.md` 顯示，目前僅觀測到 DuckDuckGo（DuckAssist）爬蟲請求（36 次），熱門抓取集中於 `robots.txt` 與多篇 `news-detail.php` 頁面。未見 Google-Extended、GPTBot、PerplexityBot 等主流生成式 AI 相關爬蟲造訪跡象。
- 綜合判斷：AQUASKY 的內容尚未被主流 LLM 廣泛收錄與引用，AEO 能見度偏低。核心原因包括：
  - 官方站內容對「黃金問題」的可引用性與結構化標註不足（缺 FAQ/Organization/Product/Article 等 Schema、缺系統化關鍵敘述）。
  - 站點對生成式 AI 爬蟲的可及性與允許策略可能不足（僅見 DuckAssist 檢索，其他主流 AI 爬蟲未見）。
  - 內容聚焦點與 LLM 問題庫不完全對齊（如願景、ESG、OEM/ODM 能力、QC 流程、專利/認證、通路政策、交期/MOQ/保固/付款等）。

---

## 二、資料觀察重點

- 「AI 答案生成監控」面（來自 `aiqa_report_data.csv`）
  - __模型覆蓋__：2025-07-26 有 `anthropic_claude-3.5-sonnet` 回答；2025-08-10 有 `x-ai_grok-3-mini-beta` 回答。
  - __回答特徵__：
    - 多題呈現「缺少 AQUASKY 具體資訊」的泛化建議，如「無法確認、建議聯繫官方」。
    - 缺少對 `aquaskyplus.com` 的引用或外部可信來源的佐證鏈接。
    - 針對「願景與藍圖、ESG、OEM/ODM 能力、QC 測試流程、製造技術/專利、認證、經銷條件、MOQ/Lead Time/保固/付款條件、製造商或貿易商身份」等題型，回答多不具體或無引證。
  - __推論__：AEO 市佔與可引用性偏低；AI 模型對 AQUASKY 的高置信內容庫尚未建立。

- 「AI 爬蟲日誌分析」面（來自 `log_analysis/report.md`）
  - __LLM Bot 請求總數__：36 次，皆為 DuckDuckGo（DuckAssist）。
  - __熱門抓取__：`/robots.txt`（13 次）與多篇 `news-detail.php`；另有 `js/bootstrap.min.js`。
  - __未觀測到__：Google-Extended（Google AI）、OpenAI GPTBot、PerplexityBot、Anthropic（ClaudeBot / anthropic-ai）、CCBot、Amazonbot 等。
  - __推論__：主流 AI 爬蟲尚未常態造訪或被允許有效抓取；內容曝光主要偏向 DuckAssist 來源，整體 AEO 爬取面偏窄。

---

## 三、與《建構方案》目標對照的診斷

- __模組一（AI 爬蟲日誌分析）__：已具雛形，但需擴大 User-Agent 覆蓋、反向 DNS 驗證、指標化與趨勢化（如「新內容首次被抓取時間」「各 Bot 週/月趨勢」「前 20 熱門抓取頁面」）。
- __模組二（AI 答案生成監控）__：資料已產生，但答案品質與引用率低，顯示「黃金問題庫」與站內可引用內容的對齊度需要提升，並需建立明確的「AEO 內容基礎建設」（FAQ、權威頁面、Schema 結構化標註）。
- __自動化與報告__：已有 CSV/MD 報告產出，建議補齊指標定義與 KPI 目標，並建立時間序列比較。

---

## 四、根因分析

- __內容層__：缺少對黃金問題的「權威答案頁」與 FAQ 結構；缺關鍵事實陳述（願景、ESG、OEM/ODM 能力、QC、專利、認證、通路政策、Lead Time、MOQ、保固、付款等）的清楚條列與可引用片段。
- __結構化層__：缺少 Schema.org 的 `Organization`、`Product`、`FAQPage`、`Article` 等 JSON-LD；缺 `hreflang`、清晰的 `sitemap.xml` 覆蓋與 `lastmod`；內文可引點（anchorable facts）不足。
- __抓取與權限層__：多數主流 LLM 爬蟲未見造訪，可能與 `robots.txt`、防護策略或未主動釋出「對 LLM 友善政策」（如 llms.txt、Allow 清單）有關。
- __監測層__：Log 分析目前僅 DuckAssist；監測指標與偵測規則需擴充，避免漏抓 AI Bot 族群。

---

## 五、行動建議

### A. 未來 7 天（Quick Wins）
- __內容落地（對齊黃金問題）__
  - 建立 8–12 篇「權威主題頁」與 1–2 篇 FAQ 線上頁（中英文），對應下列題型：
    - 公司願景與五年藍圖、ESG 實踐
    - OEM/ODM 能力與流程、關鍵製造技術/專利、QC 測試（含壓力循環測試）
    - 認證（NSF/CE/WRAS/ISO）清單與文件索引頁
    - 經銷條件與定價結構、交付前置時間（Lead Time）、MOQ、保固與售後、付款條件
    - AQUASKY 與同級品牌比較的「原則性聲明」與可公開對比項（避免敏感價格，著重規格/應用/優勢）
- __技術基建__
  - 在上述頁面加入 JSON-LD：
    - `Organization`（品牌權威資訊）、`FAQPage`（針對黃金問題）、`Product`（關鍵產品線原則資訊）、`Article`（新聞/部落格）
  - 檢視並優化 `sitemap.xml`，納入新頁、補齊 `lastmod`，中英頁皆入列；確認 `hreflang`。
- __對 LLM 友善的抓取政策__
  - 檢查並優化 `robots.txt`：
    - 明確 Allow：Google-Extended、GPTBot、Anthropic/ClaudeBot（anthropic-ai）、PerplexityBot、CCBot、Amazonbot、DuckAssist 等主流生成式 AI 爬蟲。
    - 只排除敏感路徑與非內容資源。
  - 規劃新增 `llms.txt`（說明允許/限制、聯絡方式、抓取節率建議），並放於根目錄。
- __監測與報表__
  - 擴充 Log 解析規則：加入上述 Bot UA 與反向 DNS 驗證；日更匯出「各 Bot 次數、頁面 Top20、首見時間、重抓頻率」。
  - 在 CSV 報告中新增欄位：是否提及 AQUASKY、是否附上官網鏈接、引用來源數、答案正確性標註（人工抽樣）。

### B. 1–2 個月（中程建設）
- __內容與結構化滾動優化__
  - 完成 20–30 篇主題頁與 FAQ 系列，確保黃金問題全覆蓋，並持續以 JSON-LD 結構化。
  - 將 `news-detail.php` 內容升級為具備 `Article` 結構化的長青內容頁（必要時重構 URL 與內文層級、加目錄與錨點）。
- __外部權威信號__
  - 規劃外部權威引用（產業協會、標準組織、合作案例），建立合理的反向鏈接與第三方引用。
- __監控系統與 KPI 看板__
  - 將模組一、二的結果導入 Looker Studio/Power BI 儀表板，建立週報/旬報/月報。
  - 自動化「模型×問題×語言」矩陣的趨勢追蹤（回答品質、品牌提及、官網引用）。

---

## 六、衡量方式與 KPI（建議下階段目標）

- __爬蟲面（4 週內）__
  - Bot 覆蓋數：由 1 種提升到 ≥4 種（含 Google-Extended、GPTBot、Perplexity、Anthropic）。
  - LLM Bot 請求量：≥200/週。
  - 新頁面「首次被 LLM 抓取」時間：≤72 小時。
- __答案面（4–8 週內）__
  - 前 10 題黃金問題：≥60% 的回答「明確提及 AQUASKY」、≥40% 附 `aquaskyplus.com` 引用。
  - 答案正確率（人工抽樣）：≥80%。
- __內容面__
  - 完成 ≥20 篇權威主題/FAQ 頁，100% 具 JSON-LD 結構化與可引述片段。

---

## 七、風險與對策

- __Bot 流量增加__：以 `robots.txt`/`llms.txt` 規範抓取節率；監控流量峰值與快取策略。
- __內容正確性__：建立法遵與專業審校流程（特別是專利、認證、保固等敘述）。
- __比較內容敏感性__：避免價格直接比較，以規格、應用場景、品質流程為主。

---

## 八、立即待辦清單（給下週一 09:00 排程前）

- __[內容]__ 建立 8–12 篇核心主題頁與 1–2 篇 FAQ（中英），對齊黃金問題。
- __[Schema]__ 為新頁面加入 `Organization`/`FAQPage`/`Product`/`Article` JSON-LD。
- __[Sitemap/Hreflang]__ 更新並提交至 GSC/Bing Webmaster，檢查索引狀態。
- __[Robots]__ 檢視並調整 `robots.txt`，允許主流 LLM Bot；新增 `llms.txt` 草案。
- __[Log]__ 擴充 UA 偵測與反向 DNS 驗證；導出週報 Top20 抓取頁面。
- __[監控]__ 在 `aiqa_report_data.csv` 報表流程中加入「品牌提及」「官網引用」「引用數」欄位與評分欄（供後續 Excel/Markdown 報告使用）。

---

### 附錄 A：主流 LLM Bot 名單（用於 UA 偵測與 robots 設定）
- Google-Extended
- GPTBot（OpenAI）
- anthropic-ai（Claude）
- PerplexityBot
- CCBot（Common Crawl）
- Amazonbot
- DuckAssist（DuckDuckGo）
- 其他依實際名單持續擴充

---

### 附錄 B：建議 `robots.txt` 原則（示意）
- 允許主流 LLM Bot 抓取主要內容區域（/、/products、/news、/blog…）
- 僅阻擋敏感/動態/後台路徑
- 指向 `sitemap.xml`
- 與 `llms.txt` 政策一致

---

### 附錄 C：建議 Schema 佈署（示意）
- `Organization`：品牌資訊、聯繫方式、同義詞、官方頁。
- `FAQPage`：直接映射黃金問題與簡明答案，含錨點。
- `Product`：關鍵產品線的規格/用途/認證/相容性。
- `Article`：新聞/部落格，含 `headline`、`datePublished`、`author`、`mainEntityOfPage`。

---

## 後續執行與產出保存

- 本報告已另存於：
  - `E:\CascadeProjects\Aquasky-AIQA-Monitor\outputs\cross_analysis\AEO_cross_analysis_2025-08-13.md`
- 完成本次重要報告更新後，建議執行一次 GitHub 版本更新（commit 與 push），以保留分析成果與可追溯性。
