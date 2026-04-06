from github import Github
from ..config.config import config

class GithubService:
    def __init__(self):
        """初始化 GitHub 服务"""
        self.github_token = config.GITHUB_TOKEN
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN 环境变量未设置")
        self.github = Github(self.github_token)

    def get_file_content(self, repo_owner, repo_name, file_path, branch="master"):
        """获取 GitHub 文件内容"""
        try:
            repo = self.github.get_repo(f"{repo_owner}/{repo_name}")
            content = repo.get_contents(file_path, ref=branch)
            return content.decoded_content.decode('utf-8')
        except Exception as e:
            print(f"Error getting GitHub file: {e}")
            return None

    def get_repo(self, repo_owner, repo_name):
        """获取 GitHub 仓库"""
        try:
            return self.github.get_repo(f"{repo_owner}/{repo_name}")
        except Exception as e:
            print(f"Error getting GitHub repo: {e}")
            return None

    def search_openapi_files(self, repo_owner, repo_name, file_name, branch="master"):
        """搜索仓库中的 OpenAPI 文件"""
        try:
            repo = self.github.get_repo(f"{repo_owner}/{repo_name}")
            contents = repo.get_contents("", ref=branch)
            
            # 递归搜索文件
            def search_in_contents(contents):
                for content in contents:
                    if content.type == "file" and content.name == file_name:
                        return content.path
                    elif content.type == "dir":
                        sub_contents = repo.get_contents(content.path, ref=branch)
                        result = search_in_contents(sub_contents)
                        if result:
                            return result
                return None
            
            return search_in_contents(contents)
        except Exception as e:
            print(f"Error searching OpenAPI files: {e}")
            return None
