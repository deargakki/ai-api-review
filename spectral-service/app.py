from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json
import tempfile
import os

app = FastAPI(title="Spectral API Service")

# 默认的 Spectral 配置
DEFAULT_SPECTRAL_CONFIG = """
extends: spectral:oas
rules:
  operation-description: error
  path-params: error
  no-undefined-refs: error
  operation-2xx-response: error
  tag-description: warning
  no-empty-servers: warning
  no-server-trailing-slash: warning
  info-contact: warning
  info-description: warning
  license-url: warning
  no-eval-in-markdown: warning
  no-script-tags-in-markdown: warning
  operation-operationId-unique: error
  operation-parameters-unique: error
  parameter-description: warning
  path-declarations-must-exist: error
  path-not-include-query: error
  request-body-description: warning
  response-description: warning
"""


class ScanRequest(BaseModel):
    openapi_content: str
    config_content: str = None

class ScanResponse(BaseModel):
    success: bool
    issues: list
    summary: dict

@app.post("/scan", response_model=ScanResponse)
async def scan_openapi(request: ScanRequest):
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(request.openapi_content)
            openapi_file = f.name

        config_file = None
        # 使用用户提供的配置或默认配置
        config_content = request.config_content or DEFAULT_SPECTRAL_CONFIG
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_file = f.name

        # 模拟 Spectral 扫描结果
        # 实际项目中这里会调用真实的 Spectral CLI
        issues = [
            {
                "code": "operation-description",
                "message": "Operation 'get' on path '/test' has no description",
                "severity": "warning",
                "path": ["paths", "/test", "get"],
                "range": {
                    "start": {"line": 8, "character": 5},
                    "end": {"line": 12, "character": 11}
                },
                "source": "spectral:oas"
            },
            {
                "code": "info-description",
                "message": "Info object should have a description",
                "severity": "warning",
                "path": ["info"],
                "range": {
                    "start": {"line": 2, "character": 1},
                    "end": {"line": 4, "character": 1}
                },
                "source": "spectral:oas"
            }
        ]
        print(f"Spectral CLI output: {issues}")

        # 清理临时文件
        os.unlink(openapi_file)
        if config_file:
            os.unlink(config_file)

        return ScanResponse(
            success=True,
            issues=issues,
            summary={
                "total": len(issues),
                "errors": len([i for i in issues if i['severity'] == 'error']),
                "warnings": len([i for i in issues if i['severity'] == 'warning']),
                "infos": len([i for i in issues if i['severity'] == 'info'])
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
