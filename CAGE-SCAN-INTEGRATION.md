# Cage Scan 集成方案

## 1. Cage Scan 简介

### 1.1 什么是 Cage Scan

Cage Scan 是一个 API 安全扫描工具，用于检测 API 中的安全漏洞和风险。

**主要功能**：
- 检测 API 安全漏洞
- 检查认证和授权问题
- 验证输入安全性
- 识别潜在的安全风险
- 提供详细的安全报告

**扫描内容**：
- 认证机制
- 授权控制
- 输入验证
- 数据泄露风险
- API 配置安全
- 敏感数据处理

### 1.2 为什么需要 Cage Scan

在 API Contract Review 流程中集成 Cage Scan 可以：
1. **自动化安全检查**：在 API 变更时自动进行安全扫描
2. **早期发现问题**：在 API 部署前发现安全漏洞
3. **合规性检查**：确保 API 符合安全标准
4. **降低风险**：减少安全漏洞带来的潜在损失

## 2. 集成方案

### 2.1 方案概述

由于公司已经提供了 Cage Scan 的访问 link，我们可以通过以下方式集成：

```
系统 → 调用 Cage Scan API → 获取扫描结果 → 集成到报告
```

### 2.2 实现方式

#### 方式 1：HTTP API 调用（推荐）

如果公司提供的 link 支持 HTTP API 调用：

```python
import requests
import json

class CageScanClient:
    """
    Cage Scan 客户端
    """
    
    def __init__(self, api_url, api_key=None):
        """
        初始化客户端
        
        Args:
            api_url: Cage Scan API 的 URL
            api_key: API 密钥（如果需要）
        """
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json'
        }
        
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def scan_openapi(self, openapi_content, scan_config=None):
        """
        扫描 OpenAPI 规范
        
        Args:
            openapi_content: OpenAPI 规范内容（YAML 或 JSON 字符串）
            scan_config: 可选的扫描配置
        
        Returns:
            扫描结果
        """
        endpoint = f"{self.api_url}/scan"
        
        payload = {
            'openapi': openapi_content,
            'config': scan_config or {}
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=300  # 5 分钟超时
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Cage Scan 调用失败'
            }
    
    def get_scan_status(self, scan_id):
        """
        获取扫描状态（如果支持异步扫描）
        
        Args:
            scan_id: 扫描任务 ID
        
        Returns:
            扫描状态
        """
        endpoint = f"{self.api_url}/scan/{scan_id}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': '获取扫描状态失败'
            }
```

#### 方式 2：命令行工具调用

如果公司提供的是命令行工具或可执行文件：

```python
import subprocess
import json
import tempfile
import os

class CageScanCLI:
    """
    Cage Scan 命令行工具封装
    """
    
    def __init__(self, cli_path):
        """
        初始化 CLI 客户端
        
        Args:
            cli_path: Cage Scan CLI 工具的路径
        """
        self.cli_path = cli_path
    
    def scan_openapi(self, openapi_content, output_format='json'):
        """
        扫描 OpenAPI 规范
        
        Args:
            openapi_content: OpenAPI 规范内容
            output_format: 输出格式（json, yaml, xml）
        
        Returns:
            扫描结果
        """
        # 创建临时文件保存 OpenAPI 内容
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False
        ) as f:
            f.write(openapi_content)
            input_file = f.name
        
        try:
            # 构建命令
            cmd = [
                self.cli_path,
                'scan',
                '--input', input_file,
                '--output', output_format
            ]
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr,
                    'message': 'Cage Scan 执行失败'
                }
            
            # 解析输出
            if output_format == 'json':
                return json.loads(result.stdout)
            else:
                return {
                    'success': True,
                    'raw_output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '扫描超时',
                'message': 'Cage Scan 执行超时'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Cage Scan 执行异常'
            }
        finally:
            # 清理临时文件
            if os.path.exists(input_file):
                os.unlink(input_file)
```

#### 方式 3：Web 界面自动化（不推荐）

如果只能通过 Web 界面使用：

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class CageScanWeb:
    """
    Cage Scan Web 界面自动化（不推荐，仅作为备选方案）
    """
    
    def __init__(self, web_url, username=None, password=None):
        """
        初始化 Web 客户端
        
        Args:
            web_url: Cage Scan Web 界面 URL
            username: 用户名（如果需要登录）
            password: 密码（如果需要登录）
        """
        self.web_url = web_url
        self.username = username
        self.password = password
        
        # 初始化浏览器
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 无头模式
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
    
    def scan_openapi(self, openapi_content):
        """
        通过 Web 界面扫描 OpenAPI
        
        Args:
            openapi_content: OpenAPI 规范内容
        
        Returns:
            扫描结果
        """
        try:
            # 打开 Web 页面
            self.driver.get(self.web_url)
            
            # 登录（如果需要）
            if self.username and self.password:
                self._login()
            
            # 上传 OpenAPI 文件
            self._upload_openapi(openapi_content)
            
            # 等待扫描完成
            self._wait_for_scan_completion()
            
            # 获取结果
            result = self._get_scan_results()
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Web 界面扫描失败'
            }
        finally:
            self.driver.quit()
    
    def _login(self):
        """登录"""
        # 实现登录逻辑
        pass
    
    def _upload_openapi(self, content):
        """上传 OpenAPI 文件"""
        # 实现上传逻辑
        pass
    
    def _wait_for_scan_completion(self):
        """等待扫描完成"""
        # 实现等待逻辑
        pass
    
    def _get_scan_results(self):
        """获取扫描结果"""
        # 实现获取结果逻辑
        pass
```

## 3. 集成到系统

### 3.1 配置管理

创建配置文件 `config.py`：

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """配置类"""
    
    # Cage Scan 配置
    CAGE_SCAN_API_URL = os.getenv('CAGE_SCAN_API_URL', 'https://cage-scan.company.com/api')
    CAGE_SCAN_API_KEY = os.getenv('CAGE_SCAN_API_KEY', '')
    CAGE_SCAN_TIMEOUT = int(os.getenv('CAGE_SCAN_TIMEOUT', '300'))
    
    # 扫描配置
    SCAN_CONFIG = {
        'severity_level': 'medium',  # low, medium, high, critical
        'check_auth': True,
        'check_authorization': True,
        'check_input_validation': True,
        'check_data_leakage': True,
    }
```

### 3.2 在主流程中调用

```python
from cage_scan_client import CageScanClient
from config import Config

def run_cage_scan(openapi_content):
    """
    运行 Cage Scan
    
    Args:
        openapi_content: OpenAPI 规范内容
    
    Returns:
        扫描结果
    """
    # 初始化客户端
    client = CageScanClient(
        api_url=Config.CAGE_SCAN_API_URL,
        api_key=Config.CAGE_SCAN_API_KEY
    )
    
    # 执行扫描
    result = client.scan_openapi(
        openapi_content=openapi_content,
        scan_config=Config.SCAN_CONFIG
    )
    
    return result

# 在主流程中使用
def main():
    # ... 其他步骤 ...
    
    # 读取生成的 OpenAPI
    with open('openapi-generated.yml', 'r') as f:
        openapi_content = f.read()
    
    # 运行 Cage Scan
    scan_result = run_cage_scan(openapi_content)
    
    # 处理结果
    if scan_result['success']:
        print(f"扫描完成，发现 {len(scan_result.get('issues', []))} 个问题")
    else:
        print(f"扫描失败: {scan_result.get('message', '未知错误')}")
```

## 4. 输出格式处理

### 4.1 标准化输出

无论使用哪种方式调用，都需要将输出格式标准化：

```python
def normalize_scan_result(raw_result):
    """
    标准化扫描结果
    
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
        'summary': summary,
        'scan_time': raw_result.get('scan_time'),
        'scan_duration': raw_result.get('scan_duration')
    }
```

### 4.2 输出格式示例

```json
{
  "success": true,
  "issues": [
    {
      "code": "AUTH-001",
      "message": "API 端点缺少认证机制",
      "severity": "error",
      "path": ["paths", "/users", "post"],
      "recommendation": "添加 JWT 或 API Key 认证"
    },
    {
      "code": "INPUT-001",
      "message": "输入参数缺少类型验证",
      "severity": "warning",
      "path": ["paths", "/users", "get", "parameters", "0"],
      "recommendation": "添加参数类型和格式验证"
    },
    {
      "code": "DATA-001",
      "message": "响应中包含敏感信息",
      "severity": "error",
      "path": ["paths", "/users", "get", "responses", "200"],
      "recommendation": "移除或加密敏感字段"
    }
  ],
  "summary": {
    "total": 3,
    "errors": 2,
    "warnings": 1,
    "info": 0
  },
  "scan_time": "2026-04-03T10:30:00Z",
  "scan_duration": 15.5
}
```

## 5. 错误处理

### 5.1 常见错误及处理

```python
class CageScanError(Exception):
    """Cage Scan 错误基类"""
    pass

class AuthenticationError(CageScanError):
    """认证错误"""
    pass

class TimeoutError(CageScanError):
    """超时错误"""
    pass

class APIError(CageScanError):
    """API 错误"""
    pass

def handle_cage_scan_error(error):
    """
    处理 Cage Scan 错误
    
    Args:
        error: 错误对象
    
    Returns:
        错误信息
    """
    if isinstance(error, AuthenticationError):
        return {
            'success': False,
            'error_type': 'authentication',
            'message': 'Cage Scan 认证失败，请检查 API Key'
        }
    elif isinstance(error, TimeoutError):
        return {
            'success': False,
            'error_type': 'timeout',
            'message': 'Cage Scan 执行超时，请稍后重试'
        }
    elif isinstance(error, APIError):
        return {
            'success': False,
            'error_type': 'api',
            'message': f'Cage Scan API 错误: {str(error)}'
        }
    else:
        return {
            'success': False,
            'error_type': 'unknown',
            'message': f'未知错误: {str(error)}'
        }
```

### 5.2 重试机制

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=5):
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
@retry_on_failure(max_retries=3, delay=5)
def scan_with_retry(openapi_content):
    """带重试的扫描"""
    client = CageScanClient(
        api_url=Config.CAGE_SCAN_API_URL,
        api_key=Config.CAGE_SCAN_API_KEY
    )
    return client.scan_openapi(openapi_content)
```

## 6. 最佳实践

### 6.1 性能优化

1. **异步扫描**：如果支持，使用异步扫描避免阻塞
2. **缓存结果**：对相同的 OpenAPI 内容缓存扫描结果
3. **批量扫描**：如果支持，批量扫描多个 API
4. **超时设置**：合理设置超时时间

### 6.2 安全考虑

1. **API Key 保护**：
   - 使用环境变量存储 API Key
   - 不要将 API Key 提交到代码仓库
   - 定期轮换 API Key

2. **数据安全**：
   - 确保传输使用 HTTPS
   - 不要在日志中记录敏感信息
   - 及时清理临时文件

### 6.3 监控和日志

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scan_with_logging(openapi_content):
    """
    带日志记录的扫描
    """
    logger.info("开始 Cage Scan")
    
    try:
        result = run_cage_scan(openapi_content)
        
        if result['success']:
            logger.info(f"扫描完成，发现 {result['summary']['total']} 个问题")
            logger.info(f"错误: {result['summary']['errors']}, 警告: {result['summary']['warnings']}")
        else:
            logger.error(f"扫描失败: {result.get('message')}")
        
        return result
        
    except Exception as e:
        logger.error(f"扫描异常: {str(e)}", exc_info=True)
        raise
```

## 7. 集成到报告

将 Cage Scan 结果集成到最终的报告中：

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

## 8. 总结

**关键点**：
1. 根据公司提供的 link 类型选择合适的集成方式
2. 优先使用 HTTP API 调用，其次是命令行工具
3. 标准化输出格式，便于集成到报告
4. 实现完善的错误处理和重试机制
5. 注意 API Key 和数据安全
6. 添加日志记录，便于调试和监控

**下一步**：
1. 联系公司获取 Cage Scan 的详细使用文档
2. 确认 API 端点、认证方式和请求格式
3. 测试集成方案
4. 部署到生产环境
