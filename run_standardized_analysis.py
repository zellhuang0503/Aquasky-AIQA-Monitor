#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
啟動器：委派執行 archive/run_standardized_analysis.py，維持相容的根目錄命令。
"""
import sys
from pathlib import Path
import runpy

here = Path(__file__).resolve().parent
target = here / 'archive' / 'run_standardized_analysis.py'
if not target.exists():
    raise SystemExit(f'找不到 {target}，請確認檔案位置。')

# 將參數保持不變，由目標腳本自行解析
sys.argv = [str(target)] + sys.argv[1:]
runpy.run_path(str(target), run_name='__main__')
