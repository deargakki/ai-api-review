# Spectral 集成方案

## 1. Spectral 简介

### 1.1 什么是 Spectral

Spectral 是一个强大的 API 规范检查工具（linter），用于验证 OpenAPI/Swagger、AsyncAPI、JSON Schema 等规范的合规性。

**主要功能**：
- 验证 API 规范的合规性
- 检查命名规范（kebab-case、camelCase 等）
- 验证文档完整性（description、summary 等）
- 检查安全配置（security schemes）
- 自定义规则支持
- 支持多种规范格式

**扫描内容**：
- 路径命名规范
- 操作描述完整性
- 参数定义规范
- 响应格式验证
- 安全配置检查
- 版本控制规范
- 媒体类型定义

### 1.2 为什么需要 Spectral

在 API Contract Review 流程中集成 Spectral 可以：
1. **确保规范一致性**：强制执行统一的命名和格式规范
2. **提高文档质量**：确保 API 文档的完整性和可读性
3. **早期发现问题**：在 API 部署前发现规范问题
4. **自动化检查**：替代人工审查，提高效率
5. **可定制规则**：根据团队需求自定义检查规则

## 2. 安装和配置

### 2.1 安装 Spectral

Spectral 可以通过多种方式安装：

#### 方式 1：通过 npm 安装（推荐）

```bash
# 全局安装
npm install -g @stoplight/spectral-cli

# 或者在项目中安装
npm install --save-dev @stoplight/spectral-cli
```

#### 方式 2：通过 Homebrew 安装（macOS）

```bash
brew install spectral
```

#### 方式 3：使用 Docker

```bash
docker pull stoplight/spectral:latest
```

### 2.2 验证安装

```bash
spectral --version
```

### 2.3 创建 Spectral 配置文件

在项目根目录创建 `.spectral.yaml` 配置文件：

```yaml
# .spectral.yaml

extends:
  - spectral:oas
  - spectral:oas/functions

rules:
  # 路径命名规范
  path-kebab-case:
    description: API paths must use kebab-case
    given: $.paths
    then:
      field: @key
      function: pattern
      functionOptions:
        match: "^\/[a-z0-9-\/{}]+$"
    severity: error

  # 版本号要求
  version-in-path:
    description: API paths must include version number
    given: $.paths
    then:
      field: @key
      function: pattern
      functionOptions:
        match: "^\/v[0-9]+"
    severity: error

  # 安全配置要求
  security-required:
    description: Operations must have security defined
    given: "$.paths[*][*][?(@property === 'get' || @property === 'post' || @property === 'put' || @property === 'delete')]"
    then:
      field: security
      function: truthy
    severity: error

  # 描述要求
  description-required:
    description: Operations must have a description
    given: "$.paths[*][*][?(@property === 'get' || @property === 'post' || @property === 'put' || @property === 'delete')]"
    then:
      field: description
      function: truthy
    severity: warning

  # 摘要要求
  summary-required:
    description: Operations must have a summary
    given: "$.paths[*][*][?(@property === 'get' || @property === 'post' || @property === 'put' || @property === 'delete')]"
    then:
      field: summary
      function: truthy
    severity: warning

  # 参数描述要求
  parameter-description:
    description: Parameters must have a description
    given: "$.paths[*][*].parameters[*]"
    then:
      field: description
      function: truthy
    severity: warning

  # 响应描述要求
  response-description:
    description: Responses must have a description
    given: "$.paths[*][*].responses[*]"
    then:
      field: description
      function: truthy
    severity: warning

  # 必需的响应状态码
  required-response-codes:
    description: Operations should define common response codes
    given: "$.paths[*][*][?(@property === 'get' || @property === 'post' || @property === 'put' || @property === 'delete')]"
    then:
      field: responses
      function: schema
      functionOptions:
        schema:
          type: object
          required:
            - 200
            - 400
            - 500
    severity: warning

  # 标签要求
  tags-required:
    description: Operations should have tags for grouping
    given: "$.paths[*][*][?(@property === 'get' || @property === 'post' || @property === 'put' || @property === 'delete')]"
    then:
      field: tags
      function: truthy
    severity: info
```

## 3. 集成方案

### 3.0 方式 0：部署为服务（推荐用于生产环境）

将 Spectral 部署为 HTTP 服务，通过 API 调用进行扫描。这种方式适合生产环境，具有以下优势：

**优势**：
- 集中管理 Spectral 版本和配置
- 无需在每个客户端安装 Spectral
- 便于监控和日志收集
- 支持并发请求
- 易于扩展和维护

#### 3.0.1 使用 FastAPI 部署 Spectral 服务

创建 `spectral_service.py`：

```python
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import subprocess
import json
import os
import tempfile
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Spectral API Service", version="1.0.0")

class ScanRequest(BaseModel):
    openapi_content: str
    config_content: Optional[str] = None
    output_format: str = "json"

class ScanResponse(BaseModel):
    success: bool
    issues: list = []
    summary: dict = {}
    error: Optional[str] = None
    message: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Spectral API Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/scan", response_model=ScanResponse)
async def scan_openapi(request: ScanRequest):
    """
    扫描 OpenAPI 规范
    
    Args:
        request: 扫描请求，包含 OpenAPI 内容和配置
    
    Returns:
        扫描结果
    """
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
        
        try:
            # 构建命令
            cmd = ['spectral', 'lint', openapi_file, '--format', request.output_format]
            
            if config_file:
                cmd.extend(['--ruleset', config_file])
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # 处理结果
            if result.returncode == 0:
                return ScanResponse(
                    success=True,
                    issues=[],
                    summary={'total': 0, 'errors': 0, 'warnings': 0, 'info': 0}
                )
            elif result.returncode == 1:
                if request.output_format == 'json':
                    issues = json.loads(result.stdout)
                    return _parse_issues(issues)
                else:
                    return ScanResponse(
                        success=True,
                        issues=[],
                        raw_output=result.stdout,
                        summary={'total': 0, 'errors': 0, 'warnings': 0, 'info': 0}
                    )
            else:
                return ScanResponse(
                    success=False,
                    error=result.stderr,
                    message="Spectral 执行失败"
                )
                
        finally:
            # 清理临时文件
            os.unlink(openapi_file)
            if config_file and os.path.exists(config_file):
                os.unlink(config_file)
                
    except subprocess.TimeoutExpired:
        logger.error("Spectral 执行超时")
        return ScanResponse(
            success=False,
            error="扫描超时",
            message="Spectral 执行超时"
        )
    except json.JSONDecodeError as e:
        logger.error(f"Spectral 输出解析失败: {str(e)}")
        return ScanResponse(
            success=False,
            error=str(e),
            message="Spectral 输出解析失败"
        )
    except Exception as e:
        logger.error(f"Spectral 扫描异常: {str(e)}", exc_info=True)
        return ScanResponse(
            success=False,
            error=str(e),
            message="Spectral 扫描异常"
        )

@app.post("/scan/file", response_model=ScanResponse)
async def scan_openapi_file(file: UploadFile = File(...), config: UploadFile = File(None)):
    """
    通过文件上传扫描 OpenAPI 规范
    
    Args:
        file: OpenAPI 文件
        config: 可选的 Spectral 配置文件
    
    Returns:
        扫描结果
    """
    try:
        # 读取上传的文件
        openapi_content = await file.read()
        openapi_content = openapi_content.decode('utf-8')
        
        config_content = None
        if config:
            config_content = await config.read()
            config_content = config_content.decode('utf-8')
        
        # 调用扫描函数
        request = ScanRequest(
            openapi_content=openapi_content,
            config_content=config_content
        )
        
        return await scan_openapi(request)
        
    except Exception as e:
        logger.error(f"文件扫描异常: {str(e)}", exc_info=True)
        return ScanResponse(
            success=False,
            error=str(e),
            message="文件扫描异常"
        )

def _parse_issues(spectral_output):
    """解析 Spectral 输出"""
    issues = []
    
    for item in spectral_output:
        severity = _map_severity(item.get('severity', 0))
        
        issue = {
            'code': item.get('code', 'unknown'),
            'message': item.get('message', ''),
            'severity': severity,
            'path': item.get('path', []),
            'range': item.get('range', {}),
            'source': item.get('source', '')
        }
        
        issues.append(issue)
    
    # 统计问题
    summary = {
        'total': len(issues),
        'errors': len([i for i in issues if i['severity'] == 'error']),
        'warnings': len([i for i in issues if i['severity'] == 'warning']),
        'info': len([i for i in issues if i['severity'] == 'info'])
    }
    
    return ScanResponse(
        success=True,
        issues=issues,
        summary=summary
    )

def _map_severity(spectral_severity):
    """映射 Spectral 严重级别"""
    severity_map = {
        0: 'error',
        1: 'warning',
        2: 'info',
        3: 'info'
    }
    return severity_map.get(spectral_severity, 'info')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 3.0.2 部署服务

**使用 Docker 部署**：

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

# 安装 Spectral
RUN npm install -g @stoplight/spectral-cli

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY spectral_service.py .

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "spectral_service:app", "--host", "0.0.0.0", "--port", "8000"]
```

创建 `requirements.txt`：

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
```

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  spectral-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./config:/app/config:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**启动服务**：

```bash
# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 3.0.3 调用服务

**使用 Python 客户端**：

```python
import requests
import json

class SpectralServiceClient:
    """
    Spectral 服务客户端
    """
    
    def __init__(self, service_url="http://localhost:8000"):
        """
        初始化客户端
        
        Args:
            service_url: Spectral 服务 URL
        """
        self.service_url = service_url
        self.session = requests.Session()
    
    def scan_openapi(self, openapi_content, config_content=None, output_format='json'):
        """
        扫描 OpenAPI 规范
        
        Args:
            openapi_content: OpenAPI 规范内容
            config_content: 可选的 Spectral 配置内容
            output_format: 输出格式
        
        Returns:
            扫描结果
        """
        url = f"{self.service_url}/scan"
        
        payload = {
            "openapi_content": openapi_content,
            "output_format": output_format
        }
        
        if config_content:
            payload["config_content"] = config_content
        
        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=120
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Spectral 服务调用失败'
            }
    
    def scan_openapi_file(self, openapi_file_path, config_file_path=None):
        """
        通过文件扫描 OpenAPI 规范
        
        Args:
            openapi_file_path: OpenAPI 文件路径
            config_file_path: 可选的配置文件路径
        
        Returns:
            扫描结果
        """
        url = f"{self.service_url}/scan/file"
        
        files = {
            'file': open(openapi_file_path, 'rb')
        }
        
        if config_file_path:
            files['config'] = open(config_file_path, 'rb')
        
        try:
            response = self.session.post(
                url,
                files=files,
                timeout=120
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Spectral 服务调用失败'
            }
        finally:
            for f in files.values():
                f.close()
    
    def health_check(self):
        """
        健康检查
        
        Returns:
            服务状态
        """
        url = f"{self.service_url}/health"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

# 使用示例
def main():
    # 初始化客户端
    client = SpectralServiceClient(service_url="http://localhost:8000")
    
    # 健康检查
    health = client.health_check()
    print(f"服务状态: {health}")
    
    # 读取 OpenAPI 文件
    with open('openapi-generated.yml', 'r') as f:
        openapi_content = f.read()
    
    # 读取配置文件（可选）
    try:
        with open('.spectral.yaml', 'r') as f:
            config_content = f.read()
    except FileNotFoundError:
        config_content = None
    
    # 执行扫描
    result = client.scan_openapi(
        openapi_content=openapi_content,
        config_content=config_content
    )
    
    # 处理结果
    if result['success']:
        print(f"扫描完成，发现 {result['summary']['total']} 个问题")
        print(f"错误: {result['summary']['errors']}, 警告: {result['summary']['warnings']}")
    else:
        print(f"扫描失败: {result.get('message', '未知错误')}")

if __name__ == "__main__":
    main()
```

#### 3.0.4 服务配置管理

创建配置文件 `config.py`：

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """配置类"""
    
    # Spectral 服务配置
    SPECTRAL_SERVICE_URL = os.getenv('SPECTRAL_SERVICE_URL', 'http://localhost:8000')
    SPECTRAL_SERVICE_TIMEOUT = int(os.getenv('SPECTRAL_SERVICE_TIMEOUT', '120'))
    
    # 默认配置文件路径
    DEFAULT_SPECTRAL_CONFIG_PATH = os.getenv('DEFAULT_SPECTRAL_CONFIG_PATH', '.spectral.yaml')
```

#### 3.0.5 在主流程中调用

```python
from spectral_service_client import SpectralServiceClient
from config import Config

def run_spectral_scan(openapi_content):
    """
    运行 Spectral 扫描（通过服务）
    
    Args:
        openapi_content: OpenAPI 规范内容
    
    Returns:
        扫描结果
    """
    # 初始化客户端
    client = SpectralServiceClient(
        service_url=Config.SPECTRAL_SERVICE_URL
    )
    
    # 读取配置文件（可选）
    config_content = None
    if os.path.exists(Config.DEFAULT_SPECTRAL_CONFIG_PATH):
        with open(Config.DEFAULT_SPECTRAL_CONFIG_PATH, 'r') as f:
            config_content = f.read()
    
    # 执行扫描
    result = client.scan_openapi(
        openapi_content=openapi_content,
        config_content=config_content
    )
    
    return result

# 在主流程中使用
def main():
    # ... 其他步骤 ...
    
    # 读取生成的 OpenAPI
    with open('openapi-generated.yml', 'r') as f:
        openapi_content = f.read()
    
    # 运行 Spectral 扫描
    scan_result = run_spectral_scan(openapi_content)
    
    # 处理结果
    if scan_result['success']:
        print(f"Spectral 扫描完成，发现 {scan_result['summary']['total']} 个问题")
        print(f"错误: {scan_result['summary']['errors']}, 警告: {scan_result['summary']['warnings']}")
    else:
        print(f"Spectral 扫描失败: {scan_result.get('message', '未知错误')}")
```

#### 3.0.6 服务监控和日志

**添加监控端点**：

```python
from prometheus_client import Counter, Histogram, generate_latest

# Prometheus 指标
scan_requests_total = Counter('spectral_scan_requests_total', 'Total scan requests')
scan_requests_success = Counter('spectral_scan_requests_success', 'Successful scan requests')
scan_requests_failed = Counter('spectral_scan_requests_failed', 'Failed scan requests')
scan_duration = Histogram('spectral_scan_duration_seconds', 'Scan duration')

@app.get("/metrics")
async def metrics():
    """Prometheus 指标"""
    return Response(content=generate_latest(), media_type="text/plain")

# 在 scan_openapi 函数中使用
@app.post("/scan", response_model=ScanResponse)
async def scan_openapi(request: ScanRequest):
    scan_requests_total.inc()
    
    with scan_duration.time():
        # ... 扫描逻辑 ...
        
        if result['success']:
            scan_requests_success.inc()
        else:
            scan_requests_failed.inc()
        
        return result
```

### 3.1 方式 1：命令行调用（推荐）

```python
import subprocess
import json
import os

class SpectralScanner:
    """
    Spectral 扫描器
    """
    
    def __init__(self, spectral_path='spectral', config_path='.spectral.yaml'):
        """
        初始化扫描器
        
        Args:
            spectral_path: Spectral 可执行文件路径
            config_path: Spectral 配置文件路径
        """
        self.spectral_path = spectral_path
        self.config_path = config_path
    
    def scan_openapi(self, openapi_file, output_format='json'):
        """
        扫描 OpenAPI 文件
        
        Args:
            openapi_file: OpenAPI 文件路径
            output_format: 输出格式（json, pretty, stylish, junit）
        
        Returns:
            扫描结果
        """
        # 构建命令
        cmd = [
            self.spectral_path,
            'lint',
            openapi_file,
            '--format', output_format
        ]
        
        # 添加配置文件
        if os.path.exists(self.config_path):
            cmd.extend(['--ruleset', self.config_path])
        
        try:
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Spectral 返回码：0 = 无问题，1 = 有问题
            if result.returncode == 0:
                return {
                    'success': True,
                    'issues': [],
                    'summary': {
                        'total': 0,
                        'errors': 0,
                        'warnings': 0,
                        'info': 0
                    }
                }
            elif result.returncode == 1:
                # 解析输出
                if output_format == 'json':
                    issues = json.loads(result.stdout)
                    return self._parse_issues(issues)
                else:
                    return {
                        'success': True,
                        'issues': [],
                        'raw_output': result.stdout,
                        'summary': {
                            'total': 0,
                            'errors': 0,
                            'warnings': 0,
                            'info': 0
                        }
                    }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'message': 'Spectral 执行失败'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '扫描超时',
                'message': 'Spectral 执行超时'
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Spectral 输出解析失败',
                'raw_output': result.stdout
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Spectral 执行异常'
            }
    
    def _parse_issues(self, spectral_output):
        """
        解析 Spectral 输出
        
        Args:
            spectral_output: Spectral 原始输出
        
        Returns:
            标准化的问题列表
        """
        issues = []
        
        for item in spectral_output:
            severity = self._map_severity(item.get('severity', 0))
            
            issue = {
                'code': item.get('code', 'unknown'),
                'message': item.get('message', ''),
                'severity': severity,
                'path': item.get('path', []),
                'range': item.get('range', {}),
                'source': item.get('source', '')
            }
            
            issues.append(issue)
        
        # 统计问题
        summary = {
            'total': len(issues),
            'errors': len([i for i in issues if i['severity'] == 'error']),
            'warnings': len([i for i in issues if i['severity'] == 'warning']),
            'info': len([i for i in issues if i['severity'] == 'info'])
        }
        
        return {
            'success': True,
            'issues': issues,
            'summary': summary
        }
    
    def _map_severity(self, spectral_severity):
        """
        映射 Spectral 严重级别
        
        Args:
            spectral_severity: Spectral 严重级别（0=error, 1=warning, 2=info, 3=hint）
        
        Returns:
            标准化的严重级别
        """
        severity_map = {
            0: 'error',
            1: 'warning',
            2: 'info',
            3: 'info'
        }
        return severity_map.get(spectral_severity, 'info')
```

### 3.2 方式 2：使用 Python 库

```python
from spectral import Spectral

class SpectralLibraryScanner:
    """
    使用 Spectral Python 库的扫描器
    """
    
    def __init__(self, config_path='.spectral.yaml'):
        """
        初始化扫描器
        
        Args:
            config_path: Spectral 配置文件路径
        """
        self.config_path = config_path
        self.spectral = Spectral()
        
        # 加载配置
        if os.path.exists(config_path):
            self.spectral.load_ruleset(config_path)
    
    def scan_openapi(self, openapi_content):
        """
        扫描 OpenAPI 内容
        
        Args:
            openapi_content: OpenAPI 规范内容（字符串）
        
        Returns:
            扫描结果
        """
        try:
            # 解析 OpenAPI 内容
            spec = yaml.safe_load(openapi_content)
            
            # 运行扫描
            results = self.spectral.run(spec)
            
            # 解析结果
            issues = []
            for result in results:
                issue = {
                    'code': result.code,
                    'message': result.message,
                    'severity': self._map_severity(result.severity),
                    'path': result.path,
                    'range': result.range
                }
                issues.append(issue)
            
            # 统计问题
            summary = {
                'total': len(issues),
                'errors': len([i for i in issues if i['severity'] == 'error']),
                'warnings': len([i for i in issues if i['severity'] == 'warning']),
                'info': len([i for i in issues if i['severity'] == 'info'])
            }
            
            return {
                'success': True,
                'issues': issues,
                'summary': summary
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Spectral 扫描失败',
                'issues': [],
                'summary': {
                    'total': 0,
                    'errors': 0,
                    'warnings': 0,
                    'info': 0
                }
            }
    
    def _map_severity(self, spectral_severity):
        """
        映射 Spectral 严重级别
        """
        severity_map = {
            'error': 'error',
            'warn': 'warning',
            'info': 'info',
            'hint': 'info'
        }
        return severity_map.get(spectral_severity, 'info')
```

### 3.3 方式 3：使用 Docker

```python
import subprocess
import json

class SpectralDockerScanner:
    """
    使用 Docker 运行 Spectral 的扫描器
    """
    
    def __init__(self, image='stoplight/spectral:latest', config_path='.spectral.yaml'):
        """
        初始化扫描器
        
        Args:
            image: Spectral Docker 镜像
            config_path: Spectral 配置文件路径
        """
        self.image = image
        self.config_path = config_path
    
    def scan_openapi(self, openapi_file, output_format='json'):
        """
        扫描 OpenAPI 文件
        
        Args:
            openapi_file: OpenAPI 文件路径
            output_format: 输出格式
        
        Returns:
            扫描结果
        """
        # 构建命令
        cmd = [
            'docker', 'run', '--rm',
            '-v', f"{os.path.dirname(os.path.abspath(openapi_file))}:/work",
            '-w', '/work',
            self.image,
            'lint',
            os.path.basename(openapi_file),
            '--format', output_format
        ]
        
        # 添加配置文件
        if os.path.exists(self.config_path):
            cmd.extend(['--ruleset', f'/work/{self.config_path}'])
        
        try:
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # 处理结果
            if result.returncode == 0:
                return {
                    'success': True,
                    'issues': [],
                    'summary': {
                        'total': 0,
                        'errors': 0,
                        'warnings': 0,
                        'info': 0
                    }
                }
            elif result.returncode == 1:
                if output_format == 'json':
                    issues = json.loads(result.stdout)
                    return self._parse_issues(issues)
                else:
                    return {
                        'success': True,
                        'issues': [],
                        'raw_output': result.stdout
                    }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'message': 'Spectral Docker 执行失败'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '扫描超时',
                'message': 'Spectral Docker 执行超时'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Spectral Docker 执行异常'
            }
    
    def _parse_issues(self, spectral_output):
        """解析 Spectral 输出"""
        issues = []
        
        for item in spectral_output:
            severity = self._map_severity(item.get('severity', 0))
            
            issue = {
                'code': item.get('code', 'unknown'),
                'message': item.get('message', ''),
                'severity': severity,
                'path': item.get('path', []),
                'range': item.get('range', {})
            }
            
            issues.append(issue)
        
        summary = {
            'total': len(issues),
            'errors': len([i for i in issues if i['severity'] == 'error']),
            'warnings': len([i for i in issues if i['severity'] == 'warning']),
            'info': len([i for i in issues if i['severity'] == 'info'])
        }
        
        return {
            'success': True,
            'issues': issues,
            'summary': summary
        }
    
    def _map_severity(self, spectral_severity):
        """映射 Spectral 严重级别"""
        severity_map = {
            0: 'error',
            1: 'warning',
            2: 'info',
            3: 'info'
        }
        return severity_map.get(spectral_severity, 'info')
```

## 4. 集成到系统

### 4.1 配置管理

创建配置文件 `config.py`：

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """配置类"""
    
    # Spectral 配置
    SPECTRAL_PATH = os.getenv('SPECTRAL_PATH', 'spectral')
    SPECTRAL_CONFIG_PATH = os.getenv('SPECTRAL_CONFIG_PATH', '.spectral.yaml')
    SPECTRAL_TIMEOUT = int(os.getenv('SPECTRAL_TIMEOUT', '60'))
    
    # 扫描配置
    SPECTRAL_OUTPUT_FORMAT = os.getenv('SPECTRAL_OUTPUT_FORMAT', 'json')
    
    # 使用方式：cli, library, docker
    SPECTRAL_MODE = os.getenv('SPECTRAL_MODE', 'cli')
    
    # Docker 配置（如果使用 Docker）
    SPECTRAL_DOCKER_IMAGE = os.getenv('SPECTRAL_DOCKER_IMAGE', 'stoplight/spectral:latest')
```

### 4.2 在主流程中调用

```python
from spectral_scanner import SpectralScanner
from config import Config

def run_spectral_scan(openapi_file):
    """
    运行 Spectral 扫描
    
    Args:
        openapi_file: OpenAPI 文件路径
    
    Returns:
        扫描结果
    """
    # 根据配置选择扫描器
    if Config.SPECTRAL_MODE == 'cli':
        scanner = SpectralScanner(
            spectral_path=Config.SPECTRAL_PATH,
            config_path=Config.SPECTRAL_CONFIG_PATH
        )
    elif Config.SPECTRAL_MODE == 'docker':
        scanner = SpectralDockerScanner(
            image=Config.SPECTRAL_DOCKER_IMAGE,
            config_path=Config.SPECTRAL_CONFIG_PATH
        )
    else:
        scanner = SpectralLibraryScanner(
            config_path=Config.SPECTRAL_CONFIG_PATH
        )
    
    # 执行扫描
    result = scanner.scan_openapi(
        openapi_file=openapi_file,
        output_format=Config.SPECTRAL_OUTPUT_FORMAT
    )
    
    return result

# 在主流程中使用
def main():
    # ... 其他步骤 ...
    
    # 运行 Spectral 扫描
    scan_result = run_spectral_scan('openapi-generated.yml')
    
    # 处理结果
    if scan_result['success']:
        print(f"Spectral 扫描完成，发现 {scan_result['summary']['total']} 个问题")
        print(f"错误: {scan_result['summary']['errors']}, 警告: {scan_result['summary']['warnings']}")
    else:
        print(f"Spectral 扫描失败: {scan_result.get('message', '未知错误')}")
```

## 5. 输出格式处理

### 5.1 标准化输出

```python
def normalize_spectral_result(raw_result):
    """
    标准化 Spectral 扫描结果
    
    Args:
        raw_result: 原始扫描结果
    
    Returns:
        标准化后的结果
    """
    if not raw_result.get('success', True):
        return {
            'success': False,
            'error': raw_result.get('error', '未知错误'),
            'message': raw_result.get('message', '扫描失败'),
            'issues': [],
            'summary': {
                'total': 0,
                'errors': 0,
                'warnings': 0,
                'info': 0
            }
        }
    
    # 提取问题列表
    issues = raw_result.get('issues', [])
    
    # 统计问题
    summary = {
        'total': len(issues),
        'errors': len([i for i in issues if i.get('severity') == 'error']),
        'warnings': len([i for i in issues if i.get('severity') == 'warning']),
        'info': len([i for i in issues if i.get('severity') == 'info'])
    }
    
    return {
        'success': True,
        'issues': issues,
        'summary': summary
    }
```

### 5.2 输出格式示例

```json
{
  "success": true,
  "issues": [
    {
      "code": "path-kebab-case",
      "message": "Path should use kebab-case",
      "severity": "error",
      "path": ["paths", "/userProfiles"],
      "range": {
        "start": {
          "line": 10,
          "character": 1
        },
        "end": {
          "line": 10,
          "character": 15
        }
      }
    },
    {
      "code": "version-in-path",
      "message": "URL must contain version number",
      "severity": "error",
      "path": ["paths", "/users"],
      "range": {
        "start": {
          "line": 15,
          "character": 1
        },
        "end": {
          "line": 15,
          "character": 8
        }
      }
    },
    {
      "code": "security-required",
      "message": "Operation must have \"security\"",
      "severity": "error",
      "path": ["paths", "/users", "get"],
      "range": {
        "start": {
          "line": 16,
          "character": 3
        },
        "end": {
          "line": 16,
          "character": 6
        }
      }
    },
    {
      "code": "description-required",
      "message": "Operation must have \"description\"",
      "severity": "warning",
      "path": ["paths", "/users", "get"],
      "range": {
        "start": {
          "line": 16,
          "character": 3
        },
        "end": {
          "line": 16,
          "character": 6
        }
      }
    }
  ],
  "summary": {
    "total": 4,
    "errors": 3,
    "warnings": 1,
    "info": 0
  }
}
```

## 6. 自定义规则

### 6.1 创建自定义规则

在 `.spectral.yaml` 中添加自定义规则：

```yaml
rules:
  # 自定义规则：操作 ID 命名规范
  operation-id-naming:
    description: Operation IDs must follow the pattern: {resource}_{action}
    given: "$.paths[*][*][?(@property === 'get' || @property === 'post' || @property === 'put' || @property === 'delete')]"
    then:
      field: operationId
      function: pattern
      functionOptions:
        match: "^[a-z]+_[a-z]+$"
    severity: error

  # 自定义规则：响应必须有 schema
  response-schema-required:
    description: Response must have a schema defined
    given: "$.paths[*][*].responses[*].content[*]"
    then:
      field: schema
      function: truthy
    severity: error

  # 自定义规则：参数必须有示例
  parameter-example-required:
    description: Parameters should have an example
    given: "$.paths[*][*].parameters[*]"
    then:
      field: example
      function: truthy
    severity: warning

  # 自定义规则：禁止使用 any 类型
  no-any-type:
    description: Schema should not use 'any' type
    given: "$.components.schemas[*][?(@.type === 'any')]"
    then:
      function: truthy
      functionOptions:
        inverse: true
    severity: error

  # 自定义规则：必须提供服务器 URL
  server-url-required:
    description: API must define server URL
    given: "$.servers"
    then:
      field: 0
      function: truthy
    severity: error
```

### 6.2 使用 JavaScript 自定义规则

创建 `custom-rules.js` 文件：

```javascript
module.exports = {
  rules: {
    'custom-rule-name': {
      description: '自定义规则描述',
      message: '错误消息',
      severity: 'error',
      given: '$.paths[*][*]',
      then: {
        function: function(path, _, context) {
          // 自定义逻辑
          return true; // 返回 true 表示通过，false 表示失败
        }
      }
    }
  }
};
```

在 `.spectral.yaml` 中引用：

```yaml
extends:
  - ./custom-rules.js
```

## 7. 错误处理

### 7.1 常见错误及处理

```python
class SpectralError(Exception):
    """Spectral 错误基类"""
    pass

class ConfigurationError(SpectralError):
    """配置错误"""
    pass

class FileNotFoundError(SpectralError):
    """文件未找到错误"""
    pass

class ParseError(SpectralError):
    """解析错误"""
    pass

def handle_spectral_error(error):
    """
    处理 Spectral 错误
    
    Args:
        error: 错误对象
    
    Returns:
        错误信息
    """
    if isinstance(error, ConfigurationError):
        return {
            'success': False,
            'error_type': 'configuration',
            'message': 'Spectral 配置错误，请检查 .spectral.yaml 文件'
        }
    elif isinstance(error, FileNotFoundError):
        return {
            'success': False,
            'error_type': 'file_not_found',
            'message': 'OpenAPI 文件未找到'
        }
    elif isinstance(error, ParseError):
        return {
            'success': False,
            'error_type': 'parse',
            'message': 'OpenAPI 文件解析失败，请检查文件格式'
        }
    else:
        return {
            'success': False,
            'error_type': 'unknown',
            'message': f'未知错误: {str(error)}'
        }
```

### 7.2 重试机制

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=2):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        continue
                    else:
                        raise
            
            raise last_error
        return wrapper
    return decorator

# 使用示例
@retry_on_failure(max_retries=3, delay=2)
def scan_with_retry(openapi_file):
    """带重试的扫描"""
    scanner = SpectralScanner()
    return scanner.scan_openapi(openapi_file)
```

## 8. 最佳实践

### 8.1 性能优化

1. **缓存结果**：对相同的 OpenAPI 文件缓存扫描结果
2. **并行扫描**：如果扫描多个文件，使用并行处理
3. **增量扫描**：只扫描变更的部分
4. **规则优化**：只启用必要的规则

### 8.2 规则管理

1. **分层规则**：
   - 基础规则：所有项目必须遵守
   - 项目规则：特定项目的规则
   - 自定义规则：团队自定义的规则

2. **规则版本控制**：
   - 将 `.spectral.yaml` 纳入版本控制
   - 记录规则变更历史
   - 定期审查和更新规则

3. **规则文档**：
   - 为每个自定义规则添加文档
   - 说明规则的用途和影响
   - 提供修复建议

### 8.3 监控和日志

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scan_with_logging(openapi_file):
    """
    带日志记录的扫描
    """
    logger.info(f"开始 Spectral 扫描: {openapi_file}")
    
    try:
        result = run_spectral_scan(openapi_file)
        
        if result['success']:
            logger.info(f"Spectral 扫描完成，发现 {result['summary']['total']} 个问题")
            logger.info(f"错误: {result['summary']['errors']}, 警告: {result['summary']['warnings']}, 信息: {result['summary']['info']}")
            
            # 记录每个问题
            for issue in result['issues']:
                logger.debug(f"问题: {issue['code']} - {issue['message']} at {issue['path']}")
        else:
            logger.error(f"Spectral 扫描失败: {result.get('message')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Spectral 扫描异常: {str(e)}", exc_info=True)
        raise
```

## 9. 集成到报告

将 Spectral 结果集成到最终的报告中：

```python
def generate_final_report(comparison_result, cage_scan_result, spectral_result):
    """
    生成最终报告
    
    Args:
        comparison_result: OpenAPI 对比结果
        cage_scan_result: Cage Scan 结果
        spectral_result: Spectral 扫描结果
    
    Returns:
        最终报告
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'comparison': comparison_result,
        'security_scan': {
            'cage_scan': cage_scan_result,
            'spectral': spectral_result
        },
        'overall_status': 'pass'
    }
    
    # 判断整体状态
    if comparison_result.get('breaking_changes'):
        report['overall_status'] = 'fail'
    elif cage_scan_result.get('summary', {}).get('errors', 0) > 0:
        report['overall_status'] = 'fail'
    elif spectral_result.get('summary', {}).get('errors', 0) > 0:
        report['overall_status'] = 'fail'
    
    return report
```

## 10. 总结

**关键点**：
1. Spectral 是强大的 API 规范检查工具，可以确保 API 文档质量
2. 提供多种集成方式：命令行、Python 库、Docker
3. 支持自定义规则，满足团队特定需求
4. 标准化输出格式，便于集成到报告
5. 实现完善的错误处理和重试机制
6. 建立规则管理和版本控制流程
7. 添加日志记录，便于调试和监控

**与 Cage Scan 的区别**：
- **Spectral**：关注 API 规范的合规性（命名、格式、文档完整性）
- **Cage Scan**：关注 API 的安全性（认证、授权、输入验证、数据泄露）

**下一步**：
1. 安装 Spectral 并验证安装
2. 创建和配置 `.spectral.yaml` 文件
3. 根据团队需求自定义规则
4. 测试集成方案
5. 部署到生产环境
6. 建立规则审查和更新流程
