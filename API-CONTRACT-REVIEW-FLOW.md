# API Contract Review 系统 - 完整流程文档

## 1. 场景描述

### 业务背景

Governance Team 负责 API 变更的审批和合规性检查。当用户更新 Confluence 中的 API Contract 页面后，会发送 review 邮件给 Governance Team，Governance Team 需要手动触发系统来分析 API 变更。

### 核心需求

1. 读取 Confluence 中的 API Contract 页面
2. 读取 Confluence 中的 Governance Standard 页面（固定配置）
3. 从 API Contract 生成 OpenAPI 规范
4. 获取 GitHub master 分支的 OpenAPI 规范
5. 对比两个 OpenAPI 文件，识别差异
6. 识别 Breaking Changes
7. 根据 Governance Standard 检查合规性
8. 生成 Spectral 规则并运行 Cage Scan
9. 生成详细的差异报告（包含所有检查结果）
10. 通过 Web UI 展示报告
11. 支持发送邮件通知

***

## 2. 触发机制

### 触发方式

**手动触发** - Governance Team 在收到 review 邮件后，手动触发系统

### 触发流程

```
1. 用户更新 Confluence API Contract 页面
   ↓
2. 用户发送 review 邮件给 Governance Team
   ↓
3. Governance Team 收到邮件，决定 review 这个 API 变更
   ↓
4. Governance Team 访问 Web UI
   ↓
5. 输入 Confluence API Contract 页面 ID
   ↓
6. 点击"Review"按钮（Governance Standard 页面 ID 为固定配置）
   ↓
7. 系统自动执行分析流程
   ↓
8. 生成报告并展示在 Web UI
   ↓
9. Governance Team 查看报告，做出决策
```

***

## 3. 完整流程

### 阶段 1: Web UI 输入

```
┌─────────────────────────────────────────────────────────┐
│  API Contract Review Tool - Web UI                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Confluence API Contract Page ID: [________________]    │
│                                                         │
│  [Review]                                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**用户操作**：

1. 访问 Web UI（如 <http://localhost:5000）>
2. 输入 Confluence API Contract 页面 ID
3. 点击"Review"按钮

**注意**：Governance Standard 页面 ID 为固定配置项，不需要用户输入。

**系统响应**：

- 显示执行进度
- 实时更新每个步骤的状态
- 完成后展示最终报告

***

### 阶段 2: 读取 Confluence 页面

#### 步骤 2.1: 读取 API Contract 页面

**工具**: `read_confluence_api_page`

**输入**:

- `page_id`: Confluence API Contract 页面 ID

**输出**:

```json
{
  "success": true,
  "page_id": "123456789",
  "title": "User API Contract",
  "content": "<div>...</div>",
  "content_length": 5000
}
```

**内容包含**:

- API Contract 信息
- Header 定义
- Request Body 结构
- Response Sample
- Path 入参
- 其他 API 相关信息

***

#### 步骤 2.2: 读取 Governance Standard 页面

**工具**: `read_confluence_standard`

**输入**:

- `page_id`: Confluence Governance Standard 页面 ID

**输出**:

```json
{
  "success": true,
  "page_id": "987654321",
  "title": "API Governance Standards",
  "content": "<div>...</div>",
  "content_length": 3000
}
```

**内容包含**:

- API 命名规范
- 版本控制规范
- 安全要求
- 文档要求
- 其他 Governance 标准

***

### 阶段 3: 生成 OpenAPI 规范

#### 步骤 3.1: 从 API Contract 生成 OpenAPI

**工具**: `generate_openapi_from_confluence`

**输入**:

- `confluence_content`: Confluence API Contract 页面的完整内容

**处理流程**:

1. 调用 LLM（GPT-4）
2. 解析 Confluence 内容
3. 提取 API 端点信息
4. 生成 OpenAPI 3.0 规范
5. 保存到 `openapi-generated.yml`

**输出**:

```json
{
  "success": true,
  "file_path": "openapi-generated.yml",
  "content_length": 2500,
  "preview": "openapi: 3.0.0\ninfo:\n  title: User API\n..."
}
```

**生成的 OpenAPI 格式**:

```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
  description: User Management API

paths:
  /users:
    get:
      summary: Get all users
      parameters:
        - name: limit
          in: query
          type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
```

***

### 阶段 4: 获取 GitHub master 的 OpenAPI

#### 步骤 4.1: 从 GitHub 获取 OpenAPI

**工具**: `get_github_openapi`

**输入**:

- `repo`: GitHub 仓库名称（如 `owner/repo`）
- `branch`: 分支名称（默认 `master`）
- `path`: OpenAPI 文件路径（默认 `openapi.yml`）

**处理流程**:

1. 连接到 GitHub API
2. 获取指定分支的 OpenAPI 文件
3. 保存到 `master-openapi.yml`

**输出**:

```json
{
  "success": true,
  "file_path": "master-openapi.yml",
  "content_length": 2300,
  "preview": "openapi: 3.0.0\ninfo:\n  title: User API\n..."
}
```

***

### 阶段 5: 对比 OpenAPI 文件

#### 步骤 5.1: 对比两个 OpenAPI 文件

**工具**: `compare_openapi`

**输入**:

- `generated_path`: Confluence 生成的 OpenAPI 文件路径（`openapi-generated.yml`）
- `master_path`: GitHub master 的 OpenAPI 文件路径（`master-openapi.yml`）

**对比内容**:

1. 端点差异
   - Confluence 独有的端点
   - GitHub master 独有的端点
   - 共同端点的方法差异
2. 参数差异
   - 新增参数
   - 删除参数
   - 参数类型变更
3. 响应差异
   - 新增响应状态码
   - 删除响应状态码
   - 响应结构变更

**输出**:

```json
{
  "success": true,
  "generated_only": [
    "/orders",
    "/products"
  ],
  "master_only": [
    "/legacy/users"
  ],
  "differences": [
    {
      "type": "method_added",
      "path": "/users",
      "method": "POST",
      "source": "generated"
    },
    {
      "type": "parameter_added",
      "path": "/users",
      "method": "GET",
      "parameter": "limit",
      "source": "generated"
    },
    {
      "type": "response_added",
      "path": "/users",
      "method": "GET",
      "status": "200",
      "source": "generated"
    }
  ],
  "summary": {
    "generated_only_count": 2,
    "master_only_count": 1,
    "differences_count": 3
  }
}
```

***

### 阶段 6: 识别 Breaking Changes

#### 步骤 6.1: 识别 Breaking Changes

**工具**: `identify_breaking_changes`

**输入**:

- `diff_result`: OpenAPI 对比结果 JSON 字符串

**Breaking Changes 定义**:

1. **端点删除** - 删除整个端点
2. **方法删除** - 删除端点的某个 HTTP 方法
3. **参数删除** - 删除必需参数
4. **参数类型变更** - 修改参数类型（如 string → integer）
5. **响应删除** - 删除某个响应状态码
6. **响应类型变更** - 修改响应结构

**输出**:

```json
{
  "success": true,
  "breaking_changes": [
    {
      "type": "endpoint_removed",
      "severity": "critical",
      "description": "端点 /legacy/users 被删除"
    },
    {
      "type": "parameter_removed",
      "severity": "critical",
      "description": "端点 GET /users 的参数 userId 被删除"
    },
    {
      "type": "response_removed",
      "severity": "high",
      "description": "端点 GET /users 的响应 404 被删除"
    }
  ],
  "count": 3
}
```

***

### 阶段 7: 检查 Governance Standards

#### 步骤 7.1: 检查合规性

**工具**: `check_governance_standards`

**输入**:

- `openapi_path`: OpenAPI 文件路径（`openapi-generated.yml`）
- `standard_content`: Governance Standard 页面内容

**处理流程**:

1. 调用 LLM（GPT-4）
2. 解析 Governance Standard 内容
3. 提取所有规则
4. 检查 OpenAPI 规范是否符合每个规则
5. 生成违规列表

**Governance Standard 示例**:

```markdown
# API Governance Standards

## 命名规范
- 路径使用 kebab-case（如 /user-profiles）
- 参数使用 camelCase（如 userId）

## 版本控制
- URL 中必须包含版本号（如 /v1/users）

## 安全要求
- 所有端点必须定义 security
- 生产环境必须使用 HTTPS

## 文档要求
- 所有端点必须有 description
- 所有参数必须有 description
```

**输出**:

```json
{
  "success": true,
  "violations": [
    {
      "rule": "path-kebab-case",
      "severity": "error",
      "description": "路径 /userProfiles 不符合 kebab-case 规范",
      "location": "paths./userProfiles",
      "suggestion": "改为 /user-profiles"
    },
    {
      "rule": "version-in-path",
      "severity": "error",
      "description": "URL 中缺少版本号",
      "location": "paths./users",
      "suggestion": "改为 /v1/users"
    },
    {
      "rule": "security-defined",
      "severity": "error",
      "description": "端点 /users 未定义 security",
      "location": "paths./users.get",
      "suggestion": "添加 security 定义"
    },
    {
      "rule": "description-required",
      "severity": "warning",
      "description": "端点 /users 缺少 description",
      "location": "paths./users.get",
      "suggestion": "添加 description"
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

***

### 阶段 8: Spectral Cage Scan

#### 步骤 8.1: 生成 Spectral 规则

**工具**: `generate_spectral_rules`

**输入**:

- `standard_content`: Governance Standard 页面内容

**处理流程**:

1. 调用 LLM（GPT-4）
2. 从 Governance Standard 提取规则
3. 生成 Spectral 规则配置
4. 保存到 `.spectral.generated.yml`

**输出**:

```json
{
  "success": true,
  "file_path": ".spectral.generated.yml",
  "content": "extends: spectral:oas\n..."
}
```

**生成的 Spectral 规则格式**:

```yaml
extends: spectral:oas

rules:
  path-kebab-case:
    description: 路径应使用 kebab-case
    severity: error
    given: $.paths[*]~
    then:
      function: pattern
      functionOptions:
        match: /^[a-z0-9-]+$/
  
  version-in-path:
    description: URL 中必须包含版本号
    severity: error
    given: $.paths[*]~
    then:
      function: pattern
      functionOptions:
        match: /v[0-9]+/
  
  security-required:
    description: 所有端点必须定义 security
    severity: error
    given: $.paths[*][*]
    then:
      field: security
      function: truthy
  
  description-required:
    description: 所有端点必须有 description
    severity: warning
    given: $.paths[*][*]
    then:
      field: description
      function: truthy
```

***

#### 步骤 8.2: 运行 Spectral Cage Scan

**工具**: `run_spectral`

**输入**:

- `openapi_path`: OpenAPI 文件路径（`openapi-generated.yml`）
- `rules_path`: Spectral 规则文件路径（`.spectral.generated.yml`）

**处理流程**:

1. 运行 Spectral 扫描
2. 检查 OpenAPI 规范的合规性
3. 生成违规列表

**输出**:

```json
{
  "success": false,
  "issues": [
    {
      "code": "path-kebab-case",
      "message": "Path should use kebab-case",
      "severity": "error",
      "path": ["paths", "/userProfiles"]
    },
    {
      "code": "version-in-path",
      "message": "URL must contain version number",
      "severity": "error",
      "path": ["paths", "/users"]
    },
    {
      "code": "security-required",
      "message": "Operation must have \"security\"",
      "severity": "error",
      "path": ["paths", "/users", "get"]
    },
    {
      "code": "description-required",
      "message": "Operation must have \"description\"",
      "severity": "warning",
      "path": ["paths", "/users", "get"]
    }
  ],
  "summary": {
    "total": 4,
    "errors": 3,
    "warnings": 1
  }
}
```

**Spectral Cage Scan 说明**:

- Spectral 是一个 API 规范检查工具（linter）
- 用于验证 OpenAPI/Swagger 规范的合规性
- 可以检查命名规范、文档完整性、安全性等
- 在本系统中，Spectral 用于实现类似 Cage Scan 的功能

***

### 阶段 9: 生成差异报告

#### 步骤 9.1: 生成 Markdown 报告

**工具**: `generate_diff_report`

**输入**:

- `diff_result`: OpenAPI 对比结果
- `breaking_changes`: Breaking Changes 列表
- `standard_violations`: Standard 违规列表
- `spectral_issues`: Spectral Cage Scan 结果

**处理流程**:

1. 调用 LLM（GPT-4）
2. 综合所有分析结果（包括 Spectral Cage Scan）
3. 生成结构化的 Markdown 报告
4. 保存到 `diff-report.md`

**报告格式**:

```markdown
# 📊 API Contract Review 报告

## 执行摘要
- Confluence 独有: 2 个端点
- GitHub master 独有: 1 个端点
- 差异总数: 3 个
- Breaking Changes: 3 个
- Governance Standard 违规: 4 个
- Spectral Cage Scan 问题: 4 个

## Breaking Changes ⚠️

### Critical
1. **端点删除**: `/legacy/users` 被删除
   - 严重程度: critical
   - 影响: 客户端无法访问该端点
   - 建议: 确认是否需要删除，或提供迁移方案

2. **参数删除**: `userId` 参数从 `GET /users` 被删除
   - 严重程度: critical
   - 影响: 客户端无法使用该参数
   - 建议: 确认是否需要删除，或提供替代方案

### High
3. **响应删除**: 响应状态码 `404` 从 `GET /users` 被删除
   - 严重程度: high
   - 影响: 客户端无法正确处理 404 错误
   - 建议: 恢复 404 响应

## Governance Standards 违规 🔍

### Errors
1. **path-kebab-case**: 路径 `/userProfiles` 不符合 kebab-case 规范
   - 位置: `paths./userProfiles`
   - 建议: 改为 `/user-profiles`

2. **version-in-path**: URL 中缺少版本号
   - 位置: `paths./users`
   - 建议: 改为 `/v1/users`

3. **security-defined**: 端点 `/users` 未定义 security
   - 位置: `paths./users.get`
   - 建议: 添加 security 定义

### Warnings
4. **description-required**: 端点 `/users` 缺少 description
   - 位置: `paths./users.get`
   - 建议: 添加 description

## Spectral Cage Scan 结果 🛡️

### Errors
1. **path-kebab-case**: 路径 `/userProfiles` 不符合 kebab-case 规范
   - 位置: `paths./userProfiles`
   - 建议: 改为 `/user-profiles`

2. **version-in-path**: URL 中缺少版本号
   - 位置: `paths./users`
   - 建议: 改为 `/v1/users`

3. **security-required**: 端点 `/users` 未定义 security
   - 位置: `paths./users.get`
   - 建议: 添加 security 定义

### Warnings
4. **description-required**: 端点 `/users` 缺少 description
   - 位置: `paths./users.get`
   - 建议: 添加 description

## Confluence 独有的端点

### 新增端点
1. **POST /orders**
   - 描述: 创建订单
   - 参数: orderData (body)

2. **GET /products**
   - 描述: 获取产品列表
   - 参数: limit (query)

## GitHub master 独有的端点

### 删除端点
1. **GET /legacy/users**
   - 描述: 获取用户列表（旧版）
   - 影响: Breaking Change

## 详细差异

### 新增的端点/方法
- POST /orders (新增)
- GET /products (新增)

### 删除的端点/方法
- GET /legacy/users (删除)

### 修改的端点
- GET /users
  - 新增参数: limit (query)
  - 删除参数: userId (query)
  - 新增响应: 200
  - 删除响应: 404

## 建议和行动计划

### 高优先级
1. ⚠️ **Breaking Changes**: 端点 `/legacy/users` 被删除
   - 行动: 确认是否需要删除，或提供迁移方案
   - 截止日期: [待定]

2. ⚠️ **Breaking Changes**: 参数 `userId` 被删除
   - 行动: 确认是否需要删除，或提供替代方案
   - 截止日期: [待定]

3. 🔴 **Error**: 路径不符合 kebab-case 规范
   - 行动: 修改路径为 kebab-case
   - 截止日期: [待定]

### 中优先级
4. 🔴 **Error**: URL 中缺少版本号
   - 行动: 添加版本号到 URL
   - 截止日期: [待定]

5. 🔴 **Error**: 端点未定义 security
   - 行动: 添加 security 定义
   - 截止日期: [待定]

### 低优先级
6. 🟡 **Warning**: 端点缺少 description
   - 行动: 添加 description
   - 截止日期: [待定]

---

*此报告由 API Contract Review Agent 自动生成*
*生成时间: 2026-03-29 10:00:00*
```

**输出**:

```json
{
  "success": true,
  "file_path": "diff-report.md",
  "content": "# 📊 API Contract Review 报告\n\n..."
}
```

***

### 阶段 10: 展示报告

#### 步骤 10.1: Web UI 展示

```
┌─────────────────────────────────────────────────────────┐
│  API Contract Review Tool - 报告展示                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ✅ 读取 Confluence API Contract 页面                   │
│  ✅ 读取 Confluence Governance Standard 页面             │
│  ✅ 生成 OpenAPI 规范                                 │
│  ✅ 获取 GitHub master 的 OpenAPI                        │
│  ✅ 对比两个 OpenAPI 文件                              │
│  ✅ 识别 Breaking Changes                               │
│  ✅ 检查 Governance Standards                          │
│  ✅ 生成 Spectral 规则                                 │
│  ✅ 运行 Spectral Cage Scan                             │
│  ✅ 生成差异报告                                       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  📊 API Contract Review 报告                     │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  执行摘要                                        │  │
│  │  - Confluence 独有: 2 个端点                     │  │
│  │  - GitHub master 独有: 1 个端点                  │  │
│  │  - 差异总数: 3 个                                │  │
│  │  - Breaking Changes: 3 个                        │  │
│  │  - Governance Standard 违规: 4 个                   │  │
│  │  - Spectral Cage Scan 问题: 4 个                    │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  Breaking Changes ⚠️                             │  │
│  │  [列出所有 Breaking Changes...]                   │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  Governance Standards 违规 🔍                    │  │
│  │  [列出所有违规...]                               │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  Spectral Cage Scan 结果 🛡️                      │  │
│  │  [列出所有 Spectral 问题...]                      │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  详细差异                                        │  │
│  │  [列出所有差异...]                               │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  建议和行动计划                                  │  │
│  │  [列出所有建议...]                               │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [下载报告] [发送邮件] [重新 Review]                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**功能按钮**:

- **下载报告**: 下载 `diff-report.md` 文件
- **发送邮件**: 将报告发送到指定邮箱
- **重新 Review**: 重新执行分析流程

***

### 阶段 11: 发送邮件（可选）

#### 步骤 10.1: 发送邮件通知

**功能**: 将报告发送到指定邮箱

**邮件内容**:

```
主题: API Contract Review 报告 - [API 名称]

Dear Governance Team,

API Contract Review 已完成，请查看以下报告：

[报告内容...]

如有任何问题，请联系 [联系人]。

Best regards,
API Contract Review System
```

**收件人**: 配置文件中指定的邮箱列表

***

## 4. 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│  Web UI (Flask)                                       │
│  - 输入 Confluence API Contract 页面 ID                  │
│  - 显示执行进度                                         │
│  - 展示最终报告                                         │
│  - 下载报告 / 发送邮件                                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  工作流引擎 (Workflow Engine)                          │
│  - 协调所有模块的执行                                   │
│  - 管理执行流程                                         │
│  - 处理错误和异常                                       │
│  - 状态管理                                             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  核心模块                                              │
│  - Confluence 模块: 读取页面内容                          │
│  - OpenAPI 模块: 生成和对比 OpenAPI                     │
│  - LLM 模块: 调用 LLM API 进行分析                       │
│  - Spectral 模块: 生成规则和运行扫描                      │
│  - 报告模块: 生成详细报告                                 │
│  - 邮件模块: 发送通知邮件                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  外部服务                                             │
│  - Confluence API                                     │
│  - GitHub API                                         │
│  - OpenAI API (LLM)                                   │
│  - Spectral CLI (Cage Scan）                            │
│  - SMTP (邮件发送）                                     │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

| 组件             | 技术                      | 说明                  |
| -------------- | ----------------------- | ------------------- |
| Web 框架         | Flask                   | 轻量级 Web 框架          |
| Agent 框架       | LangChain               | LLM Agent 框架        |
| LLM            | GPT-4                   | 生成 OpenAPI 和报告      |
| Confluence API | atlassian-python-api    | 读取 Confluence 页面    |
| GitHub API     | PyGithub                | 获取 GitHub 文件        |
| Spectral CLI   | @stoplight/spectral-cli | API 规范检查（Cage Scan） |
| 邮件发送           | smtplib                 | 发送邮件通知              |
| 配置管理           | python-dotenv           | 环境变量管理              |

***

## 5. 工具说明

### 5.1 Confluence API Page Tool

**名称**: `read_confluence_api_page`

**功能**: 从 Confluence 读取 API Contract 页面

**输入**:

- `page_id`: Confluence 页面 ID

**输出**:

```json
{
  "success": true,
  "page_id": "123456789",
  "title": "User API Contract",
  "content": "<div>...</div>",
  "content_length": 5000
}
```

**错误处理**:

- 页面不存在
- 权限不足
- 网络错误

***

### 5.2 Confluence Standard Tool

**名称**: `read_confluence_standard`

**功能**: 从 Confluence 读取 Governance Standard 页面

**输入**:

- `page_id`: Confluence 页面 ID

**输出**:

```json
{
  "success": true,
  "page_id": "987654321",
  "title": "API Governance Standards",
  "content": "<div>...</div>",
  "content_length": 3000
}
```

**错误处理**:

- 页面不存在
- 权限不足
- 网络错误

***

### 5.3 Generate OpenAPI Tool

**名称**: `generate_openapi_from_confluence`

**功能**: 根据 Confluence API Contract 生成 OpenAPI 规范

**输入**:

- `confluence_content`: Confluence API Contract 页面内容

**输出**:

```json
{
  "success": true,
  "file_path": "openapi-generated.yml",
  "content_length": 2500,
  "preview": "openapi: 3.0.0\ninfo:\n..."
}
```

**错误处理**:

- LLM 生成失败
- 生成的格式不正确
- 文件写入失败

***

### 5.4 GitHub OpenAPI Tool

**名称**: `get_github_openapi`

**功能**: 从 GitHub 获取 OpenAPI 文件

**输入**:

- `repo`: GitHub 仓库名称
- `branch`: 分支名称
- `path`: 文件路径

**输出**:

```json
{
  "success": true,
  "file_path": "master-openapi.yml",
  "content_length": 2300,
  "preview": "openapi: 3.0.0\ninfo:\n..."
}
```

**错误处理**:

- 仓库不存在
- 分支不存在
- 文件不存在
- 权限不足

***

### 5.5 Compare OpenAPI Tool

**名称**: `compare_openapi`

**功能**: 对比两个 OpenAPI 文件，支持筛选特定 API 路径

**输入**:

- `generated_path`: Confluence 生成的 OpenAPI 文件路径
- `master_path`: GitHub master 的 OpenAPI 文件路径
- `api_path`: （可选）要对比的特定 API 路径，如 `/users` 或 `/orders/{id}`

**输出**:

```json
{
  "success": true,
  "api_path": "/users",
  "generated_only": [...],
  "master_only": [...],
  "differences": [...],
  "summary": {
    "total_differences": 5,
    "breaking_changes": 2,
    "non_breaking_changes": 3
  }
}
```

**功能说明**:

- 如果提供了 `api_path`，只对比该路径下的 API 定义
- 如果未提供 `api_path`，对比整个 OpenAPI 文件
- 支持路径参数，如 `/orders/{id}` 会匹配 `/orders/123` 等具体路径
- 支持通配符，如 `/users/*` 会匹配 `/users`, `/users/123` 等路径

**对比内容**:

- HTTP 方法
- 请求参数
- 请求体
- 响应状态码
- 响应体结构
- 安全定义

**错误处理**:

- 文件不存在
- 格式不正确
- 解析失败
- 指定的 `api_path` 不存在

***

### 5.6 Identify Breaking Changes Tool

**名称**: `identify_breaking_changes`

**功能**: 识别 Breaking Changes

**输入**:

- `diff_result`: OpenAPI 对比结果

**输出**:

```json
{
  "success": true,
  "breaking_changes": [...],
  "count": 3
}
```

**Breaking Changes 定义**:

- 端点删除
- 方法删除
- 参数删除
- 参数类型变更
- 响应删除
- 响应类型变更

***

### 5.7 Generate Spectral Rules Tool

**名称**: `generate_spectral_rules`

**功能**: 根据 Governance Standard 生成 Spectral 规则配置

**输入**:

- `standard_content`: Governance Standard 页面内容

**输出**:

```json
{
  "success": true,
  "file_path": ".spectral.generated.yml",
  "content": "extends: spectral:oas\n..."
}
```

**生成的规则类型**:

- 命名规范规则（如 kebab-case）
- 版本控制规则（如版本号）
- 安全规则（如 security 定义）
- 文档规则（如 description）

**错误处理**:

- LLM 生成失败
- 规则格式不正确
- 文件写入失败

***

### 5.8 Run Spectral Tool

**名称**: `run_spectral`

**功能**: 运行 Spectral Cage Scan，检查 API 规范合规性

**输入**:

- `openapi_path`: OpenAPI 文件路径
- `rules_path`: Spectral 规则文件路径

**输出**:

```json
{
  "success": false,
  "issues": [...],
  "summary": {
    "total": 4,
    "errors": 3,
    "warnings": 1
  }
}
```

**检查内容**:

- 命名规范合规性
- 版本控制合规性
- 安全要求合规性
- 文档完整性

**错误处理**:

- Spectral 未安装
- 文件不存在
- 规则文件格式错误

***

### 5.9 Check Governance Standards Tool

**名称**: `check_governance_standards`

**功能**: 根据 Governance Standard 检查合规性

**输入**:

- `openapi_path`: OpenAPI 文件路径
- `standard_content`: Governance Standard 内容

**输出**:

```json
{
  "success": true,
  "violations": [...],
  "summary": {
    "total": 4,
    "errors": 3,
    "warnings": 1,
    "info": 0
  }
}
```

**检查内容**:

- 命名规范
- 版本控制
- 安全要求
- 文档要求

***

### 5.10 Generate Diff Report Tool

**名称**: `generate_diff_report`

**功能**: 生成 Markdown 格式的差异报告

**输入**:

- `diff_result`: OpenAPI 对比结果
- `breaking_changes`: Breaking Changes 列表
- `standard_violations`: Standard 违规列表
- `spectral_issues`: Spectral Cage Scan 结果

**输出**:

```json
{
  "success": true,
  "file_path": "diff-report.md",
  "content": "# 📊 API Contract Review 报告\n\n..."
}
```

**报告内容**:

- 执行摘要
- Breaking Changes
- Governance Standards 违规
- Spectral Cage Scan 结果
- 详细差异
- 建议和行动计划

***

## 6. 报告内容

### 6.1 执行摘要

包含以下信息：

- Confluence 独有的端点数量
- GitHub master 独有的端点数量
- 差异总数
- Breaking Changes 数量
- Governance Standard 违规数量
- Spectral Cage Scan 问题数量

### 6.2 Breaking Changes

按严重程度分类：

- **Critical**: 端点删除、参数删除
- **High**: 响应删除、参数类型变更
- **Medium**: 响应类型变更
- **Low**: 其他 Breaking Changes

每个 Breaking Change 包含：

- 类型
- 严重程度
- 描述
- 影响
- 建议

### 6.3 Governance Standards 违规

按严重程度分类：

- **Error**: 必须修复
- **Warning**: 建议修复
- **Info**: 信息提示

每个违规包含：

- 规则名称
- 严重程度
- 描述
- 位置
- 建议

### 6.4 Spectral Cage Scan 结果

按严重程度分类：

- **Error**: 必须修复
- **Warning**: 建议修复
- **Info**: 信息提示

每个问题包含：

- 规则代码
- 问题描述
- 严重程度
- 位置
- 建议

### 6.5 详细差异

分类列出所有差异：

- 新增的端点/方法
- 删除的端点/方法
- 修改的端点

### 6.5 建议和行动计划

按优先级分类：

- 高优先级: Breaking Changes + Errors
- 中优先级: Warnings
- 低优先级: Info

每个建议包含：

- 描述
- 行动
- 截止日期（可选）

***

## 7. 交互流程

### 7.1 用户操作流程

```
1. 访问 Web UI
   ↓
2. 输入 Confluence API Contract 页面 ID
   ↓
3. 点击"Review"按钮（Governance Standard 页面 ID 为固定配置）
   ↓
4. 等待系统执行（显示进度）
   ↓
5. 查看报告
   ↓
6. 下载报告（可选）
   ↓
7. 发送邮件（可选）
   ↓
8. 做出决策（批准/拒绝/要求修改）
```

### 7.2 系统执行流程

```
1. 接收用户输入
   ↓
2. 读取 Confluence API Contract 页面
   ↓
3. 读取 Confluence Governance Standard 页面（固定配置）
   ↓
4. 从 API Contract 生成 OpenAPI
   ↓
5. 获取 GitHub master 的 OpenAPI
   ↓
6. 对比两个 OpenAPI 文件
   ↓
7. 识别 Breaking Changes
   ↓
8. 检查 Governance Standards
   ↓
9. 生成 Spectral 规则
   ↓
10. 运行 Spectral Cage Scan
   ↓
11. 生成差异报告（包含所有结果）
   ↓
12. 展示报告
   ↓
13. 等待用户操作（下载/发送邮件）
```

***

## 8. 配置说明

### 8.1 环境变量

| 变量名                           | 说明                                         | 示例                                  |
| ----------------------------- | ------------------------------------------ | ----------------------------------- |
| `CONFLUENCE_URL`              | Confluence URL                             | `https://xxx.atlassian.net`         |
| `CONFLUENCE_TOKEN`            | Confluence API Token                       | `xxx`                               |
| `CONFLUENCE_STANDARD_PAGE_ID` | Confluence Governance Standard 页面 ID（固定配置） | `987654321`                         |
| `GITHUB_TOKEN`                | GitHub API Token                           | `ghp_xxx`                           |
| `GITHUB_REPO`                 | GitHub 仓库名称                                | `owner/repo`                        |
| `OPENAI_API_KEY`              | OpenAI API Key                             | `sk-xxx`                            |
| `SMTP_SERVER`                 | SMTP 服务器                                   | `smtp.gmail.com`                    |
| `SMTP_PORT`                   | SMTP 端口                                    | `587`                               |
| `SMTP_USERNAME`               | SMTP 用户名                                   | `user@gmail.com`                    |
| `SMTP_PASSWORD`               | SMTP 密码                                    | `xxx`                               |
| `SMTP_FROM`                   | 发件人邮箱                                      | `noreply@company.com`               |
| `SMTP_TO`                     | 收件人邮箱列表                                    | `team@company.com,lead@company.com` |

### 8.2 配置文件

```yaml
# config.yaml
confluence:
  url: "https://xxx.atlassian.net"
  token: "xxx"
  standard_page_id: "987654321"  # 固定配置

github:
  token: "ghp_xxx"
  repo: "owner/repo"

openai:
  api_key: "sk-xxx"

smtp:
  server: "smtp.gmail.com"
  port: 587
  username: "user@gmail.com"
  password: "xxx"
  from: "noreply@company.com"
  to:
    - "team@company.com"
    - "lead@company.com"
```

---

## 9. 错误处理

### 9.1 常见错误

| 错误类型 | 原因 | 处理方式 |
|---------|------|---------|
| Confluence 页面不存在 | 页面 ID 错误 | 提示用户检查页面 ID |
| Confluence 权限不足 | Token 无权限 | 提示用户检查 Token 权限 |
| GitHub 仓库不存在 | 仓库名称错误 | 提示用户检查仓库名称 |
| GitHub 权限不足 | Token 无权限 | 提示用户检查 Token 权限 |
| LLM 生成失败 | API 调用失败 | 提示用户检查 API Key |
| OpenAPI 格式错误 | 生成内容不正确 | 提示用户检查 Confluence 内容 |

### 9.2 错误处理策略

1. **友好提示**: 显示清晰的错误信息
2. **部分成功**: 尽可能生成部分报告
3. **重试机制**: 网络错误自动重试
4. **日志记录**: 记录所有错误信息

---

## 10. 性能优化

### 10.1 执行时间估算

| 步骤 | 时间 |
|------|------|
| 读取 Confluence 页面 | 1-2 秒 |
| 生成 OpenAPI | 10-30 秒 |
| 获取 GitHub OpenAPI | 1-2 秒 |
| 对比 OpenAPI | 1-2 秒 |
| 识别 Breaking Changes | 1-2 秒 |
| 检查 Governance Standards | 10-30 秒 |
| 生成报告 | 10-30 秒 |
| **总计** | **35-100 秒** |

### 10.2 优化建议

1. **并行执行**: 读取两个 Confluence 页面可以并行
2. **缓存**: 缓存 GitHub OpenAPI 文件
3. **增量更新**: 只检查变更的部分
4. **异步处理**: 使用异步 API 调用

---

## 11. 安全考虑

### 11.1 数据安全

- 敏感信息加密存储
- API Token 定期轮换
- 日志脱敏处理

### 11.2 访问控制

- Web UI 访问控制
- API 访问限流
- 用户权限管理

### 11.3 审计日志

- 记录所有操作
- 记录访问日志
- 记录错误日志

---

## 12. 扩展性

### 12.1 支持更多 API 规范

- Swagger 2.0
- GraphQL
- gRPC

### 12.2 支持更多 Governance Standard

- 自定义规则
- 规则库管理
- 规则版本控制

### 12.3 支持更多输出格式

- PDF
- HTML
- JSON

---

## 13. 总结

### 13.1 核心价值

1. **自动化**: 自动化 API Contract Review 流程
2. **准确性**: 准确识别 Breaking Changes 和违规
3. **效率**: 大幅提高 Governance Team 的审核效率
4. **透明**: 清晰的报告和可视化
5. **灵活**: 支持自定义 Governance Standard

### 13.2 使用场景

1. API 变更审核
2. API 合规性检查
3. API 文档管理
4. API 版本控制

### 13.3 下一步

1. 实现 Web UI
2. 实现所有工具
3. 实现邮件发送
4. 测试和调试
5. 部署和上线

---

## 14. 待实现功能

### 14.1 Confluence 内容提取

#### 提取策略

1. **HTML 解析方法**
   - 使用 BeautifulSoup 解析 HTML 结构
   - 识别 Confluence 特定标签和结构
   - 提取章节内容和代码块

2. **LLM 提取方法**
   - 使用 GPT-4 解析 HTML 内容
   - 提取结构化 API 信息
   - 处理复杂的自然语言描述

#### 提取内容类型

1. **API 基本信息**
   - 标题和描述
   - 版本信息
   - 作者和创建时间

2. **端点信息**
   - HTTP 方法
   - 路径
   - 路径参数
   - 查询参数

3. **请求信息**
   - 请求头
   - 请求体结构
   - 示例请求

4. **响应信息**
   - 响应状态码
   - 响应体结构
   - 示例响应

5. **安全信息**
   - 认证方式
   - 权限要求
   - 安全注意事项

#### 实现步骤

1. **开发 HTML 解析器**
   - 处理 Confluence 特定标签
   - 提取结构化内容
   - 处理嵌套结构

2. **开发 LLM 提取器**
   - 设计提示词模板
   - 处理大型页面
   - 验证提取结果

3. **集成两种方法**
   - 先用 HTML 解析提取结构化信息
   - 用 LLM 处理复杂部分
   - 合并提取结果

4. **测试和优化**
   - 测试不同格式的 Confluence 页面
   - 优化提取准确性
   - 提高处理速度

#### 技术实现

1. **依赖库**
   - BeautifulSoup4: HTML 解析
   - lxml: 高性能 XML 解析
   - openai: LLM API 调用

2. **代码结构**
   - `confluence_parser.py`: HTML 解析逻辑
   - `llm_extractor.py`: LLM 提取逻辑
   - `content_extractor.py`: 集成提取器

3. **提取流程**
   - 读取 Confluence 页面内容
   - 清理和预处理 HTML
   - 提取结构化信息
   - 验证和格式化结果

#### 示例代码

```python
# content_extractor.py
def extract_api_from_confluence(html_content, openai_api_key=None):
    """从 Confluence 内容中提取 API 信息"""
    # 1. 先用 HTML 解析提取基本结构
    basic_info = parse_html_structure(html_content)
    
    # 2. 用 LLM 处理复杂部分
    if openai_api_key:
        detailed_info = extract_with_llm(html_content, openai_api_key)
        # 合并结果
        basic_info.update(detailed_info)
    
    return basic_info
```

#### 挑战和解决方案

1. **挑战**: Confluence 页面格式多样
   **解决方案**: 设计灵活的解析器，支持多种格式
2. **挑战**: 大型页面处理
   **解决方案**: 分块处理，避免 LLM token 限制
3. **挑战**: 提取准确性
   **解决方案**: 结合规则解析和 LLM 理解，交叉验证
4. **挑战**: 性能优化
   **解决方案**: 缓存解析结果，并行处理多个页面

---

### 14.2 OpenAPI 对比优化

#### 问题描述

GPT 生成的 OpenAPI 与 GitHub master 的 OpenAPI（人工修改）格式差异大，导致对比结果噪音过多。

#### 待讨论方案

1. **标准化处理**
   - 对比前对两个文件进行标准化
   - 消除格式差异（字段顺序、缩进、描述风格等）

2. **语义对比**
   - 不对比文本，只对比 API 契约的核心语义
   - 提取 path、method、parameters、request/response body 等核心信息
   - 智能识别 Breaking Changes

3. **配置忽略规则**
   - 允许配置哪些差异可以忽略
   - 支持忽略描述、示例、格式等差异

#### 关键考虑点

- 如何定义"核心契约"
- 如何处理人工添加的元数据
- 如何平衡严格性和实用性
- 是否需要可配置的对比策略

