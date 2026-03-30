import os
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Config:
    confluence_url: str
    confluence_token: str
    github_token: str
    github_repo: str
    openai_api_key: str
    
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from: str
    smtp_to: List[str]
    
    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            confluence_url=os.getenv("CONFLUENCE_URL", ""),
            confluence_token=os.getenv("CONFLUENCE_TOKEN", ""),
            github_token=os.getenv("GITHUB_TOKEN", ""),
            github_repo=os.getenv("GITHUB_REPO", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_username=os.getenv("SMTP_USERNAME", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            smtp_from=os.getenv("SMTP_FROM", ""),
            smtp_to=os.getenv("SMTP_TO", "").split(",") if os.getenv("SMTP_TO") else []
        )
