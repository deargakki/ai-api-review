import requests
from ..config.config import config

class SpectralService:
    def __init__(self):
        """初始化 Spectral 服务"""
        self.service_url = config.SPECTRAL_SERVICE_URL

    def scan_openapi(self, openapi_content, config_content=None):
        """调用 Spectral 服务扫描 OpenAPI"""
        try:
            response = requests.post(
                f"{self.service_url}/scan",
                json={
                    "openapi_content": openapi_content,
                    "config_content": config_content
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Spectral service error: {response.text}")
                return None
        except Exception as e:
            print(f"Error calling Spectral service: {e}")
            return None

    def process_spectral_results(self, results):
        """处理 Spectral 扫描结果"""
        if not results:
            return {"success": False, "issues": []}

        # 格式化结果
        formatted_issues = []
        for issue in results.get("issues", []):
            formatted_issues.append({
                "rule": issue.get("code", ""),
                "severity": issue.get("severity", "info"),
                "message": issue.get("message", ""),
                "path": issue.get("path", []),
                "fix": issue.get("fix", "")
            })

        return {
            "success": True,
            "issues": formatted_issues,
            "summary": results.get("summary", {})
        }
