# Confluence 集成与数据解析方案

## 1. 概述

本文档详细讨论如何与 Confluence 集成，读取 API Contract 页面数据并进行解析，以支持 API Contract Review 系统的核心功能。

## 2. Confluence 集成方案

### 2.1 技术选型

| 技术/库 | 版本 | 用途 |
|--------|------|------|
| atlassian-python-api | 最新版 | Confluence API 客户端 |
| Python | 3.9+ | 开发语言 |
| python-dotenv | 最新版 | 环境变量管理 |

### 2.2 认证方式

Confluence 提供多种认证方式，推荐使用以下方式：

1. **API Token 认证**：
   - 适用于 Cloud 版本
   - 需要创建 API Token
   - 格式：`email:api_token`

2. **Basic Auth**：
   - 适用于 Server 版本
   - 需要用户名和密码

3. **OAuth 2.0**：
   - 更安全的认证方式
   - 适用于生产环境

### 2.3 环境配置

创建 `.env` 文件，包含以下配置：

```env
# Confluence 配置
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your-api-token

# 或者使用 Basic Auth（Server 版本）
# CONFLUENCE_USERNAME=username
# CONFLUENCE_PASSWORD=password
```

## 3. 数据读取实现

### 3.1 核心代码结构

```python
from atlassian import Confluence
from dotenv import load_dotenv
import os

class ConfluenceClient:
    def __init__(self):
        load_dotenv()
        self.confluence = Confluence(
            url=os.getenv('CONFLUENCE_URL'),
            username=os.getenv('CONFLUENCE_USERNAME'),
            password=os.getenv('CONFLUENCE_API_TOKEN')  # 或 CONFLUENCE_PASSWORD
        )
    
    def get_page_content(self, page_id):
        """
        获取 Confluence 页面内容
        """
        try:
            page = self.confluence.get_page_by_id(page_id, expand='body.storage')
            return {
                "success": True,
                "page_id": page_id,
                "title": page['title'],
                "content": page['body']['storage']['value'],
                "content_length": len(page['body']['storage']['value'])
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

### 3.2 调用示例

```python
client = ConfluenceClient()
result = client.get_page_content('123456789')
if result['success']:
    print(f"Page title: {result['title']}")
    print(f"Content length: {result['content_length']}")
else:
    print(f"Error: {result['error']}")
```

## 4. 数据解析方案

### 4.1 页面结构分析

根据 PRD 中的描述，Confluence API Contract 页面包含以下内容：

- API Contract 信息
- Header 定义
- Request Body 结构
- Response Sample
- Path 入参
- 其他 API 相关信息

### 4.2 解析策略

#### 4.2.1 HTML 解析

使用 BeautifulSoup 解析 HTML 内容：

```python
from bs4 import BeautifulSoup

class ConfluenceParser:
    def parse_content(self, html_content):
        """
        解析 Confluence 页面内容
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取 API Contract 信息
        api_info = self._extract_api_info(soup)
        
        # 提取 Header 定义
        headers = self._extract_headers(soup)
        
        # 提取 Request Body 结构
        request_body = self._extract_request_body(soup)
        
        # 提取 Response Sample
        response_sample = self._extract_response_sample(soup)
        
        # 提取 Path 入参
        path_params = self._extract_path_params(soup)
        
        return {
            "api_info": api_info,
            "headers": headers,
            "request_body": request_body,
            "response_sample": response_sample,
            "path_params": path_params
        }
    
    def _extract_api_info(self, soup):
        # 实现 API 信息提取逻辑
        pass
    
    def _extract_headers(self, soup):
        # 实现 Header 提取逻辑
        pass
    
    def _extract_request_body(self, soup):
        # 实现 Request Body 提取逻辑
        pass
    
    def _extract_response_sample(self, soup):
        # 实现 Response Sample 提取逻辑
        pass
    
    def _extract_path_params(self, soup):
        # 实现 Path 入参提取逻辑
        pass
```

#### 4.2.2 基于页面结构的解析

Confluence 页面通常使用特定的结构和宏，我们可以基于这些结构进行解析：

1. **标题层级**：使用 `<h1>`, `<h2>`, `<h3>` 标签识别不同部分
2. **代码块**：使用 `<pre>` 或 `<code>` 标签提取代码示例
3. **表格**：使用 `<table>` 标签提取结构化数据
4. **列表**：使用 `<ul>`, `<ol>` 标签提取列表信息

### 4.3 解析规则

根据常见的 API Contract 页面结构，制定以下解析规则：

1. **API 基本信息**：
   - 从页面标题和首节提取
   - 包含 API 名称、版本、描述等

2. **Header 定义**：
   - 查找包含 "Header" 或 "请求头" 的章节
   - 解析表格或列表形式的 Header 定义

3. **Request Body 结构**：
   - 查找包含 "Request Body" 或 "请求体" 的章节
   - 提取 JSON 或其他格式的示例

4. **Response Sample**：
   - 查找包含 "Response" 或 "响应" 的章节
   - 提取不同状态码的响应示例

5. **Path 入参**：
   - 查找包含 "Path" 或 "路径参数" 的章节
   - 解析参数名称、类型、是否必填等信息

## 5. 实现注意事项

### 5.1 异常处理

- 处理页面不存在的情况
- 处理认证失败的情况
- 处理网络连接问题
- 处理解析失败的情况

### 5.2 性能优化

- 缓存页面内容，避免重复请求
- 使用异步请求提高并发性能
- 优化解析逻辑，减少不必要的计算

### 5.3 兼容性

- 支持不同版本的 Confluence API
- 适应不同的页面结构和格式
- 处理特殊字符和格式问题

## 6. 测试方案

### 6.1 单元测试

- 测试 Confluence 客户端连接
- 测试页面内容获取
- 测试不同类型页面的解析

### 6.2 集成测试

- 测试完整的集成流程
- 测试异常情况下的处理
- 测试不同类型的 API Contract 页面

## 7. 示例输出

### 7.1 页面内容获取示例

```json
{
  "success": true,
  "page_id": "123456789",
  "title": "User API Contract",
  "content": "<div class=\"content\">...</div>",
  "content_length": 5000
}
```

### 7.2 解析结果示例

```json
{
  "api_info": {
    "name": "User API",
    "version": "v1",
    "description": "用户管理 API"
  },
  "headers": [
    {
      "name": "Authorization",
      "required": true,
      "description": "Bearer token"
    }
  ],
  "request_body": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string"
      },
      "email": {
        "type": "string"
      }
    }
  },
  "response_sample": {
    "200": {
      "status": "success",
      "data": {
        "id": 1,
        "name": "John Doe"
      }
    }
  },
  "path_params": [
    {
      "name": "id",
      "type": "integer",
      "required": true,
      "description": "用户 ID"
    }
  ]
}
```

## 8. 后续优化方向

1. **智能解析**：使用 LLM 辅助解析复杂的页面结构
2. **模板识别**：识别常见的 API Contract 页面模板
3. **自动化测试**：自动验证解析结果的准确性
4. **插件化设计**：支持不同类型的页面结构和格式

## 9. 结论

通过 atlassian-python-api 库与 Confluence 集成，结合 BeautifulSoup 进行 HTML 解析，可以有效地读取和解析 API Contract 页面内容。这种方案具有良好的可扩展性和兼容性，能够适应不同类型的 API Contract 页面结构。

在实现过程中，需要注意异常处理、性能优化和兼容性问题，确保系统能够稳定运行。同时，通过单元测试和集成测试，可以验证实现的正确性和可靠性。