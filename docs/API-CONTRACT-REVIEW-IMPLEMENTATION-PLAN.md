# API Contract Review 系统 - 技术实现路径

## 1. 项目概述

本技术实现路径基于项目开发计划，详细描述 API Contract Review 系统的技术实现方案。系统采用模块化设计，分为基础架构、核心功能、Web UI 和部署集成四个主要阶段。

## 2. 技术架构

### 2.1 核心技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| Web 框架 | Flask | 2.0+ | 构建 Web UI 和核心服务 |
| LLM API | OpenAI API | - | 生成 OpenAPI 和对比分析 |
| Confluence API | atlassian-python-api | 3.41.1+ | 读取 Confluence 页面 |
| GitHub API | PyGithub | 1.58.0+ | 获取 GitHub 文件 |
| Spectral | @stoplight/spectral-cli | 6.11.0+ | API 规范检查 |
| 服务框架 | FastAPI | 0.95.0+ | Spectral 服务化部署 |
| 配置管理 | python-dotenv | 1.0.0+ | 环境变量管理 |

### 2.2 系统架构

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Web UI (Flask)     │────>│  核心服务 (Flask)    │────>│  报告生成模块       │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
         │                           │                           ▲
         │                           ▼                           │
         │                  ┌─────────────────────┐            │
         └──────────────────>│  Spectral 服务     │────────────┘
                            │ (FastAPI + Docker) │
                            └─────────────────────┘
```

## 3. 技术实现路径

### 3.1 阶段 1: 基础架构搭建（1 周）

#### 3.1.1 任务 1.1: 搭建开发环境

**实现细节：**

1. **创建项目结构**
   ```
   api-contract-review/
   ├── src/
   │   ├── config/
   │   │   └── config.py
   │   ├── services/
   │   │   ├── confluence.py
   │   │   ├── openapi.py
   │   │   ├── github.py
   │   │   └── spectral.py
   │   ├── web/
   │   │   ├── app.py
   │   │   ├── templates/
   │   │   └── static/
   │   └── utils/
   ├── spectral-service/
   │   ├── app.py
   │   ├── Dockerfile
   │   └── requirements.txt
   ├── requirements.txt
   ├── .env.example
   └── README.md
   ```

2. **创建虚拟环境**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```env
   # .env
   CONFLUENCE_URL=https://your-confluence-instance.atlassian.net
   CONFLUENCE_USERNAME=your-username
   CONFLUENCE_API_TOKEN=your-api-token
   OPENAI_API_KEY=your-openai-api-key
   GITHUB_TOKEN=your-github-token
   SPECTRAL_SERVICE_URL=http://localhost:8000
   ```

#### 3.1.2 任务 1.2: 实现 Confluence 客户端

**实现细节：**

1. **安装 atlassian-python-api**
   ```bash
   pip install atlassian-python-api
   ```

2. **实现 Confluence 服务**
   ```python
   # src/services/confluence.py
   from atlassian import Confluence
   import os
   from dotenv import load_dotenv

   load_dotenv()

   class ConfluenceService:
       def __init__(self):
           self.confluence = Confluence(
               url=os.getenv('CONFLUENCE_URL'),
               username=os.getenv('CONFLUENCE_USERNAME'),
               password=os.getenv('CONFLUENCE_API_TOKEN')
           )

       def get_page_content(self, page_id):
           """获取 Confluence 页面内容"""
           try:
               page = self.confluence.get_page_by_id(page_id, expand='body.storage')
               return page['body']['storage']['value']
           except Exception as e:
               print(f"Error getting page content: {e}")
               return None

       def get_page_title(self, page_id):
           """获取 Confluence 页面标题"""
           try:
               page = self.confluence.get_page_by_id(page_id)
               return page['title']
           except Exception as e:
               print(f"Error getting page title: {e}")
               return None
   ```

3. **测试 API 调用**
   ```python
   # test_confluence.py
   from src.services.confluence import ConfluenceService

   def test_confluence():
       service = ConfluenceService()
       page_id = "123456789"
       content = service.get_page_content(page_id)
       title = service.get_page_title(page_id)
       print(f"Page Title: {title}")
       print(f"Content Length: {len(content) if content else 0}")

   if __name__ == "__main__":
       test_confluence()
   ```

#### 3.1.3 任务 1.3: 部署 Spectral 服务

**实现细节：**

1. **创建 Spectral 服务**
   ```python
   # spectral-service/app.py
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

           # 构建命令
           cmd = ['spectral', 'lint', openapi_file, '--format', 'json']
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
               issues = []
           else:
               issues = json.loads(result.stdout)

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
   ```

2. **创建 Dockerfile**
   ```dockerfile
   # spectral-service/Dockerfile
   FROM node:16-alpine

   RUN npm install -g @stoplight/spectral-cli

   WORKDIR /app

   COPY . .

   RUN npm install
   RUN pip install -r requirements.txt

   EXPOSE 8000

   CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **构建和运行服务**
   ```bash
   # 构建镜像
   docker build -t spectral-service .
   
   # 运行容器
   docker run -d -p 8000:8000 --name spectral-service spectral-service
   ```

4. **测试服务可用性**
   ```bash
   curl -X POST http://localhost:8000/scan \
     -H "Content-Type: application/json" \
     -d '{"openapi_content": "openapi: 3.0.0\ninfo:\n  title: Test API\n  version: 1.0.0\npaths:\n  /test:\n    get:\n      responses:\n        \"200\":\n          description: OK"}'
   ```

### 3.2 阶段 2: 核心功能实现（2 周）

#### 3.2.1 任务 2.1: OpenAPI 生成模块

**实现细节：**

1. **安装 OpenAI SDK**
   ```bash
   pip install openai
   ```

2. **设计 Prompt 模板**
   ```python
   # src/services/prompts.py
   OPENAPI_GENERATION_PROMPT = """
   You are an expert API designer. Based on the following Confluence page content, generate a valid OpenAPI 3.0 specification.

   Confluence Content:
   {content}

   Requirements:
   1. Generate a complete OpenAPI 3.0 YAML specification
   2. Include all API endpoints mentioned in the content
   3. Define appropriate request/response schemas
   4. Include proper error responses
   5. Ensure the specification is valid OpenAPI 3.0

   Output only the OpenAPI YAML, no other text.
   """
   ```

3. **实现 OpenAI API 调用**
   ```python
   # src/services/openapi.py
   import openai
   import os
   from dotenv import load_dotenv
   from src.services.prompts import OPENAPI_GENERATION_PROMPT

   load_dotenv()
   openai.api_key = os.getenv('OPENAI_API_KEY')

   class OpenAPIService:
       def generate_openapi(self, confluence_content):
           """从 Confluence 内容生成 OpenAPI 规范"""
           try:
               prompt = OPENAPI_GENERATION_PROMPT.format(content=confluence_content)
               response = openai.ChatCompletion.create(
                   model="gpt-4",
                   messages=[
                       {"role": "system", "content": "You are an expert API designer."},
                       {"role": "user", "content": prompt}
                   ],
                   temperature=0.1,
                   max_tokens=4000
               )
               return response.choices[0].message.content
           except Exception as e:
               print(f"Error generating OpenAPI: {e}")
               return None

       def validate_openapi(self, openapi_content):
           """验证 OpenAPI 规范"""
           # 可以使用 openapi-spec-validator 库进行验证
           try:
               from openapi_spec_validator import validate_spec
               from openapi_spec_validator.readers import read_from_content
               spec_dict, _ = read_from_content(openapi_content)
               validate_spec(spec_dict)
               return True
           except Exception as e:
               print(f"OpenAPI validation error: {e}")
               return False
   ```

4. **添加输出验证**
   ```python
   # 安装验证库
   pip install openapi-spec-validator
   ```

#### 3.2.2 任务 2.2: OpenAPI 对比模块

**实现细节：**

1. **安装 PyGithub**
   ```bash
   pip install PyGithub
   ```

2. **实现 GitHub API 集成**
   ```python
   # src/services/github.py
   from github import Github
   import os
   from dotenv import load_dotenv

   load_dotenv()

   class GithubService:
       def __init__(self):
           self.github = Github(os.getenv('GITHUB_TOKEN'))

       def get_file_content(self, repo_owner, repo_name, file_path, branch="master"):
           """获取 GitHub 文件内容"""
           try:
               repo = self.github.get_repo(f"{repo_owner}/{repo_name}")
               content = repo.get_contents(file_path, ref=branch)
               return content.decoded_content.decode('utf-8')
           except Exception as e:
               print(f"Error getting GitHub file: {e}")
               return None
   ```

3. **设计对比 Prompt**
   ```python
   # src/services/prompts.py
   OPENAPI_COMPARISON_PROMPT = """
   You are an expert API reviewer. Compare the following two OpenAPI specifications and identify all differences.

   Generated OpenAPI (from Confluence):
   {generated_openapi}

   Master OpenAPI (from GitHub):
   {master_openapi}

   Requirements:
   1. Identify all API endpoint differences
   2. Identify all Breaking Changes
   3. Categorize differences by severity
   4. Provide clear descriptions of each change
   5. Output in JSON format with the following structure:
   {{
     "breaking_changes": [
       {{
         "type": "string",
         "severity": "Critical|High|Medium|Low",
         "description": "string",
         "path": "string",
         "method": "string"
       }}
     ],
     "non_breaking_changes": [
       {{
         "type": "string",
         "description": "string",
         "path": "string",
         "method": "string"
       }}
     ],
     "summary": {{
       "total_changes": number,
       "breaking_changes": number,
       "non_breaking_changes": number
     }}
   }}
   """
   ```

4. **实现差异分析**
   ```python
   # src/services/openapi.py
   def compare_openapi(self, generated_openapi, master_openapi):
       """对比两个 OpenAPI 规范"""
       try:
           prompt = OPENAPI_COMPARISON_PROMPT.format(
               generated_openapi=generated_openapi,
               master_openapi=master_openapi
           )
           response = openai.ChatCompletion.create(
               model="gpt-4",
               messages=[
                   {"role": "system", "content": "You are an expert API reviewer."},
                   {"role": "user", "content": prompt}
               ],
               temperature=0.1,
               max_tokens=4000
           )
           return response.choices[0].message.content
       except Exception as e:
           print(f"Error comparing OpenAPI: {e}")
           return None
   ```

#### 3.2.3 任务 2.3: Spectral 集成

**实现细节：**

1. **实现服务调用**
   ```python
   # src/services/spectral.py
   import requests
   import os
   from dotenv import load_dotenv

   load_dotenv()

   class SpectralService:
       def __init__(self):
           self.service_url = os.getenv('SPECTRAL_SERVICE_URL', 'http://localhost:8000')

       def scan_openapi(self, openapi_content, config_content=None):
           """调用 Spectral 服务扫描 OpenAPI"""
           try:
               response = requests.post(
                   f"{self.service_url}/scan",
                   json={
                       "openapi_content": openapi_content,
                       "config_content": config_content
                   },
                   timeout=30
               )
               if response.status_code == 200:
                   return response.json()
               else:
                   print(f"Spectral service error: {response.text}")
                   return None
           except Exception as e:
               print(f"Error calling Spectral service: {e}")
               return None
   ```

2. **处理扫描结果**
   ```python
   def process_spectral_results(self, results):
       """处理 Spectral 扫描结果"""
       if not results:
           return {"success": False, "issues": []}

       # 格式化结果
       formatted_issues = []
       for issue in results.get("issues", []):
           formatted_issues.append({
               "rule": issue.get("rule", ""),
               "severity": issue.get("severity", "info"),
               "message": issue.get("message", ""),
               "path": issue.get("path", ""),
               "fix": issue.get("fix", "")
           })

       return {
           "success": True,
           "issues": formatted_issues,
           "summary": results.get("summary", {})
       }
   ```

3. **集成到流程中**
   ```python
   # src/services/flow.py
   class ReviewFlow:
       def __init__(self):
           self.confluence_service = ConfluenceService()
           self.openapi_service = OpenAPIService()
           self.github_service = GithubService()
           self.spectral_service = SpectralService()

       def run_review(self, confluence_page_id, github_repo, github_file, github_branch="master"):
           """运行完整的审查流程"""
           # 1. 读取 Confluence 页面
           content = self.confluence_service.get_page_content(confluence_page_id)
           if not content:
               return {"error": "Failed to get Confluence content"}

           # 2. 生成 OpenAPI
           generated_openapi = self.openapi_service.generate_openapi(content)
           if not generated_openapi:
               return {"error": "Failed to generate OpenAPI"}

           # 3. 获取 GitHub OpenAPI
           master_openapi = self.github_service.get_file_content(
               github_repo.split('/')[0],
               github_repo.split('/')[1],
               github_file,
               github_branch
           )
           if not master_openapi:
               return {"error": "Failed to get GitHub OpenAPI"}

           # 4. 对比 OpenAPI
           comparison_result = self.openapi_service.compare_openapi(
               generated_openapi, master_openapi
           )
           if not comparison_result:
               return {"error": "Failed to compare OpenAPI"}

           # 5. 运行 Spectral 扫描
           spectral_result = self.spectral_service.scan_openapi(generated_openapi)
           if not spectral_result:
               return {"error": "Failed to run Spectral scan"}

           # 6. 处理结果
           spectral_processed = self.spectral_service.process_spectral_results(spectral_result)

           return {
               "success": True,
               "generated_openapi": generated_openapi,
               "master_openapi": master_openapi,
               "comparison": comparison_result,
               "spectral": spectral_processed
           }
   ```

### 3.3 阶段 3: Web UI 和报告（2 周）

#### 3.3.1 任务 3.1: Web UI 开发

**实现细节：**

1. **创建 Flask 应用**
   ```python
   # src/web/app.py
   from flask import Flask, render_template, request, jsonify
   from src.services.flow import ReviewFlow

   app = Flask(__name__)
   review_flow = ReviewFlow()

   @app.route('/')
   def index():
       return render_template('index.html')

   @app.route('/review', methods=['POST'])
   def review():
       try:
           data = request.json
           confluence_page_id = data['confluence_page_id']
           github_repo = data['github_repo']
           github_file = data['github_file']
           github_branch = data.get('github_branch', 'master')

           # 运行审查流程
           result = review_flow.run_review(
               confluence_page_id, github_repo, github_file, github_branch
           )

           return jsonify(result)
       except Exception as e:
           return jsonify({"error": str(e)}), 500

   if __name__ == '__main__':
       app.run(debug=True)
   ```

2. **创建输入页面**
   ```html
   <!-- src/web/templates/index.html -->
   <!DOCTYPE html>
   <html>
   <head>
       <title>API Contract Review</title>
       <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
   </head>
   <body>
       <div class="container mt-5">
           <h1>API Contract Review Tool</h1>
           <form id="reviewForm" class="mt-4">
               <div class="mb-3">
                   <label for="confluencePageId" class="form-label">Confluence Page ID</label>
                   <input type="text" class="form-control" id="confluencePageId" required>
               </div>
               <div class="mb-3">
                   <label for="githubRepo" class="form-label">GitHub Repo (owner/repo)</label>
                   <input type="text" class="form-control" id="githubRepo" required>
               </div>
               <div class="mb-3">
                   <label for="githubFile" class="form-label">GitHub OpenAPI File Path</label>
                   <input type="text" class="form-control" id="githubFile" value="openapi.yml" required>
               </div>
               <div class="mb-3">
                   <label for="githubBranch" class="form-label">GitHub Branch</label>
                   <input type="text" class="form-control" id="githubBranch" value="master">
               </div>
               <button type="submit" class="btn btn-primary">Review</button>
           </form>
           <div id="loading" class="mt-4 d-none">
               <div class="spinner-border" role="status">
                   <span class="visually-hidden">Loading...</span>
               </div>
               <p class="mt-2">Processing...</p>
           </div>
           <div id="result" class="mt-4 d-none"></div>
       </div>
       <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
       <script>
           document.getElementById('reviewForm').addEventListener('submit', async function(e) {
               e.preventDefault();
               
               const loading = document.getElementById('loading');
               const result = document.getElementById('result');
               
               loading.classList.remove('d-none');
               result.classList.add('d-none');
               
               const data = {
                   confluence_page_id: document.getElementById('confluencePageId').value,
                   github_repo: document.getElementById('githubRepo').value,
                   github_file: document.getElementById('githubFile').value,
                   github_branch: document.getElementById('githubBranch').value
               };
               
               try {
                   const response = await fetch('/review', {
                       method: 'POST',
                       headers: {
                           'Content-Type': 'application/json'
                       },
                       body: JSON.stringify(data)
                   });
                   
                   const resultData = await response.json();
                   
                   if (resultData.success) {
                       result.innerHTML = `
                           <h2>Review Results</h2>
                           <div class="mt-3">
                               <h3>Comparison Summary</h3>
                               <pre>${JSON.stringify(resultData.comparison, null, 2)}</pre>
                           </div>
                           <div class="mt-3">
                               <h3>Spectral Results</h3>
                               <pre>${JSON.stringify(resultData.spectral, null, 2)}</pre>
                           </div>
                       `;
                   } else {
                       result.innerHTML = `<div class="alert alert-danger">Error: ${resultData.error}</div>`;
                   }
               } catch (error) {
                   result.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
               } finally {
                   loading.classList.add('d-none');
                   result.classList.remove('d-none');
               }
           });
       </script>
   </body>
   </html>
   ```

3. **添加实时进度**
   - 使用 WebSocket 或轮询实现实时进度更新

#### 3.3.2 任务 3.2: 报告生成

**实现细节：**

1. **设计报告模板**
   ```python
   # src/services/report.py
   class ReportGenerator:
       def generate_html_report(self, review_result):
           """生成 HTML 报告"""
           # 实现 HTML 报告生成逻辑
           pass

       def generate_pdf_report(self, review_result):
           """生成 PDF 报告"""
           # 实现 PDF 报告生成逻辑
           pass
   ```

2. **实现数据汇总**
   ```python
   def summarize_results(self, review_result):
       """汇总结果数据"""
       comparison = review_result.get('comparison', {})
       spectral = review_result.get('spectral', {})

       summary = {
           "total_changes": comparison.get('summary', {}).get('total_changes', 0),
           "breaking_changes": comparison.get('summary', {}).get('breaking_changes', 0),
           "non_breaking_changes": comparison.get('summary', {}).get('non_breaking_changes', 0),
           "spectral_issues": spectral.get('summary', {}).get('total', 0),
           "spectral_errors": spectral.get('summary', {}).get('errors', 0),
           "spectral_warnings": spectral.get('summary', {}).get('warnings', 0)
       }

       return summary
   ```

3. **添加可视化图表**
   - 使用 Chart.js 或其他图表库实现数据可视化

#### 3.3.3 任务 3.3: 测试和优化

**实现细节：**

1. **端到端测试**
   ```python
   # tests/test_end_to_end.py
   def test_full_review_flow():
       # 实现端到端测试
       pass
   ```

2. **性能优化**
   - 实现缓存机制
   - 优化 API 调用
   - 使用异步处理

3. **错误处理**
   - 添加详细的错误日志
   - 实现重试机制
   - 提供友好的错误提示

### 3.4 阶段 4: 部署和集成（1 周）

#### 3.4.1 任务 4.1: 部署到测试环境

**实现细节：**

1. **配置 CI/CD**
   - 使用 GitHub Actions 或 Jenkins
   - 配置自动测试和部署

2. **自动化测试**
   - 实现单元测试
   - 实现集成测试
   - 实现端到端测试

3. **监控设置**
   - 集成 Prometheus 和 Grafana
   - 配置日志收集
   - 设置告警机制

#### 3.4.2 任务 4.2: Cage Scan 集成（可选）

**实现细节：**

1. **集成公司 Cage Scan 服务**
   ```python
   # src/services/cage_scan.py
   class CageScanService:
       def __init__(self):
           self.service_url = os.getenv('CAGE_SCAN_URL')
           self.api_key = os.getenv('CAGE_SCAN_API_KEY')

       def scan_openapi(self, openapi_content):
           """调用 Cage Scan 服务"""
           # 实现 Cage Scan 调用
           pass
   ```

2. **测试 API 调用**
   - 测试 Cage Scan API 调用
   - 验证返回结果

3. **结果处理**
   - 处理 Cage Scan 结果
   - 集成到报告中

#### 3.4.3 任务 4.3: 文档和培训

**实现细节：**

1. **更新技术文档**
   - 更新 README.md
   - 编写架构文档
   - 编写 API 文档

2. **编写用户指南**
   - 编写使用手册
   - 录制演示视频
   - 创建 FAQ 文档

3. **内部培训**
   - 组织技术培训
   - 进行演示和 Q&A
   - 收集反馈和改进建议

## 4. 关键技术挑战和解决方案

### 4.1 Confluence API 访问限制
**挑战：** Confluence API 可能有访问频率限制
**解决方案：** 实现重试机制和缓存

### 4.2 OpenAI API 成本
**挑战：** GPT-4 API 调用成本较高
**解决方案：** 设置使用限制和监控，优化 Prompt 设计

### 4.3 扫描性能
**挑战：** Spectral 扫描可能较慢
**解决方案：** 优化并行处理和异步操作，使用服务化部署

### 4.4 公司环境集成
**挑战：** 与公司内部系统集成可能复杂
**解决方案：** 预留集成时间和测试，使用配置驱动的集成方案

## 5. 技术债务管理

### 5.1 代码质量
- 遵循 PEP 8 编码规范
- 使用类型提示
- 编写单元测试

### 5.2 文档维护
- 保持文档与代码同步
- 使用自动化文档生成工具
- 定期更新技术文档

### 5.3 依赖管理
- 固定依赖版本
- 定期更新依赖
- 监控依赖安全漏洞

## 6. 总结

本技术实现路径详细描述了 API Contract Review 系统的技术实现方案，包括：

1. **基础架构搭建**：开发环境、Confluence 客户端、Spectral 服务
2. **核心功能实现**：OpenAPI 生成、OpenAPI 对比、Spectral 集成
3. **Web UI 和报告**：Web 界面、报告生成、测试优化
4. **部署和集成**：测试环境部署、Cage Scan 集成、文档培训

通过遵循此技术实现路径，可以在 6-8 周内完成系统开发和部署，为 Governance Team 提供一个高效、可靠的 API 变更审查工具。