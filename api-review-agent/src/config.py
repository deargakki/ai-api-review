import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    github_token: str
    github_repo: str
    github_pr_number: int
    
    main_openapi_path: str
    pr_openapi_path: str
    
    confluence_url: str
    confluence_token: str
    confluence_page_id: str
    
    openai_api_key: str
    
    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            github_token=os.getenv("GITHUB_TOKEN", ""),
            github_repo=os.getenv("GITHUB_REPOSITORY", ""),
            github_pr_number=int(os.getenv("PR_NUMBER", "0")),
            main_openapi_path=os.getenv("MAIN_OPENAPI_PATH", "main-openapi.yaml"),
            pr_openapi_path=os.getenv("PR_OPENAPI_PATH", "pr-openapi.yaml"),
            confluence_url=os.getenv("CONFLUENCE_URL", ""),
            confluence_token=os.getenv("CONFLUENCE_TOKEN", ""),
            confluence_page_id=os.getenv("CONFLUENCE_PAGE_ID", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        )
