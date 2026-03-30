# API Review Agent - 技术实现指南

> **目标**: 从零开始开发一个GitHub Action，自动Review OpenAPI.yaml变更

---

## 开发步骤概览

### Phase 1: 项目初始化
1. 创建项目结构
2. 配置Python环境
3. 编写基础配置文件

### Phase 2: 核心功能实现
4. GitHub API集成
5. OpenAPI Diff实现
6. Spectral规则扫描
7. 报告生成

### Phase 3: GitHub Action集成
8. 编写Action配置
9. 测试和调试
10. 部署和发布

---

## Phase 1: 项目初始化

### Step 1.1: 创建项目目录结构

```bash
# 创建项目根目录
mkdir api-review-agent
cd api-review-agent

# 创建目录结构
mkdir -p src/{github,diff,spectral,confluence,report/templates}
mkdir -p tests
```

### Step 1.2: 初始化Python项目

创建 `requirements.txt`:
```txt
PyGithub>=2.1.0
openapi-diff>=0.2.0
jinja2>=3.1.0
pyyaml>=6.0
requests>=2.31.0
atlassian-python-api>=3.40.0
python-dotenv>=1.0.0
```

创建 `setup.py`:
```python
from setuptools import setup, find_packages

setup(
    name="api-review-agent",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyGithub>=2.1.0",
        "openapi-diff>=0.2.0",
        "jinja2>=3.1.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "atlassian-python-api>=3.40.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.9",
)
```

### Step 1.3: 配置文件

创建 `.spectral.yml` (Spectral规则配置):
```yaml
extends: spectral:oas
rules:
  operation-description:
    description: 端点必须有描述
    severity: error
    given: $.paths[*][get,post,put,delete,patch]
    then:
      field: description
      function: truthy
  no-trailing-slash:
    description: 路径不应以斜杠结尾
    severity: warning
    given: $.paths[*]~
    then:
      function: pattern
      functionOptions:
        match: /[^/]$/
```

创建 `.gitignore`:
```txt
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
venv/
ENV/
```

---

## Phase 2: 核心功能实现

### Step 2.1: 配置管理 (config.py)

```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    github_token: str
    github_repo: str
    github_pr_number: int
    openapi_path: str
    base_branch: str = "main"
    confluence_url: Optional[str] = None
    confluence_token: Optional[str] = None
    confluence_page_id: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            github_token=os.getenv("GITHUB_TOKEN"),
            github_repo=os.getenv("GITHUB_REPOSITORY"),
            github_pr_number=int(os.getenv("PR_NUMBER", "0")),
            openapi_path=os.getenv("OPENAPI_PATH", "openapi.yaml"),
            base_branch=os.getenv("BASE_BRANCH", "main"),
            confluence_url=os.getenv("CONFLUENCE_URL"),
            confluence_token=os.getenv("CONFLUENCE_TOKEN"),
            confluence_page_id=os.getenv("CONFLUENCE_PAGE_ID"),
        )
```

### Step 2.2: GitHub API封装 (github/client.py)

```python
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Content import Content
import yaml

class GitHubClient:
    def __init__(self, token: str, repo_name: str):
        self.client = Github(token)
        self.repo: Repository = self.client.get_repo(repo_name)
    
    def get_pr(self, pr_number: int) -> PullRequest:
        return self.repo.get_pull(pr_number)
    
    def get_file_content(self, path: str, ref: str) -> str:
        content_file: Content = self.repo.get_contents(path, ref=ref)
        return content_file.decoded_content.decode('utf-8')
    
    def get_openapi_yaml(self, path: str, ref: str) -> dict:
        content = self.get_file_content(path, ref)
        return yaml.safe_load(content)
    
    def post_pr_comment(self, pr_number: int, body: str):
        pr = self.get_pr(pr_number)
        pr.create_issue_comment(body)
    
    def get_pr_diff_files(self, pr_number: int) -> list:
        pr = self.get_pr(pr_number)
        return [file.filename for file in pr.get_files()]
```

### Step 2.3: Diff引擎 (diff/engine.py)

```python
from typing import Dict, List, Any
import openapi_diff

class DiffEngine:
    def __init__(self):
        pass
    
    def compare(self, old_spec: dict, new_spec: dict) -> Dict[str, Any]:
        result = {
            "added": [],
            "removed": [],
            "modified": [],
            "breaking_changes": []
        }
        
        # 比较paths
        old_paths = set(old_spec.get("paths", {}).keys())
        new_paths = set(new_spec.get("paths", {}).keys())
        
        # 新增的端点
        for path in new_paths - old_paths:
            result["added"].append({
                "type": "endpoint",
                "path": path,
                "methods": list(new_spec["paths"][path].keys())
            })
        
        # 删除的端点
        for path in old_paths - new_paths:
            result["removed"].append({
                "type": "endpoint",
                "path": path
            })
            result["breaking_changes"].append({
                "type": "endpoint_removed",
                "path": path,
                "severity": "critical"
            })
        
        # 修改的端点
        for path in old_paths & new_paths:
            old_path_spec = old_spec["paths"][path]
            new_path_spec = new_spec["paths"][path]
            
            for method in set(old_path_spec.keys()) | set(new_path_spec.keys()):
                if method not in old_path_spec:
                    result["added"].append({
                        "type": "method",
                        "path": path,
                        "method": method.upper()
                    })
                elif method not in new_path_spec:
                    result["removed"].append({
                        "type": "method",
                        "path": path,
                        "method": method.upper()
                    })
                    result["breaking_changes"].append({
                        "type": "method_removed",
                        "path": path,
                        "method": method.upper(),
                        "severity": "critical"
                    })
                else:
                    # 比较schema变化
                    schema_diff = self._compare_schemas(
                        old_path_spec[method],
                        new_path_spec[method],
                        path,
                        method.upper()
                    )
                    result["modified"].extend(schema_diff["modified"])
                    result["breaking_changes"].extend(schema_diff["breaking_changes"])
        
        return result
    
    def _compare_schemas(self, old_schema: dict, new_schema: dict, 
                        path: str, method: str) -> Dict[str, List]:
        result = {"modified": [], "breaking_changes": []}
        
        # 比较响应schema
        old_responses = old_schema.get("responses", {})
        new_responses = new_schema.get("responses", {})
        
        for status_code in set(old_responses.keys()) | set(new_responses.keys()):
            if status_code not in new_responses:
                result["breaking_changes"].append({
                    "type": "response_removed",
                    "path": path,
                    "method": method,
                    "status_code": status_code,
                    "severity": "critical"
                })
        
        return result
```

### Step 2.4: Spectral扫描 (spectral/runner.py)

```python
import subprocess
import json
from typing import Dict, List

class SpectralRunner:
    def __init__(self, config_path: str = ".spectral.yml"):
        self.config_path = config_path
    
    def scan(self, openapi_path: str) -> Dict[str, Any]:
        try:
            # 运行spectral CLI
            result = subprocess.run(
                ["spectral", "lint", openapi_path, "-f", "json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {"success": True, "issues": []}
            
            issues = json.loads(result.stdout)
            return {
                "success": False,
                "issues": self._parse_issues(issues)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "issues": []
            }
    
    def _parse_issues(self, issues: list) -> List[Dict]:
        parsed = []
        for issue in issues:
            parsed.append({
                "code": issue.get("code"),
                "message": issue.get("message"),
                "severity": issue.get("severity"),
                "path": issue.get("path"),
                "source": issue.get("source")
            })
        return parsed
```

### Step 2.5: 报告生成 (report/generator.py)

```python
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

class ReportGenerator:
    def __init__(self, template_dir: str = "src/report/templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    def generate(self, diff_result: Dict, spectral_result: Dict) -> str:
        template = self.env.get_template("review.md.jinja2")
        
        summary = self._generate_summary(diff_result, spectral_result)
        
        return template.render(
            summary=summary,
            diff_result=diff_result,
            spectral_result=spectral_result
        )
    
    def _generate_summary(self, diff_result: Dict, spectral_result: Dict) -> str:
        added_count = len(diff_result.get("added", []))
        removed_count = len(diff_result.get("removed", []))
        modified_count = len(diff_result.get("modified", []))
        breaking_count = len(diff_result.get("breaking_changes", []))
        spectral_issues = len(spectral_result.get("issues", []))
        
        summary = f"""
## 📊 Review Summary

| 指标 | 数量 |
|------|------|
| ✅ 新增 | {added_count} |
| ❌ 删除 | {removed_count} |
| 🔄 修改 | {modified_count} |
| ⚠️ Breaking Changes | {breaking_count} |
| 🔍 Spectral Issues | {spectral_issues} |
"""
        return summary
```

### Step 2.6: 报告模板 (report/templates/review.md.jinja2)

```jinja2
# 🔍 API Review Report

{{ summary }}

{% if diff_result.breaking_changes %}
## 🚨 Breaking Changes

{% for change in diff_result.breaking_changes %}
- **{{ change.type }}**: `{{ change.path }}`
  - 严重程度: {{ change.severity }}
{% endfor %}
{% endif %}

{% if diff_result.added %}
## ➕ 新增内容

{% for item in diff_result.added %}
- **{{ item.type }}**: `{{ item.path }}`
{% endfor %}
{% endif %}

{% if diff_result.removed %}
## ➖ 删除内容

{% for item in diff_result.removed %}
- **{{ item.type }}**: `{{ item.path }}`
{% endfor %}
{% endif %}

{% if diff_result.modified %}
## 🔄 修改内容

{% for item in diff_result.modified %}
- **{{ item.type }}**: `{{ item.path }}`
{% endfor %}
{% endif %}

{% if spectral_result.issues %}
## 🔍 Spectral 扫描结果

{% for issue in spectral_result.issues %}
- **[{{ issue.severity }}]** {{ issue.message }}
  - 位置: `{{ issue.path }}`
  - 规则: `{{ issue.code }}`
{% endfor %}
{% endif %}

---

*此报告由 API Review Agent 自动生成*
```

### Step 2.7: 主入口 (main.py)

```python
import sys
from src.config import Config
from src.github.client import GitHubClient
from src.diff.engine import DiffEngine
from src.spectral.runner import SpectralRunner
from src.report.generator import ReportGenerator

def main():
    config = Config.from_env()
    
    # 初始化组件
    github_client = GitHubClient(config.github_token, config.github_repo)
    diff_engine = DiffEngine()
    spectral_runner = SpectralRunner()
    report_generator = ReportGenerator()
    
    # 获取PR信息
    pr = github_client.get_pr(config.github_pr_number)
    
    # 获取base和head分支的OpenAPI规范
    old_spec = github_client.get_openapi_yaml(config.openapi_path, config.base_branch)
    new_spec = github_client.get_openapi_yaml(config.openapi_path, pr.head.ref)
    
    # 执行Diff
    diff_result = diff_engine.compare(old_spec, new_spec)
    
    # 执行Spectral扫描
    spectral_result = spectral_runner.scan(config.openapi_path)
    
    # 生成报告
    report = report_generator.generate(diff_result, spectral_result)
    
    # 发布PR评论
    github_client.post_pr_comment(config.github_pr_number, report)
    
    print("API Review completed successfully!")

if __name__ == "__main__":
    main()
```

---

## Phase 3: GitHub Action集成

### Step 3.1: GitHub Action配置 (.github/workflows/api-review.yml)

```yaml
name: API Review

on:
  pull_request:
    paths:
      - '**/openapi.yaml'
      - '**/openapi.yml'

jobs:
  api-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm install -g @stoplight/spectral-cli
      
      - name: Run API Review
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          OPENAPI_PATH: "openapi.yaml"
          BASE_BRANCH: ${{ github.base_ref }}
        run: |
          python src/main.py
```

---

## 开发流程建议

### 1. 本地开发环境搭建

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -e .

# 安装Spectral CLI
npm install -g @stoplight/spectral-cli
```

### 2. 测试策略

创建测试文件 `tests/test_diff.py`:
```python
import pytest
from src.diff.engine import DiffEngine

def test_endpoint_added():
    engine = DiffEngine()
    old_spec = {"paths": {}}
    new_spec = {"paths": {"/users": {"get": {}}}}
    
    result = engine.compare(old_spec, new_spec)
    assert len(result["added"]) == 1
    assert result["added"][0]["path"] == "/users"

def test_endpoint_removed():
    engine = DiffEngine()
    old_spec = {"paths": {"/users": {"get": {}}}}
    new_spec = {"paths": {}}
    
    result = engine.compare(old_spec, new_spec)
    assert len(result["removed"]) == 1
    assert len(result["breaking_changes"]) == 1
```

运行测试:
```bash
pytest tests/
```

### 3. 调试技巧

- 使用 `print` 输出中间结果
- 在GitHub Action中添加 `env: ACTIONS_STEP_DEBUG: true` 启用详细日志
- 本地测试时使用环境变量模拟GitHub环境

---

## 下一步行动

1. ✅ 创建项目目录结构
2. ✅ 初始化Python项目
3. ✅ 实现核心功能模块
4. ✅ 编写GitHub Action配置
5. ⏳ 本地测试和调试
6. ⏳ 提交到GitHub仓库
7. ⏳ 创建测试PR验证功能

---

## 常见问题

### Q1: 如何处理多个OpenAPI文件？
A: 可以修改配置，支持指定多个文件路径，循环处理。

### Q2: Spectral规则如何自定义？
A: 编辑 `.spectral.yml` 文件，添加或修改规则。

### Q3: 如何集成Confluence？
A: 使用 `atlassian-python-api` 库，在 `confluence/reader.py` 中实现。

### Q4: 如何处理大型API规范？
A: 考虑增量处理，只分析变更的部分。

---

## 参考资料

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [PyGithub文档](https://pygithub.readthedocs.io/)
- [Spectral文档](https://meta.stoplight.io/docs/spectral/)
- [OpenAPI规范](https://swagger.io/specification/)
