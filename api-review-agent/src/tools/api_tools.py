from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
import json
import yaml
import subprocess

class ConfluenceInput(BaseModel):
    page_id: str = Field(description="Confluence 页面 ID")

class ConfluenceTool(BaseTool):
    name = "read_confluence"
    description = "从 Confluence 读取 API Review 规范文档，输入页面 ID"
    args_schema: Type[BaseModel] = ConfluenceInput
    
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
            return f"成功读取 Confluence 规范:\n\n{content}"
        except Exception as e:
            return f"读取 Confluence 失败: {str(e)}"
    
    async def _arun(self, page_id: str) -> str:
        return self._run(page_id)


class SpectralRulesInput(BaseModel):
    content: str = Field(description="API Review 规范内容")

class SpectralRulesGeneratorTool(BaseTool):
    name = "generate_spectral_rules"
    description = "根据 API Review 规范内容生成 Spectral 规则配置"
    args_schema: Type[BaseModel] = SpectralRulesInput
    
    def __init__(self, openai_api_key: str):
        super().__init__()
        self.openai_api_key = openai_api_key
    
    def _run(self, content: str) -> str:
        import openai
        
        openai.api_key = self.openai_api_key
        
        prompt = f"""
你是一位 API 规范专家。请根据以下 API Review 规范，生成对应的 Spectral 规则配置（YAML 格式）：

{content}

要求：
1. 所有规则必须有清晰的描述
2. 规则级别根据重要性设置为 error、warning 或 info
3. 使用正确的 JSONPath 表达式
4. 覆盖所有提到的规范要求
5. 生成完整的 YAML 配置，包括 extends: spectral:oas

请只输出 YAML 内容，不要包含其他说明。
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            rules = response.choices[0].message.content
            
            with open(".spectral.generated.yml", "w", encoding="utf-8") as f:
                f.write(rules)
            
            return f"成功生成 Spectral 规则并保存到 .spectral.generated.yml\n\n规则预览:\n{rules[:500]}..."
        except Exception as e:
            return f"生成 Spectral 规则失败: {str(e)}"
    
    async def _arun(self, content: str) -> str:
        return self._run(content)


class DiffInput(BaseModel):
    old_yaml_path: str = Field(description="旧 OpenAPI 文件路径")
    new_yaml_path: str = Field(description="新 OpenAPI 文件路径")

class DiffTool(BaseTool):
    name = "compare_openapi"
    description = "对比两个 OpenAPI 文件，识别变更和 Breaking Changes"
    args_schema: Type[BaseModel] = DiffInput
    
    def _run(self, old_yaml_path: str, new_yaml_path: str) -> str:
        try:
            with open(old_yaml_path, encoding="utf-8") as f:
                old_spec = yaml.safe_load(f)
            
            with open(new_yaml_path, encoding="utf-8") as f:
                new_spec = yaml.safe_load(f)
            
            breaking_changes = []
            non_breaking_changes = []
            
            old_paths = set(old_spec.get("paths", {}).keys())
            new_paths = set(new_spec.get("paths", {}).keys())
            
            for path in old_paths - new_paths:
                breaking_changes.append({
                    "code": "endpoint-removed",
                    "message": f"端点 {path} 被删除",
                    "path": path
                })
            
            for path in new_paths - old_paths:
                non_breaking_changes.append({
                    "code": "endpoint-added",
                    "message": f"新增端点 {path}",
                    "path": path
                })
            
            result = {
                "breaking_changes": breaking_changes,
                "non_breaking_changes": non_breaking_changes,
                "summary": {
                    "breaking": len(breaking_changes),
                    "non_breaking": len(non_breaking_changes)
                }
            }
            
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"对比失败: {str(e)}"
    
    async def _arun(self, old_yaml_path: str, new_yaml_path: str) -> str:
        return self._run(old_yaml_path, new_yaml_path)


class SpectralScanInput(BaseModel):
    openapi_path: str = Field(description="OpenAPI 文件路径")
    rules_path: str = Field(description="Spectral 规则文件路径")

class SpectralScanTool(BaseTool):
    name = "run_spectral"
    description = "运行 Spectral 扫描，检查 API 规范合规性"
    args_schema: Type[BaseModel] = SpectralScanInput
    
    def _run(self, openapi_path: str, rules_path: str) -> str:
        try:
            result = subprocess.run(
                ["spectral", "lint", openapi_path, "-r", rules_path, "-f", "json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return json.dumps({
                    "success": True,
                    "issues": [],
                    "message": "所有规则检查通过"
                }, indent=2)
            
            issues = json.loads(result.stdout) if result.stdout else []
            
            error_count = sum(1 for i in issues if i.get("severity") == "error")
            warning_count = sum(1 for i in issues if i.get("severity") == "warning")
            
            return json.dumps({
                "success": False,
                "issues": issues,
                "summary": {
                    "total": len(issues),
                    "errors": error_count,
                    "warnings": warning_count
                }
            }, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Spectral 扫描失败: {str(e)}"
    
    async def _arun(self, openapi_path: str, rules_path: str) -> str:
        return self._run(openapi_path, rules_path)
