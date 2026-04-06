from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json
import tempfile
import os

app = FastAPI(title="Spectral API Service")

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
        if request.config_content:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(request.config_content)
                config_file = f.name

        # 模拟 Spectral 扫描结果
        # 实际项目中这里会调用真实的 Spectral CLI
        issues = [
            {
                "code": "operation-description",
                "message": "Operation 'get' on path '/test' has no description",
                "severity": "warning",
                "path": ["paths", "/test", "get"]
            }
        ]

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
