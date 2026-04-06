from typing import Dict, Any
import json

class ReportService:
    """报告生成服务"""
    
    def generate_report(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成审查报告"""
        try:
            # 提取审查结果
            generated_openapi = review_result.get('generated_openapi', '')
            comparison_result = review_result.get('comparison_result', {})
            spectral_result = review_result.get('spectral_result', {})
            summary = review_result.get('summary', {})
            
            # 构建报告
            report = {
                "title": "API Contract Review Report",
                "generated_openapi": generated_openapi,
                "comparison": {
                    "api_status": comparison_result.get('api_status', 'unknown'),
                    "breaking_changes": self._format_breaking_changes(comparison_result.get('breaking_changes', [])),
                    "non_breaking_changes": self._format_non_breaking_changes(comparison_result.get('non_breaking_changes', [])),
                    "summary": comparison_result.get('summary', {})
                },
                "spectral": {
                    "issues": self._format_spectral_issues(spectral_result.get('issues', [])),
                    "summary": spectral_result.get('summary', {})
                },
                "summary": summary,
                "recommendations": self._generate_recommendations(comparison_result, spectral_result)
            }
            
            return report
        except Exception as e:
            print(f"Error generating report: {e}")
            return {
                "error": f"Failed to generate report: {str(e)}"
            }
    
    def _format_breaking_changes(self, breaking_changes: list) -> list:
        """格式化 Breaking Changes"""
        formatted_changes = []
        for change in breaking_changes:
            formatted_changes.append({
                "type": change.get('type', 'unknown'),
                "severity": change.get('severity', 'low'),
                "description": change.get('description', ''),
                "path": change.get('path', ''),
                "method": change.get('method', '')
            })
        return formatted_changes
    
    def _format_non_breaking_changes(self, non_breaking_changes: list) -> list:
        """格式化 Non-Breaking Changes"""
        formatted_changes = []
        for change in non_breaking_changes:
            formatted_changes.append({
                "type": change.get('type', 'unknown'),
                "description": change.get('description', ''),
                "path": change.get('path', ''),
                "method": change.get('method', '')
            })
        return formatted_changes
    
    def _format_spectral_issues(self, issues: list) -> list:
        """格式化 Spectral 扫描结果"""
        formatted_issues = []
        for issue in issues:
            formatted_issues.append({
                "code": issue.get('code', ''),
                "message": issue.get('message', ''),
                "severity": issue.get('severity', 'info'),
                "path": issue.get('path', []),
                "range": issue.get('range', {})
            })
        return formatted_issues
    
    def _generate_recommendations(self, comparison_result: Dict[str, Any], spectral_result: Dict[str, Any]) -> list:
        """生成建议"""
        recommendations = []
        
        # 基于 Breaking Changes 的建议
        breaking_changes = comparison_result.get('breaking_changes', [])
        if breaking_changes:
            recommendations.append({
                "type": "breaking_changes",
                "message": f"发现 {len(breaking_changes)} 个 Breaking Changes，请谨慎处理",
                "severity": "high"
            })
        
        # 基于 Spectral 扫描的建议
        spectral_issues = spectral_result.get('issues', [])
        if spectral_issues:
            error_count = len([i for i in spectral_issues if i.get('severity') == 'error'])
            warning_count = len([i for i in spectral_issues if i.get('severity') == 'warning'])
            if error_count > 0:
                recommendations.append({
                    "type": "spectral_errors",
                    "message": f"发现 {error_count} 个错误，请修复",
                    "severity": "high"
                })
            if warning_count > 0:
                recommendations.append({
                    "type": "spectral_warnings",
                    "message": f"发现 {warning_count} 个警告，建议修复",
                    "severity": "medium"
                })
        
        # 一般建议
        recommendations.append({
            "type": "general",
            "message": "请确保 API 变更符合组织的 API 设计规范",
            "severity": "low"
        })
        
        return recommendations