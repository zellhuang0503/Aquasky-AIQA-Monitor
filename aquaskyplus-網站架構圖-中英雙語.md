# aquaskyplus.com 網站架構圖 / Site Map (Bilingual)

> 根據網站公開 sitemap.xml 整理。以清晰層級呈現主要導覽、頁面與參數。

## 總覽 / Overview

- 首頁 / Home: `/`
  - 語系參數 / Language param: `?lang=en|zh|es|fr|ru|ar-XA`
  - 範例 / Example: `index.php?lang=en`

## 導覽與頁面層級 / Navigation & Hierarchy

- 關於我們 / About Us
  - `about.php`

- 產品與方案 / Products & Solutions
  - `PUMPLUS.php`
  - `MEGA-PLUS.php`
  - `RO-PLUS.php`
  - `THERMAL-PLUS.php`
  - `HYDRO-PLUS.php`
  - `SOLAR-PLUS.php`
  - `PREMIUM-PLUS.php`
  - `supreme.php`
  - 配件 / Accessories: `accessories.php`

- 特色功能 / Features
  - `feature.php`

- 認證與合規 / Certifications & Compliance
  - 認證總覽 / Certifications Overview: `certification.php`
  - CE 文件下載 / CE Downloads: `dl-ce.php`
  - ASME 熱處理 / ASME Heat Treatment: `asme-ht.php`

- 選型工具 / Selection Tools
  - `sel_tools.php`

- 下載中心 / Downloads
  - `downloadpage.php`

- 影音資源 / Media
  - 影片列表 / Videos: `videos.php`
  - 分頁 / Pagination: `videos.php?page=N`（可加 `&lang=...`）

- 新聞與活動 / News & Events
  - 分類一 / Category 1: `news.php?cid=1`
  - 分類二 / Category 2: `news.php?cid=2`
  - 分頁 / Pagination: `news.php?page=N&cid={1|2}`（可加 `&lang=...`）

- 常見問題 / FAQ
  - `FAQ.php`

- 聯絡我們 / Contact Us
  - `contact.php`

## 語系與參數說明 / Languages & Parameters

- 多語系（全站常見）/ Multi-language (site-wide): `?lang=en|zh|es|fr|ru|ar-XA`
- 新聞分頁 / News pagination: `page=N`、分類 `cid=1|2`、可附 `lang`
- 影片分頁 / Videos pagination: `page=N`、可附 `lang`

## 備註 / Notes

- `downloadpage.php` 同時出現含語系與不含語系版本於 sitemap。
- 首頁亦提供語系直達（例如 `index.php?lang=en`）。
