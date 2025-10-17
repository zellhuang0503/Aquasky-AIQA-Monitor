#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
標準化交叉分析執行器
整合所有分析流程，確保每次都達到標準水準
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加 scripts 目錄到路徑
sys.path.append(str(Path(__file__).parent / "scripts"))

from scripts.generate_cross_analysis import CrossAnalysisGenerator
from scripts.quality_validator import ReportQualityValidator

class StandardizedAnalysisRunner:
    """標準化分析執行器"""
    
    def __init__(self):
        self.generator = CrossAnalysisGenerator()
        self.validator = ReportQualityValidator()
        self.project_root = Path.cwd()
    
    def run_complete_analysis(self, date_pattern: str = None) -> dict:
        """執行完整的標準化分析流程"""
        if not date_pattern:
            date_pattern = datetime.now().strftime("%Y%m%d")
        
        print(f"🚀 開始執行標準化交叉分析流程 - {date_pattern}")
        
        results = {
            'date_pattern': date_pattern,
            'report_generated': False,
            'report_path': None,
            'quality_validated': False,
            'quality_score': 0,
            'quality_report_path': None,
            'success': False,
            'errors': []
        }
        
        try:
            # 步驟 1: 生成交叉分析報告
            print("\n📊 步驟 1: 生成交叉分析報告...")
            report_path = self.generator.generate_report(date_pattern)
            results['report_generated'] = True
            results['report_path'] = report_path
            print(f"✅ 報告生成完成: {report_path}")
            
            # 步驟 2: 驗證報告品質
            print("\n🔍 步驟 2: 驗證報告品質...")
            validation_result = self.validator.validate_report(report_path)
            results['quality_validated'] = True
            results['quality_score'] = validation_result['quality_score']
            
            # 生成品質檢查報告
            quality_report = self.validator.generate_quality_report(validation_result)
            report_name = Path(report_path).stem
            quality_report_path = Path("outputs/cross_analysis") / f"{report_name}_quality_check.md"
            
            with open(quality_report_path, 'w', encoding='utf-8') as f:
                f.write(quality_report)
            
            results['quality_report_path'] = str(quality_report_path)
            print(f"📊 品質分數: {validation_result['quality_score']:.1f}/100")
            print(f"📁 品質檢查報告: {quality_report_path}")
            
            # 步驟 3: 檢查是否需要重新生成
            if validation_result['quality_score'] < 70:
                print("\n⚠️ 步驟 3: 品質分數過低，建議檢查並改善...")
                results['errors'].append(f"品質分數過低: {validation_result['quality_score']:.1f}/100")
                
                for error in validation_result['errors']:
                    results['errors'].append(error)
                    print(f"   ❌ {error}")
                
                for warning in validation_result['warnings']:
                    print(f"   ⚠️ {warning}")
            else:
                print(f"\n✅ 步驟 3: 品質驗證通過 ({validation_result['quality_score']:.1f}/100)")
                results['success'] = True
            
            # 步驟 4: 生成執行摘要
            print("\n📋 步驟 4: 生成執行摘要...")
            summary = self._generate_execution_summary(results, validation_result)
            summary_path = Path("outputs/cross_analysis") / f"execution_summary_{date_pattern}.md"
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            results['summary_path'] = str(summary_path)
            print(f"📄 執行摘要: {summary_path}")
            
        except Exception as e:
            error_msg = f"分析流程執行失敗: {str(e)}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
        
        return results
    
    def _generate_execution_summary(self, results: dict, validation_result: dict) -> str:
        """生成執行摘要"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        summary = f"""# 標準化交叉分析執行摘要

**執行時間**: {timestamp}
**分析日期**: {results['date_pattern']}
**執行狀態**: {'✅ 成功' if results['success'] else '❌ 失敗'}

## 執行結果

### 📊 報告生成
- **狀態**: {'✅ 完成' if results['report_generated'] else '❌ 失敗'}
- **報告路徑**: {results.get('report_path', 'N/A')}

### 🔍 品質驗證
- **狀態**: {'✅ 完成' if results['quality_validated'] else '❌ 失敗'}
- **品質分數**: {results['quality_score']:.1f}/100
- **品質等級**: {self._get_quality_grade(results['quality_score'])}
- **驗證報告**: {results.get('quality_report_path', 'N/A')}

## 品質檢查詳情

"""
        
        if 'checks' in validation_result:
            for check_name, check_result in validation_result['checks'].items():
                status = '✅' if check_result['passed'] else '❌'
                summary += f"- **{check_name.replace('_', ' ').title()}**: {status}\n"
        
        if results['errors']:
            summary += "\n## ❌ 發現問題\n"
            for error in results['errors']:
                summary += f"- {error}\n"
        
        summary += f"""
## 📈 改善建議

### 立即改善
- 確保所有必需章節完整
- 補充量化數據和指標
- 完善模型排名分析

### 持續優化
- 定期檢查報告品質
- 更新分析標準
- 改善自動化流程

## 🔄 下次執行

建議下次執行時間: {datetime.now().strftime("%Y-%m-%d")} (一週後)

---
**生成工具**: 標準化交叉分析執行器 v1.0
"""
        
        return summary
    
    def _get_quality_grade(self, score: float) -> str:
        """獲取品質等級"""
        if score >= 90:
            return "🏆 優秀"
        elif score >= 80:
            return "🥈 良好"
        elif score >= 70:
            return "🥉 及格"
        elif score >= 60:
            return "⚠️ 待改善"
        else:
            return "❌ 不及格"

def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='標準化交叉分析執行器')
    parser.add_argument('--date', '-d', help='分析日期 (格式: YYYYMMDD)', default=None)
    parser.add_argument('--force', '-f', action='store_true', help='強制重新生成報告')
    
    args = parser.parse_args()
    
    runner = StandardizedAnalysisRunner()
    results = runner.run_complete_analysis(args.date)
    
    print(f"\n{'='*60}")
    print(f"標準化分析執行完成")
    print(f"{'='*60}")
    print(f"執行狀態: {'✅ 成功' if results['success'] else '❌ 失敗'}")
    print(f"品質分數: {results['quality_score']:.1f}/100")
    
    if results['success']:
        print(f"📊 分析報告: {results['report_path']}")
        print(f"🔍 品質報告: {results['quality_report_path']}")
        print(f"📋 執行摘要: {results['summary_path']}")
    else:
        print("❌ 執行過程中發現問題:")
        for error in results['errors']:
            print(f"   - {error}")
    
    return 0 if results['success'] else 1

if __name__ == "__main__":
    exit(main())
