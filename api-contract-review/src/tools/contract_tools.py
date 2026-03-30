from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List, Dict
import yaml
import json

class ConfluenceAPIPageInput(BaseModel):
    page_id: str = Field(description="Confluence API 页面 ID")

class ConfluenceAPIPageTool(BaseTool):
    name = "read_confluence_api_page"
    description = "从 Confluence 读取 API 页面，包含 API contract、Header、Request Body、Response Sample、Path 入参等完整信息"
    args_schema: Type[BaseModel] = ConfluenceAPIPageInput
    
    def __init__(self, confluence_url: str, confluence_token: str):
        super().__init__()
        self.confluence_url = confluence_url
        self.confluence_token = confluence_token
    
    def _run(self, page_id: str) -> str:
        from atlassian import Confluence
        
        confluence = Confluence(
            url=self.confluence_url,
            token=self.confluence_token
        )
        
        try:
            page = confluence.get_page_by_id(page_id, expand="body.storage")
            content = page["body"]["storage"]["value"]
            
            return json.dumps({
                "success": True,
                "page_id": page_id,
                "title": page.get('title', 'N/A'),
                "content": content,
                "content_length": len(content)
            }, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2, ensure_ascii=False)
    
    async def _arun(self, page_id: str) -> str:
        return self._run(page_id)


class ConfluenceStandardInput(BaseModel):
    page_id: str = Field(description="Confluence Governance Standard 页面 ID")

class ConfluenceStandardTool(BaseTool):
    name = "read_confluence_standard"
    description = "从 Confluence 读取 Governance Standard 页面，包含 API 的标准和规则"
    args_schema: Type[BaseModel] = ConfluenceStandardInput
    
    def __init__(self, confluence_url: str, confluence_token: str):
        super().__init__()
        self.confluence_url = confluence_url
        self.confluence_token = confluence_token
    
    def _run(self, page_id: str) -> str:
        from atlassian import Confluence
        
        confluence = Confluence(
            url=self.confluence_url,
            token=self.confluence_token
        )
        
        try:
            page = confluence.get_page_by_id(page_id, expand="body.storage")
            content = page["body"]["storage"]["value"]
            
            return json.dumps({
                "success": True,
                "page_id": page_id,
                "title": page.get('title', 'N/A'),
                "content": content,
                "content_length": len(content)
            }, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2, ensure_ascii=False)
    
    async def _arun(self, page_id: str) -> str:
        return self._run(page_id)


class GenerateOpenAPIInput(BaseModel):
    confluence_content: str = Field(description="Confluence API 页面的完整内容")

class GenerateOpenAPITool(BaseTool):
    name = "generate_openapi_from_confluence"
    description = "根据 Confluence API 页面内容生成 OpenAPI 规范文件（YAML 格式）"
    args_schema: Type[BaseModel] = GenerateOpenAPIInput
    
    def __init__(self, openai_api_key: str):
        super().__init__()
        self.openai_api_key = openai_api_key
    
    def _run(self, confluence_content: str) -> str:
        import openai
        
        client = openai.OpenAI(api_key=self.openai_api_key)
        
        prompt = f"""
你是一位 API 规范专家。请根据以下 Confluence API 页面内容，生成完整的 OpenAPI 3.0 规范（YAML 格式）。

Confluence API 页面内容：
{confluence_content}

要求：
1. 生成完整的 OpenAPI 3.0 规范
2. 包含所有 API 端点（从 Confluence 中提取）
3. 包含每个端点的：
   - HTTP 方法（GET、POST、PUT、DELETE 等）
   - 路径参数
   - 查询参数
   - 请求头
   - 请求体
   - 响应体
   - 响应示例
4. 使用正确的 OpenAPI 3.0 语法
5. 包含必要的 components/schemas 定义
6. 只输出 YAML 内容，不要包含其他说明

输出格式：
```yaml
openapi: 3.0.0
info:
  title: API 名称
  version: 1.0.0
  description: API 描述

paths:
  /endpoint:
    get:
      summary: 端点描述
      parameters: [...]
      responses:
        '200':
          description: 成功响应
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/...'
              examples:
                example: {...}

components:
  schemas:
    SchemaName:
      type: object
      properties: {...}
```
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            openapi_yaml = response.choices[0].message.content
            
            with open("openapi-generated.yml", "w", encoding="utf-8") as f:
                f.write(openapi_yaml)
            
            return json.dumps({
                "success": True,
                "file_path": "openapi-generated.yml",
                "content_length": len(openapi_yaml),
                "preview": openapi_yaml[:500]
            }, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2, ensure_ascii=False)
    
    async def _arun(self, confluence_content: str) -> str:
        return self._run(confluence_content)


class GitHubOpenAPIInput(BaseModel):
    repo: str = Field(description="GitHub 仓库名称，如 owner/repo")
    branch: str = Field(description="分支名称，默认 master")
    path: str = Field(description="OpenAPI 文件路径")

class GitHubOpenAPITool(BaseTool):
    name = "get_github_openapi"
    description = "从 GitHub 仓库获取指定分支的 OpenAPI 文件内容"
    args_schema: Type[BaseModel] = GitHubOpenAPIInput
    
    def __init__(self, github_token: str):
        super().__init__()
        self.github_token = github_token
    
    def _run(self, repo: str, branch: str = "master", path: str = "openapi.yml") -> str:
        from github import Github
        
        try:
            github_client = Github(self.github_token)
            repo_obj = github_client.get_repo(repo)
            
            branch_obj = repo_obj.get_branch(branch)
            tree = repo_obj.get_git_tree(branch_obj.commit.sha)
            
            for item in tree.tree:
                if item.path == path:
                    blob = repo_obj.get_git_blob(item.sha)
                    content = blob.content.decode("utf-8")
                    
                    with open("master-openapi.yml", "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    return json.dumps({
                        "success": True,
                        "file_path": "master-openapi.yml",
                        "content_length": len(content),
                        "preview": content[:500]
                    }, indent=2, ensure_ascii=False)
            
            return json.dumps({
                "success": False,
                "error": f"在 {repo} 仓库的 {branch} 分支中找不到文件: {path}"
            }, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2, ensure_ascii=False)
    
    async def _arun(self, repo: str, branch: str = "master", path: str = "openapi.yml") -> str:
        return self._run(repo, branch, path)


class CompareOpenAPIInput(BaseModel):
    generated_path: str = Field(description="Confluence 生成的 OpenAPI 文件路径")
    master_path: str = Field(description="GitHub master 分支的 OpenAPI 文件路径")

class CompareOpenAPITool(BaseTool):
    name = "compare_openapi"
    description = "对比两个 OpenAPI 文件，生成详细的差异报告"
    args_schema: Type[BaseModel] = CompareOpenAPIInput
    
    def _run(self, generated_path: str, master_path: str) -> str:
        try:
            with open(generated_path, encoding="utf-8") as f:
                generated_spec = yaml.safe_load(f)
            
            with open(master_path, encoding="utf-8") as f:
                master_spec = yaml.safe_load(f)
            
            diff_result = self._compare_specs(generated_spec, master_spec)
            
            return json.dumps(diff_result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2, ensure_ascii=False)
    
    def _compare_specs(self, generated: dict, master: dict) -> dict:
        result = {
            "success": True,
            "generated_only": [],
            "master_only": [],
            "differences": [],
            "summary": {}
        }
        
        gen_paths = set(generated.get("paths", {}).keys())
        mast_paths = set(master.get("paths", {}).keys())
        
        result["generated_only"] = list(gen_paths - mast_paths)
        result["master_only"] = list(mast_paths - gen_paths)
        
        for path in gen_paths & mast_paths:
            gen_methods = set(generated["paths"][path].keys())
            mast_methods = set(master["paths"][path].keys())
            
            for method in gen_methods - mast_methods:
                result["differences"].append({
                    "type": "method_added",
                    "path": path,
                    "method": method.upper(),
                    "source": "generated"
                })
            
            for method in mast_methods - gen_methods:
                result["differences"].append({
                    "type": "method_removed",
                    "path": path,
                    "method": method.upper(),
                    "source": "master"
                })
            
            for method in gen_methods & mast_methods:
                gen_endpoint = generated["paths"][path][method]
                mast_endpoint = master["paths"][path][method]
                
                self._compare_endpoint(path, method, gen_endpoint, mast_endpoint, result)
        
        result["summary"] = {
            "generated_only_count": len(result["generated_only"]),
            "master_only_count": len(result["master_only"]),
            "differences_count": len(result["differences"])
        }
        
        return result
    
    def _compare_endpoint(self, path: str, method: str, gen: dict, mast: dict, result: dict):
        gen_params = gen.get("parameters", [])
        mast_params = mast.get("parameters", [])
        
        gen_param_names = {p.get("name") for p in gen_params}
        mast_param_names = {p.get("name") for p in mast_params}
        
        for param in gen_params:
            if param.get("name") not in mast_param_names:
                result["differences"].append({
                    "type": "parameter_added",
                    "path": path,
                    "method": method.upper(),
                    "parameter": param.get("name"),
                    "source": "generated"
                })
        
        for param in mast_params:
            if param.get("name") not in gen_param_names:
                result["differences"].append({
                    "type": "parameter_removed",
                    "path": path,
                    "method": method.upper(),
                    "parameter": param.get("name"),
                    "source": "master"
                })
        
        gen_responses = gen.get("responses", {})
        mast_responses = mast.get("responses", {})
        
        for status in set(gen_responses.keys()) - set(mast_responses.keys()):
            result["differences"].append({
                "type": "response_added",
                "path": path,
                "method": method.upper(),
                "status": status,
                "source": "generated"
            })
        
        for status in set(mast_responses.keys()) - set(gen_responses.keys()):
            result["differences"].append({
                "type": "response_removed",
                "path": path,
                "method": method.upper(),
                "status": status,
                "source": "master"
            })
    
    async def _arun(self, generated_path: str, master_path: str) -> str:
        return self._run(generated_path, master_path)


class IdentifyBreakingChangesInput(BaseModel):
    diff_result: str = Field(description="OpenAPI 对比结果 JSON 字符串")

class IdentifyBreakingChangesTool(BaseTool):
    name = "identify_breaking_changes"
    description = "根据 OpenAPI 对比结果识别 Breaking Changes"
    args_schema: Type[BaseModel] = IdentifyBreakingChangesInput
    
    def _run(self, diff_result: str) -> str:
        try:
            diff = json.loads(diff_result)
            
            breaking_changes = []
            
            for diff_item in diff.get("differences", []):
                change_type = diff_item.get("type")
                
                if change_type in ["method_removed", "parameter_removed", "response_removed"]:
                    breaking_changes.append({
                        "type": change_type,
                        "severity": "critical",
                        "description": self._get_breaking_change_description(diff_item)
                    })
            
            for path in diff.get("master_only", []):
                breaking_changes.append({
                    "type": "endpoint_removed",
                    "severity": "critical",
                    "description": f"端点 {path} 被删除"
                })
            
            return json.dumps({
                "success": True,
                "breaking_changes": breaking_changes,
                "count": len(breaking_changes)
            }, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2, ensure_ascii=False)
    
    def _get_breaking_change_description(self, diff_item: dict) -> str:
        change_type = diff_item.get("type")
        path = diff_item.get("path")
        method = diff_item.get("method")
        
        if change_type == "method_removed":
            return f"端点 {method} {path} 被删除"
        elif change_type == "parameter_removed":
            param = diff_item.get("parameter")
            return f"端点 {method} {path} 的参数 {param} 被删除"
        elif change_type == "response_removed":
            status = diff_item.get("status")
            return f"端点 {method} {path} 的响应 {status} 被删除"
        
        return f"未知 Breaking Change: {change_type}"
    
    async def _arun(self, diff_result: str) -> str:
        return self._run(diff_result)


class CheckGovernanceStandardsInput(BaseModel):
    openapi_path: str = Field(description="OpenAPI 文件路径")
    standard_content: str = Field(description="Governance Standard 内容")

class CheckGovernanceStandardsTool(BaseTool):
    name = "check_governance_standards"
    description = "根据 Governance Standard 检查 OpenAPI 规范的合规性"
    args_schema: Type[BaseModel] = CheckGovernanceStandardsInput
    
    def __init__(self, openai_api_key: str):
        super().__init__()
        self.openai_api_key = openai_api_key
    
    def _run(self, openapi_path: str, standard_content: str) -> str:
        import openai
        
        client = openai.OpenAI(api_key=self.openai_api_key)
        
        try:
            with open(openapi_path, encoding="utf-8") as f:
                openapi_content = f.read()
            
            prompt = f"""
你是一位 API 规范专家。请根据以下 Governance Standard 检查 OpenAPI 规范的合规性。

Governance Standard:
{standard_content}

OpenAPI 规范:
{openapi_content}

要求：
1. 仔细分析 Governance Standard 中的所有规则
2. 检查 OpenAPI 规范是否符合每个规则
3. 对于每个违规，提供：
   - 规则名称
   - 严重程度（error/warning/info）
   - 违规描述
   - 具体位置
   - 修复建议
4. 以 JSON 格式输出

输出格式：
```json
{
  "success": true,
  "violations": [
    {
      "rule": "规则名称",
      "severity": "error",
      "description": "违规描述",
      "location": "具体位置",
      "suggestion": "修复建议"
    }
  ],
  "summary": {
    "total": 0,
    "errors": 0,
    "warnings": 0,
    "info": 0
  }
}
```
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.choices[0].message.content
            
            try:
                result = json.loads(result_text)
            except:
                result = {
                    "success": False,
                    "error": "LLM 返回的不是有效的 JSON",
                    "raw_response": result_text
                }
            
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2, ensure_ascii=False)
    
    async def _arun(self, openapi_path: str, standard_content: str) -> str:
        return self._run(openapi_path, standard_content)


class GenerateDiffReportInput(BaseModel):
    diff_result: str = Field(description="OpenAPI 对比结果 JSON 字符串")
    breaking_changes: str = Field(description="Breaking Changes JSON 字符串")
    standard_violations: str = Field(description="Standard 违规 JSON 字符串")

class GenerateDiffReportTool(BaseTool):
    name = "generate_diff_report"
    description = "根据对比结果、Breaking Changes 和 Standard 违规生成详细的 Markdown 格式差异报告"
    args_schema: Type[BaseModel] = GenerateDiffReportInput
    
    def __init__(self, openai_api_key: str):
        super().__init__()
        self.openai_api_key = openai_api_key
    
    def _run(self, diff_result: str, breaking_changes: str, standard_violations: str) -> str:
        import openai
        
        client = openai.OpenAI(api_key=self.openai_api_key)
        
        prompt = f"""
你是一位 API 文档专家。请根据以下信息生成详细的 Markdown 格式差异报告。

对比结果：
{diff_result}

Breaking Changes:
{breaking_changes}

Standard 违规：
{standard_violations}

报告要求：
1. 使用清晰的 Markdown 格式
2. 包含以下部分：
   - 执行摘要
   - Confluence 独有的端点
   - GitHub master 独有的端点
   - Breaking Changes（重点）
   - Governance Standards 违规
   - 详细差异列表
   - 建议和行动计划
3. 对每个差异提供：
   - 差异类型（新增、删除、修改）
   - 具体位置（端点路径、方法）
   - 影响分析
4. Breaking Changes 需要特别标注，使用红色
5. 使用表情符号增强可读性
6. 提供具体的修复建议

报告模板：
```markdown
# 📊 API Contract Review 报告

## 执行摘要
- Confluence 独有: X 个端点
- GitHub master 独有: Y 个端点
- 差异总数: Z 个
- Breaking Changes: N 个
- Standard 违规: M 个

## Breaking Changes ⚠️
[列出所有 Breaking Changes]

## Governance Standards 违规 🔍
[列出所有 Standard 违规]

## Confluence 独有的端点
[列出 Confluence 有但 GitHub master 没有的端点]

## GitHub master 独有的端点
[列出 GitHub master 有但 Confluence 没有的端点]

## 详细差异
### 新增的端点/方法
[列出 Confluence 新增的内容]

### 删除的端点/方法
[列出 Confluence 删除的内容]

### 修改的端点
[列出 Confluence 修改的内容]

## 建议和行动计划
1. [具体建议]
2. [具体建议]
3. [具体建议]
```

请只输出 Markdown 格式的报告，不要包含其他说明。
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            report = response.choices[0].message.content
            
            with open("diff-report.md", "w", encoding="utf-8") as f:
                f.write(report)
            
            return json.dumps({
                "success": True,
                "file_path": "diff-report.md",
                "content": report
            }, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2, ensure_ascii=False)
    
    async def _arun(self, diff_result: str, breaking_changes: str, standard_violations: str) -> str:
        return self._run(diff_result, breaking_changes, standard_violations)
