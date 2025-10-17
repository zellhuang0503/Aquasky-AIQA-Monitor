# AQUASKY AIQA Monitor

> 多 LLM 問答品質監測與交叉分析工具（目前以 `working_models_processor.py` 為主）

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 專案概述

AQUASKY AIQA Monitor 提供多個大型語言模型（LLMs）的穩定測試流程與輸出彙整。現階段以 `working_models_processor.py` 為主執行路徑，搭配 `config/working_models.json` 管理模型清單，並可透過工具同步文件中的支援清單。

## 快速開始

1) 安裝相依
```bash
pip install -r requirements.txt
```

2) 建立與設定 `config.ini`
```bash
cp config.ini.template config.ini
# 編輯 config.ini，填入 openrouter_api_key 與 PERPLEXITY_API_KEY
```

3) 準備模型清單（可直接使用已提供的 JSON）
- 編輯 `config/working_models.json`，調整你要測試的 8 個模型

4) 執行主程式
```bash
python working_models_processor.py
```

5)（選用）執行標準化交叉分析（使用啟動器）
```bash
python run_standardized_analysis.py
python run_standardized_analysis.py --date 20250829
```

6)（選用）同步 README 的模型清單
```bash
python scripts/sync_models_to_docs.py
```

## 導覽文件
- 批次系統與輸出說明：`README_BATCH.md`
- 交叉分析標準作業：`README_ANALYSIS_STANDARDS.md`

## 目錄結構（精簡）
```
AQUASKY-AIQA-Monitor/
├─ working_models_processor.py          # 目前主要執行路徑
├─ run_standardized_analysis.py         # 啟動器（委派至 archive/...）
├─ config/
│  ├─ working_models.json               # 模型清單（單一來源）
│  └─ ...
├─ scripts/
│  └─ sync_models_to_docs.py            # 將 JSON 清單同步到 README_BATCH.md
├─ outputs/                             # 輸出報告與統計
├─ logs/                                # 進度與執行日誌
├─ src/                                 # 批次/報告相關程式（保留）
├─ archive/                             # 暫存/舊版腳本（實作仍在這裡）
├─ README.md
├─ README_BATCH.md
├─ README_ANALYSIS_STANDARDS.md
├─ config.ini.template
├─ config.ini                            # 本地設定（未納版控）
└─ requirements.txt
```

注意
- `run_standardized_analysis.py` 為根目錄啟動器，實際執行委派到 `archive/run_standardized_analysis.py`，以保留相容的命令與參數。
- 如需更新支援模型清單，請以 `config/working_models.json` 為準，並使用同步工具更新文件。

## 授權
本專案以 MIT 授權條款釋出，詳見 `LICENSE`。

