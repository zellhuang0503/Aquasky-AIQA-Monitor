#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交叉分析報告品質驗證器
確保每次生成的報告都符合標準
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from analysis_config import QUALITY_CHECKS, QUALITY_STANDARDS, KPI_TARGETS

class ReportQualityValidator:
    """報告品質驗證器"""
    
    def __init__(self):
        self.checks = QUALITY_CHECKS
        self.standards = QUALITY_STANDARDS
        self.targets = KPI_TARGETS
    
    def validate_report(self, report_path: str) -> Dict[str, Any]:
        """驗證報告品質"""
        report_path = Path(report_path)
        
        if not report_path.exists():
            return {
                'valid': False,
                'error': f'報告檔案不存在: {report_path}'
            }
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {
                'valid': False,
                'error': f'無法讀取報告檔案: {e}'
            }
        
        # 執行各項檢查
        results = {
            'valid': True,
            'checks': {},
            'warnings': [],
            'errors': []
        }
        
        # 1. 內容長度檢查
        content_length = len(content)
        results['checks']['content_length'] = {
            'actual': content_length,
            'required': self.checks['min_content_length'],
            'passed': content_length >= self.checks['min_content_length']
        }
        
        if not results['checks']['content_length']['passed']:
            results['errors'].append(f"報告內容過短: {content_length} < {self.checks['min_content_length']}")
        
        # 2. 必需章節檢查
        required_sections = [
            '執行摘要', '模型效能比較', '關鍵問題分析', '模型表現評級',
            '根本問題診斷', '網站內容改善建議', '預期改善效果', '監控與評估'
        ]
        
        found_sections = []
        for section in required_sections:
            if section in content:
                found_sections.append(section)
        
        results['checks']['required_sections'] = {
            'found': len(found_sections),
            'required': len(required_sections),
            'passed': len(found_sections) >= len(required_sections)
        }
        
        if not results['checks']['required_sections']['passed']:
            missing = set(required_sections) - set(found_sections)
            results['errors'].append(f"缺少必需章節: {', '.join(missing)}")
        
        # 3. 數據指標檢查
        metrics_pattern = r'(\d+\.?\d*)%'
        metrics_found = re.findall(metrics_pattern, content)
        
        results['checks']['metrics_count'] = {
            'found': len(metrics_found),
            'required': 10,  # 至少應有10個百分比數據
            'passed': len(metrics_found) >= 10
        }
        
        if not results['checks']['metrics_count']['passed']:
            results['warnings'].append(f"數據指標較少: 找到 {len(metrics_found)} 個，建議至少 10 個")
        
        # 4. 模型排名檢查
        ranking_patterns = [
            r'Token 使用效率排名',
            r'回答品質排名',
            r'最佳綜合表現',
            r'最佳效率表現',
            r'最佳性價比'
        ]
        
        found_rankings = []
        for pattern in ranking_patterns:
            if re.search(pattern, content):
                found_rankings.append(pattern)
        
        results['checks']['rankings'] = {
            'found': len(found_rankings),
            'required': len(ranking_patterns),
            'passed': len(found_rankings) >= 3
        }
        
        if not results['checks']['rankings']['passed']:
            results['warnings'].append(f"排名類型不足: 找到 {len(found_rankings)} 個")
        
        # 5. 改善建議檢查
        suggestion_patterns = [
            r'立即執行',
            r'中期優化',
            r'長期策略',
            r'建立.*頁面',
            r'Schema.*標記',
            r'FAQ.*頁面'
        ]
        
        found_suggestions = []
        for pattern in suggestion_patterns:
            matches = re.findall(pattern, content)
            found_suggestions.extend(matches)
        
        results['checks']['suggestions'] = {
            'found': len(found_suggestions),
            'required': self.checks['min_suggestions'],
            'passed': len(found_suggestions) >= self.checks['min_suggestions']
        }
        
        if not results['checks']['suggestions']['passed']:
            results['warnings'].append(f"改善建議不足: 找到 {len(found_suggestions)} 個")
        
        # 6. KPI目標檢查
        kpi_patterns = [
            r'短期目標',
            r'中期目標',
            r'長期目標',
            r'品牌.*率.*>.*%',
            r'官網.*率.*>.*%'
        ]
        
        found_kpis = []
        for pattern in kpi_patterns:
            if re.search(pattern, content):
                found_kpis.append(pattern)
        
        results['checks']['kpi_targets'] = {
            'found': len(found_kpis),
            'required': 3,
            'passed': len(found_kpis) >= 3
        }
        
        if not results['checks']['kpi_targets']['passed']:
            results['warnings'].append("KPI目標設定不完整")
        
        # 7. 結論檢查
        has_conclusion = '結論' in content and len(content.split('結論')[-1]) > 100
        results['checks']['conclusion'] = {
            'found': has_conclusion,
            'required': True,
            'passed': has_conclusion
        }
        
        if not results['checks']['conclusion']['passed']:
            results['errors'].append("缺少完整結論")
        
        # 總體驗證結果
        all_critical_passed = all(
            check['passed'] for check in results['checks'].values()
            if check.get('required') in [True, results['checks'][list(results['checks'].keys())[0]]['required']]
        )
        
        results['valid'] = len(results['errors']) == 0
        results['quality_score'] = self._calculate_quality_score(results['checks'])
        
        return results
    
    def _calculate_quality_score(self, checks: Dict[str, Any]) -> float:
        """計算品質分數 (0-100)"""
        total_score = 0
        max_score = 0
        
        weights = {
            'content_length': 20,
            'required_sections': 25,
            'metrics_count': 15,
            'rankings': 15,
            'suggestions': 15,
            'kpi_targets': 5,
            'conclusion': 5
        }
        
        for check_name, check_result in checks.items():
            weight = weights.get(check_name, 10)
            max_score += weight
            
            if check_result['passed']:
                total_score += weight
            else:
                # 部分分數基於完成度
                if 'found' in check_result and 'required' in check_result:
                    completion_rate = min(check_result['found'] / check_result['required'], 1.0)
                    total_score += weight * completion_rate
        
        return (total_score / max_score) * 100 if max_score > 0 else 0
    
    def generate_quality_report(self, validation_result: Dict[str, Any]) -> str:
        """生成品質檢查報告"""
        result = validation_result
        
        report = f"""# 交叉分析報告品質檢查結果

## 總體評估
- **驗證狀態**: {'✅ 通過' if result['valid'] else '❌ 未通過'}
- **品質分數**: {result['quality_score']:.1f}/100

## 詳細檢查結果

"""
        
        for check_name, check_result in result['checks'].items():
            status = '✅' if check_result['passed'] else '❌'
            report += f"### {check_name.replace('_', ' ').title()}\n"
            report += f"{status} **狀態**: {'通過' if check_result['passed'] else '未通過'}\n"
            
            if 'found' in check_result and 'required' in check_result:
                report += f"- 發現: {check_result['found']}\n"
                report += f"- 要求: {check_result['required']}\n"
            elif 'actual' in check_result and 'required' in check_result:
                report += f"- 實際: {check_result['actual']}\n"
                report += f"- 要求: {check_result['required']}\n"
            
            report += "\n"
        
        if result['errors']:
            report += "## ❌ 錯誤項目\n"
            for error in result['errors']:
                report += f"- {error}\n"
            report += "\n"
        
        if result['warnings']:
            report += "## ⚠️ 警告項目\n"
            for warning in result['warnings']:
                report += f"- {warning}\n"
            report += "\n"
        
        # 改善建議
        if not result['valid'] or result['quality_score'] < 80:
            report += "## 🔧 改善建議\n"
            
            if result['quality_score'] < 60:
                report += "- 報告品質嚴重不足，建議重新生成\n"
            elif result['quality_score'] < 80:
                report += "- 報告品質有待改善，建議補充缺失內容\n"
            
            for check_name, check_result in result['checks'].items():
                if not check_result['passed']:
                    if check_name == 'content_length':
                        report += "- 增加報告內容深度和詳細分析\n"
                    elif check_name == 'required_sections':
                        report += "- 補充缺失的報告章節\n"
                    elif check_name == 'metrics_count':
                        report += "- 添加更多量化數據和指標\n"
                    elif check_name == 'rankings':
                        report += "- 完善模型排名和比較分析\n"
                    elif check_name == 'suggestions':
                        report += "- 增加具體的改善建議\n"
        
        return report

def main():
    """主程式 - 驗證最新的報告"""
    import sys
    from datetime import datetime
    
    if len(sys.argv) < 2:
        # 尋找最新的報告檔案
        cross_analysis_dir = Path("outputs/cross_analysis")
        if cross_analysis_dir.exists():
            reports = list(cross_analysis_dir.glob("AEO_detailed_cross_analysis_*.md"))
            if reports:
                latest_report = max(reports, key=lambda x: x.stat().st_mtime)
                report_path = str(latest_report)
            else:
                print("❌ 找不到交叉分析報告檔案")
                return
        else:
            print("❌ 找不到 outputs/cross_analysis 目錄")
            return
    else:
        report_path = sys.argv[1]
    
    print(f"🔍 驗證報告: {report_path}")
    
    validator = ReportQualityValidator()
    result = validator.validate_report(report_path)
    
    # 生成品質檢查報告
    quality_report = validator.generate_quality_report(result)
    
    # 保存品質檢查報告
    report_name = Path(report_path).stem
    quality_report_path = Path("outputs/cross_analysis") / f"{report_name}_quality_check.md"
    
    with open(quality_report_path, 'w', encoding='utf-8') as f:
        f.write(quality_report)
    
    print(f"📊 品質分數: {result['quality_score']:.1f}/100")
    print(f"📁 品質檢查報告: {quality_report_path}")
    
    if result['valid']:
        print("✅ 報告品質驗證通過")
    else:
        print("❌ 報告品質驗證未通過")
        for error in result['errors']:
            print(f"   - {error}")

if __name__ == "__main__":
    main()
