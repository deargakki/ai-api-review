from .confluence import ConfluenceService
from .openapi import OpenAPIService
from .github import GithubService
from .spectral import SpectralService
from .report import ReportService

# 导入发送进度更新的函数
try:
    from ..api.main import send_progress_update
except ImportError:
    # 如果无法导入，定义一个空函数
    def send_progress_update(progress, message):
        print(f"Progress: {progress}% - {message}")

class ReviewFlow:
    def __init__(self):
        """初始化审查流程"""
        self.confluence_service = ConfluenceService()
        self.openapi_service = OpenAPIService()
        self.github_service = GithubService()
        self.spectral_service = SpectralService()
        self.report_service = ReportService()

    def run_review(self, confluence_page_id, github_repo, github_file, github_branch="master"):
        """运行完整的审查流程"""
        try:
            # 1. 读取 Confluence 页面内容
            send_progress_update(10, "Reading Confluence page...")
            print("Step 1: Reading Confluence page...")
            confluence_content = self.confluence_service.get_page_content_as_text(confluence_page_id)
            if not confluence_content:
                send_progress_update(0, "Failed to get Confluence content")
                return {"error": "Failed to get Confluence content"}

            # 2. 生成 OpenAPI 规范
            send_progress_update(25, "Generating OpenAPI from Confluence content...")
            print("Step 2: Generating OpenAPI from Confluence content...")
            generated_openapi = self.openapi_service.generate_openapi(confluence_content)
            if not generated_openapi:
                send_progress_update(0, "Failed to generate OpenAPI")
                return {"error": "Failed to generate OpenAPI"}

            # 3. 验证生成的 OpenAPI 规范
            send_progress_update(40, "Validating generated OpenAPI...")
            print("Step 3: Validating generated OpenAPI...")
            is_valid, validation_error = self.openapi_service.validate_openapi(generated_openapi)
            if not is_valid:
                print(f"Warning: Generated OpenAPI is not valid: {validation_error}")

            # 4. 获取 GitHub 上的 OpenAPI 文件
            send_progress_update(50, "Getting OpenAPI from GitHub...")
            print("Step 4: Getting OpenAPI from GitHub...")
            repo_parts = github_repo.split('/')
            if len(repo_parts) != 2:
                send_progress_update(0, "Invalid GitHub repo format")
                return {"error": "Invalid GitHub repo format. Use owner/repo format."}
            repo_owner, repo_name = repo_parts
            
            # 首先尝试按固定路径读取文件
            print(f"Trying to get file from path: {github_file}")
            master_openapi = self.github_service.get_file_content(
                repo_owner, repo_name, github_file, github_branch
            )
            
            # 如果没有找到，搜索 api.yml 文件
            if not master_openapi:
                print(f"File not found at path: {github_file}, searching for api.yml")
                file_path = self.github_service.search_openapi_files(
                    repo_owner, repo_name, "api.yml", github_branch
                )
                if not file_path:
                    # 再搜索 api.yaml 文件
                    file_path = self.github_service.search_openapi_files(
                        repo_owner, repo_name, "api.yaml", github_branch
                    )
                    if not file_path:
                        send_progress_update(0, "No OpenAPI file found in repo")
                        return {"error": "No OpenAPI file found in repo"}
                print(f"Found OpenAPI file at: {file_path}")
                master_openapi = self.github_service.get_file_content(
                    repo_owner, repo_name, file_path, github_branch
                )
                if not master_openapi:
                    send_progress_update(0, "Failed to get GitHub OpenAPI")
                    return {"error": "Failed to get GitHub OpenAPI"}

            # 5. 对比两个 OpenAPI 规范
            send_progress_update(65, "Comparing OpenAPI specifications...")
            print("Step 5: Comparing OpenAPI specifications...")
            comparison_result = self.openapi_service.compare_openapi(
                generated_openapi, master_openapi
            )
            if not comparison_result:
                send_progress_update(0, "Failed to compare OpenAPI")
                return {"error": "Failed to compare OpenAPI"}

            # 6. 运行 Spectral 扫描
            send_progress_update(75, "Running Spectral scan...")
            print("Step 6: Running Spectral scan...")
            spectral_result = self.spectral_service.scan_openapi(generated_openapi)
            if not spectral_result:
                send_progress_update(0, "Failed to run Spectral scan")
                return {"error": "Failed to run Spectral scan"}

            # 7. 处理 Spectral 扫描结果
            send_progress_update(85, "Processing Spectral results...")
            print("Step 7: Processing Spectral results...")
            spectral_processed = self.spectral_service.process_spectral_results(spectral_result)

            # 8. 生成最终报告
            send_progress_update(90, "Generating final report...")
            print("Step 8: Generating final report...")
            report = {
                "success": True,
                "confluence_page_id": confluence_page_id,
                "github_repo": github_repo,
                "github_file": github_file,
                "github_branch": github_branch,
                "generated_openapi": generated_openapi,
                "master_openapi": master_openapi,
                "comparison": comparison_result,
                "spectral": spectral_processed,
                "openapi_valid": is_valid
            }

            # 9. 生成详细报告
            send_progress_update(95, "Generating detailed report...")
            print("Step 9: Generating detailed report...")
            detailed_report = self.report_service.generate_report(report)
            report["detailed_report"] = detailed_report

            send_progress_update(100, "Review completed successfully!")
            return report

        except Exception as e:
            print(f"Error running review flow: {e}")
            return {"error": str(e)}
