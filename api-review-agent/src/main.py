import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.agents.api_review_agent import APIReviewAgent

def main():
    config = Config.from_env()
    
    agent = APIReviewAgent(
        openai_api_key=config.openai_api_key,
        confluence_url=config.confluence_url,
        confluence_token=config.confluence_token
    )
    
    task = f"""
请执行完整的 API Review 流程：

1. 读取 Confluence 规范（页面 ID: {config.confluence_page_id}）
2. 生成 Spectral 规则
3. 对比 OpenAPI 变更：
   - 旧文件: {config.main_openapi_path}
   - 新文件: {config.pr_openapi_path}
4. 运行 Spectral 扫描
5. 生成完整的 Review 报告

请按顺序执行，并在最后生成 Markdown 格式的报告。
    """
    
    result = agent.run(task)
    
    print("\n" + "="*60)
    print("API Review 完成")
    print("="*60 + "\n")
    print(result)
    
    if config.github_token and config.github_pr_number > 0:
        try:
            from github import Github
            github_client = Github(config.github_token)
            repo = github_client.get_repo(config.github_repo)
            pr = repo.get_pull(config.github_pr_number)
            pr.create_issue_comment(result)
            print("\n报告已发布到 PR 评论")
        except Exception as e:
            print(f"\n发布到 PR 失败: {e}")

if __name__ == "__main__":
    main()
