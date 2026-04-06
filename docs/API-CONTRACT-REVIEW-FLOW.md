# API Contract Review 系统 - 完整流程文档

## 相关文档

本文档是 API Contract Review 系统的核心流程文档。各专项模块的详细实现请参考以下文档：

| 文档                                                       | 说明                           |
| -------------------------------------------------------- | ---------------------------- |
| [CONFLUENCE-INTEGRATION.md](./CONFLUENCE-INTEGRATION.md) | Confluence 集成与数据解析方案         |
| [OPENAPI-GENERATION.md](./OPENAPI-GENERATION.md)         | OpenAPI 生成方案（Agent + Prompt） |
| [OPENAPI-COMPARISON.md](./OPENAPI-COMPARISON.md)         | OpenAPI 对比方案（Agent + Prompt） |
| [CAGE-SCAN-INTEGRATION.md](./CAGE-SCAN-INTEGRATION.md)   | Cage Scan 集成方案               |
| [SPECTRAL-INTEGRATION.md](./SPECTRAL-INTEGRATION.md)     | Spectral 集成方案（支持服务化部署）       |

## 1. 场景描述

### 业务背景

Governance Team 负责 API 变更的审批和合规性检查。当用户更新 Confluence 中的 API Contract 页面后，会发送 review 邮件给 Governance Team，Governance Team 需要手动触发系统来分析 API 变更。

### 核心需求

1. 读取 Confluence 中的 API Contract 页面
2. 从 API Contract 生成 OpenAPI 规范
3. 获取 GitHub master 分支的 OpenAPI 规范
4. 对比两个 OpenAPI 文件，识别差异
5. 识别 Breaking Changes
6. 运行 Spectral 扫描（优先）
7. 运行 Cage Scan（后续集成）
8. 生成详细的差异报告（包含所有检查结果）
9. 通过 Web UI 展示报告

***

## 2. 触发机制

### 触发方式

**手动触发** - Governance Team 手动触发系统

### 触发流程

```
1. 用户更新 Confluence API Contract 页面
   ↓
2. Governance Team 决定 review 这个 API 变更
   ↓
3. Governance Team 访问 Web UI
   ↓
4. 输入 Confluence API Contract 页面 ID
   ↓
5. 点击"Review"按钮
   ↓
6. 系统自动执行分析流程
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

> **详细实现参考**: [CONFLUENCE-INTEGRATION.md](./CONFLUENCE-INTEGRATION.md)

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

**实现方式**: 使用 Agent + Prompt 方案

> **详细实现参考**: [OPENAPI-GENERATION.md](./OPENAPI-GENERATION.md)

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

**实现方式**: 使用 Agent + Prompt 方案

> **详细实现参考**: [OPENAPI-COMPARISON.md](./OPENAPI-COMPARISON.md)

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

**实现方式**: 与 OpenAPI 对比一起，通过 Agent + Prompt 完成

> **详细实现参考**: [OPENAPI-COMPARISON.md](./OPENAPI-COMPARISON.md) - 包含完整的 Breaking Changes 识别 Prompt

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

### 阶段 7: 扫描流程

#### 步骤 7.1: 运行 Cage Scan

**工具**: `run_cage_scan`

**输入**:

- `openapi_path`: OpenAPI 文件路径（`openapi-generated.yml`）

**处理流程**:

1. 运行 Cage Scan
2. 检查 API 安全合规性
3. 生成安全问题列表

**输出**:

```json
{
  "success": false,
  "issues": [
    {
      "code": "security-vulnerability",
      "message": "API 存在安全漏洞",
      "severity": "error",
      "path": ["paths", "/users", "post"]
    }
  ],
  "summary": {
    "total": 1,
    "errors": 1,
    "warnings": 0
  }
}
```

**Cage Scan 说明**:

- Cage Scan 是一个 API 安全扫描工具
- 用于检测 API 中的安全漏洞和风险
- 可以检查认证、授权、输入验证等安全问题
- 提供详细的安全风险报告

**集成方式**: 通过 HTTP API 调用公司提供的 Cage Scan 服务

> **详细实现参考**: [CAGE-SCAN-INTEGRATION.md](./CAGE-SCAN-INTEGRATION.md)

***

#### 步骤 7.2: 运行 Spectral 扫描

**工具**: `run_spectral`

**输入**:

- `openapi_path`: OpenAPI 文件路径（`openapi-generated.yml`）

**处理流程**:

1. 运行 Spectral 扫描（使用预定义的 Spectral 规则）
2. 检查 OpenAPI 规范的合规性
3. 生成违规列表

**集成方式**: 支持多种方式

- **方式 0（推荐）**: 部署为 HTTP 服务，通过 API 调用
- **方式 1**: 本地命令行调用
- **方式 2**: 使用 Python 库
- **方式 3**: 使用 Docker

> **详细实现参考**: [SPECTRAL-INTEGRATION.md](./SPECTRAL-INTEGRATION.md)

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

**Spectral 扫描说明**:

- Spectral 是一个 API 规范检查工具（linter）
- 用于验证 OpenAPI/Swagger 规范的合规性
- 可以检查命名规范、文档完整性、安全性等
- 在本系统中，Spectral 用于实现 API 规范的全面检查

***

### 阶段 8: 生成差异报告

#### 步骤 8.1: 生成 Markdown 报告

**工具**: `generate_diff_report`

**输入**:

- `diff_result`: OpenAPI 对比结果
- `breaking_changes`: Breaking Changes 列表
- `cage_scan_result`: Cage Scan 结果
- `spectral_issues`: Spectral 扫描结果

**处理流程**:

1. 调用 LLM（GPT-4）
2. 综合所有分析结果（包括 Cage Scan 和 Spectral 扫描）
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
- Cage Scan 问题: 1 个
- Spectral 扫描问题: 4 个

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

## Cage Scan 结果 🛡️

### Errors
1. **security-vulnerability**: API 存在安全漏洞
   - 位置: `paths./users.post`
   - 建议: 修复安全漏洞

## Spectral 扫描结果 📋

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
│  ✅ 生成 OpenAPI 规范                                 │
│  ✅ 获取 GitHub master 的 OpenAPI                        │
│  ✅ 对比两个 OpenAPI 文件                              │
│  ✅ 识别 Breaking Changes                               │
│  ✅ 运行 Cage Scan                                      │
│  ✅ 运行 Spectral 扫描                                 │
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
│  │  - Cage Scan 问题: 1 个                            │  │
│  │  - Spectral 扫描问题: 4 个                        │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  Breaking Changes ⚠️                             │  │
│  │  [列出所有 Breaking Changes...]                   │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  Cage Scan 结果 🛡️                              │  │
│  │  [列出所有 Cage Scan 问题...]                    │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  Spectral 扫描结果 📋                            │  │
│  │  [列出所有 Spectral 问题...]                     │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  详细差异                                        │  │
│  │  [列出所有差异...]                               │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  建议和行动计划                                  │  │
│  │  [列出所有建议...]                               │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [下载报告] [重新 Review]                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**功能按钮**:

- **下载报告**: 下载 `diff-report.md` 文件
- **重新 Review**: 重新执行分析流程

***

## 4. 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│  Web UI (Flask)                                       │
│  - 输入 Confluence API Contract 页面 ID                  │
│  - 显示执行进度                                         │
│  - 展示最终报告                                         │
│  - 下载报告                                            │
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
│  - Spectral 模块: 运行 Spectral 扫描                     │
│  - 报告模块: 生成详细报告                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  外部服务                                             │
│  - Confluence API                                     │
│  - GitHub API                                         │
│  - OpenAI API (LLM)                                   │
│  - Cage Scan                                          │
│  - Spectral CLI                                       │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

| 组件             | 技术                      | 说明                  |
| -------------- | ----------------------- | ------------------- |
| Web 框架         | Flask                   | 轻量级 Web 框架          |
| LLM API        | OpenAI API              | 生成 OpenAPI 和报告      |
| Confluence API | atlassian-python-api    | 读取 Confluence 页面    |
| GitHub API     | PyGithub                | 获取 GitHub 文件        |
| Spectral       | @stoplight/spectral-cli | API 规范检查（支持服务化部署） |
| 服务框架         | FastAPI                 | Spectral 服务化部署      |
| 配置管理           | python-dotenv           | 环境变量管理              |

***

## 5. 报告内容

### 5.1 执行摘要

包含以下信息：

- Confluence 独有的端点数量
- GitHub master 独有的端点数量
- 差异总数
- Breaking Changes 数量
- Cage Scan 问题数量
- Spectral 扫描问题数量

### 5.2 Breaking Changes

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

### 5.3 Cage Scan 结果

按严重程度分类：

- **Error**: 必须修复
- **Warning**: 建议修复
- **Info**: 信息提示

每个问题包含：

- 规则代码
- 问题描述
- 严重程度
- 位置（路径）
- 修复建议

### 5.4 Spectral 扫描结果

按严重程度分类：

- **Error**: 必须修复
- **Warning**: 建议修复
- **Info**: 信息提示

每个问题包含：

- 规则代码
- 问题描述
- 严重程度
- 位置（路径）
- 修复建议

### 5.5 详细差异

显示所有 API 差异：

- 端点差异
- 方法差异
- 参数差异
- 响应差异

### 5.6 建议和行动计划

根据分析结果提供建议：

- 需要立即修复的 Breaking Changes
- 建议修复的 Spectral 违规
- 建议改进的文档
- 下一步行动计划

***

## 6. 交互流程

### 6.1 用户操作流程

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
7. 做出决策（批准/拒绝/要求修改）
```

### 6.2 系统执行流程

```
1. 接收用户输入
   ↓
2. 读取 Confluence API Contract 页面
   ↓
3. 从 API Contract 生成 OpenAPI
   ↓
4. 获取 GitHub master 的 OpenAPI
   ↓
5. 对比两个 OpenAPI 文件
   ↓
6. 识别 Breaking Changes
   ↓
7. 运行 Cage Scan
   ↓
8. 运行 Spectral 扫描
   ↓
9. 生成差异报告（包含所有结果）
    ↓
10. 展示报告
    ↓
11. 等待用户操作（下载）
```

***

## 7. 配置说明

### 7.1 环境变量

| 变量名                           | 说明                                         | 示例                          |
| ----------------------------- | ------------------------------------------ | --------------------------- |
| `CONFLUENCE_URL`              | Confluence URL                             | `https://xxx.atlassian.net` |
| `CONFLUENCE_TOKEN`            | Confluence API Token                       | `xxx`                       |
| `CONFLUENCE_STANDARD_PAGE_ID` | Confluence Governance Standard 页面 ID（固定配置） | `987654321`                 |
| `GITHUB_TOKEN`                | GitHub API Token                           | `ghp_xxx`                   |
| `GITHUB_REPO`                 | GitHub 仓库名称                                | `owner/repo`                |
| `OPENAI_API_KEY`              | OpenAI API Key                             | `sk-xxx`                    |

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

***

## 8. 错误处理

### 8.1 常见错误

| 错误类型             | 原因        | 处理方式                 |
| ---------------- | --------- | -------------------- |
| Confluence 页面不存在 | 页面 ID 错误  | 提示用户检查页面 ID          |
| Confluence 权限不足  | Token 无权限 | 提示用户检查 Token 权限      |
| GitHub 仓库不存在     | 仓库名称错误    | 提示用户检查仓库名称           |
| GitHub 权限不足      | Token 无权限 | 提示用户检查 Token 权限      |
| LLM 生成失败         | API 调用失败  | 提示用户检查 API Key       |
| OpenAPI 格式错误     | 生成内容不正确   | 提示用户检查 Confluence 内容 |

### 8.2 错误处理策略

1. **友好提示**: 显示清晰的错误信息
2. **部分成功**: 尽可能生成部分报告
3. **重试机制**: 网络错误自动重试
4. **日志记录**: 记录所有错误信息

***

## 9. 性能优化

### 9.1 执行时间估算

| 步骤                  | 时间          |
| ------------------- | ----------- |
| 读取 Confluence 页面    | 1-2 秒       |
| 生成 OpenAPI          | 10-30 秒     |
| 获取 GitHub OpenAPI   | 1-2 秒       |
| 对比 OpenAPI          | 1-2 秒       |
| 识别 Breaking Changes | 1-2 秒       |
| 运行 Cage Scan        | 5-10 秒      |
| 运行 Spectral 扫描      | 1-2 秒       |
| 生成报告                | 10-30 秒     |
| **总计**              | **30-80 秒** |

### 9.2 优化建议

1. **并行执行**: Cage Scan 和 Spectral 扫描可以并行
2. **缓存**: 缓存 GitHub OpenAPI 文件
3. **增量更新**: 只检查变更的部分
4. **异步处理**: 使用异步 API 调用

***

## 10. 安全考虑

### 10.1 数据安全

- 敏感信息加密存储
- API Token 定期轮换
- 日志脱敏处理

### 10.2 访问控制

- Web UI 访问控制
- API 访问限流
- 用户权限管理

### 10.3 审计日志

- 记录所有操作
- 记录访问日志
- 记录错误日志

***

## 11. 扩展性

### 11.1 支持更多 API 规范

- Swagger 2.0
- GraphQL
- gRPC

### 11.2 支持更多 Governance Standard

- 自定义规则
- 规则库管理
- 规则版本控制

### 11.3 支持更多输出格式

- PDF
- HTML
- JSON

***

## 12. 总结

### 12.1 核心价值

1. **自动化**: 自动化 API Contract Review 流程
2. **准确性**: 准确识别 Breaking Changes 和违规
3. **效率**: 大幅提高 Governance Team 的审核效率
4. **透明**: 清晰的报告和可视化
5. **灵活**: 支持自定义 Governance Standard

### 12.2 使用场景

1. API 变更审核
2. API 合规性检查
3. API 文档管理
4. API 版本控制

### 12.3 下一步

1. 实现 Web UI
2. 实现所有工具
3. 测试和调试
4. 部署和上线

***

## 13. 实现状态

### 13.1 Confluence 内容提取

#### 状态: ✅ 已完成方案设计

**详细实现参考**: [CONFLUENCE-INTEGRATION.md](./CONFLUENCE-INTEGRATION.md)

**核心方案**:

1. **HTML 解析方法**: 使用 BeautifulSoup 解析 HTML 结构
2. **LLM 提取方法**: 使用 GPT-4 解析复杂内容
3. **集成方法**: 结合 HTML 解析和 LLM 理解，交叉验证

**提取内容**:

- API 基本信息（标题、描述、版本）
- 端点信息（HTTP 方法、路径、参数）
- 请求信息（请求头、请求体、示例）
- 响应信息（状态码、响应体、示例）
- 安全信息（认证方式、权限要求）

***

### 13.2 OpenAPI 对比优化

#### 状态: ✅ 已完成方案设计

**详细实现参考**: [OPENAPI-COMPARISON.md](./OPENAPI-COMPARISON.md)

**核心方案**: 使用 Agent + Prompt 进行语义化对比

**关键要点**:

1. **语义理解**：使用 LLM 理解 API 语义，而非简单的文本对比
2. **核心契约对比**：关注 path、method、parameters、request/response body 等核心信息
3. **智能识别 Breaking Changes**：通过精心设计的 Prompt 自动识别 Breaking Changes
4. **忽略非关键差异**：自动忽略 description、example、格式等差异

**实现方式**:

- 使用 GPT-4 作为对比 Agent
- 通过精心设计的 Prompt 指导对比逻辑
- 提供 Few-Shot Learning 示例提高准确性
- 输出标准化的 JSON 格式结果

***

### 13.3 OpenAPI 生成优化

#### 状态: ✅ 已完成方案设计

**详细实现参考**: [OPENAPI-GENERATION.md](./OPENAPI-GENERATION.md)

**核心方案**: 使用 Agent + Prompt 从 Confluence 内容生成 OpenAPI

**关键要点**:

1. **Prompt 工程**：设计高质量的 Prompt 模板
2. **Few-Shot Learning**：提供示例提高生成质量
3. **输出验证**：验证生成的 OpenAPI 规范
4. **错误处理**：处理生成失败的情况

***

### 13.4 Cage Scan 集成

#### 状态: ✅ 已完成方案设计

**详细实现参考**: [CAGE-SCAN-INTEGRATION.md](./CAGE-SCAN-INTEGRATION.md)

**核心方案**: 通过 HTTP API 调用公司提供的 Cage Scan 服务

**集成方式**:

- **方式 1（推荐）**: HTTP API 调用
- **方式 2**: 命令行工具调用
- **方式 3**: Web 界面自动化（不推荐）

***

### 13.5 Spectral 集成

#### 状态: ✅ 已完成方案设计

**详细实现参考**: [SPECTRAL-INTEGRATION.md](./SPECTRAL-INTEGRATION.md)

**核心方案**: 支持多种集成方式，推荐服务化部署

**集成方式**:

- **方式 0（推荐）**: 部署为 HTTP 服务，通过 API 调用
- **方式 1**: 本地命令行调用
- **方式 2**: 使用 Python 库
- **方式 3**: 使用 Docker

**服务化部署优势**:

- 集中管理 Spectral 版本和配置
- 无需在每个客户端安装 Spectral
- 便于监控和日志收集
- 支持并发请求
- 易于扩展和维护

***

## 14. 项目开发计划

### 14.1 技术架构

**核心技术栈**：
- Web 框架: Flask
- LLM API: OpenAI API
- Confluence API: atlassian-python-api
- GitHub API: PyGithub
- Spectral: @stoplight/spectral-cli
- 服务框架: FastAPI (Spectral 服务)
- 配置管理: python-dotenv

**系统架构**：
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Web UI    │────>│  核心服务   │────>│  报告生成   │
└─────────────┘     └─────────────┘     └─────────────┘
         │                 │                 ▲
         │                 ▼                 │
         │         ┌─────────────┐         │
         └────────>│  Spectral  │─────────┘
                   │   服务     │
                   └─────────────┘
```

### 14.2 开发阶段

#### 阶段 1: 基础架构搭建（1 周）
- **任务 1.1**: 搭建开发环境
  - 创建虚拟环境
  - 安装依赖包
  - 配置环境变量

- **任务 1.2**: 实现 Confluence 客户端
  - 集成 atlassian-python-api
  - 实现页面内容读取功能
  - 测试 API 调用

- **任务 1.3**: 部署 Spectral 服务
  - 实现 FastAPI 服务
  - 配置 Docker 部署
  - 测试服务可用性

#### 阶段 2: 核心功能实现（2 周）
- **任务 2.1**: OpenAPI 生成模块
  - 设计 Prompt 模板
  - 实现 OpenAI API 调用
  - 添加输出验证

- **任务 2.2**: OpenAPI 对比模块
  - 实现 GitHub API 集成
  - 设计对比 Prompt
  - 实现差异分析

- **任务 2.3**: Spectral 集成
  - 实现服务调用
  - 处理扫描结果
  - 集成到流程中

#### 阶段 3: Web UI 和报告（2 周）
- **任务 3.1**: Web UI 开发
  - 实现输入页面
  - 设计结果展示
  - 添加实时进度

- **任务 3.2**: 报告生成
  - 设计报告模板
  - 实现数据汇总
  - 添加可视化图表

- **任务 3.3**: 测试和优化
  - 端到端测试
  - 性能优化
  - 错误处理

#### 阶段 4: 部署和集成（1 周）
- **任务 4.1**: 部署到测试环境
  - 配置 CI/CD
  - 自动化测试
  - 监控设置

- **任务 4.2**: Cage Scan 集成（可选）
  - 集成公司 Cage Scan 服务
  - 测试 API 调用
  - 结果处理

- **任务 4.3**: 文档和培训
  - 更新技术文档
  - 编写用户指南
  - 内部培训

### 14.3 关键里程碑

| 里程碑 | 时间 | 完成标准 |
|--------|------|----------|
| 基础架构完成 | 第 1 周末 | Confluence 客户端和 Spectral 服务部署完成 |
| 核心功能完成 | 第 3 周末 | OpenAPI 生成和对比功能测试通过 |
| Web UI 完成 | 第 5 周末 | 完整的 Web 界面和报告功能 |
| 测试环境部署 | 第 6 周末 | 系统在测试环境稳定运行 |
| 生产环境部署 | 第 8 周末 | 系统正式上线 |

### 14.4 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Confluence API 访问限制 | 中 | 实现重试机制和缓存 |
| OpenAI API 成本 | 中 | 设置使用限制和监控 |
| 扫描性能 | 低 | 优化并行处理和异步操作 |
| 公司环境集成 | 中 | 预留集成时间和测试 |

## 15. 文档索引

### 15.1 核心文档

| 文档                                                           | 说明              | 状态    |
| ------------------------------------------------------------ | --------------- | ----- |
| [API-CONTRACT-REVIEW-FLOW.md](./API-CONTRACT-REVIEW-FLOW.md) | 核心流程文档（本文档）     | ✅ 已更新 |
| [CONFLUENCE-INTEGRATION.md](./CONFLUENCE-INTEGRATION.md)     | Confluence 集成方案 | ✅ 已完成 |
| [OPENAPI-GENERATION.md](./OPENAPI-GENERATION.md)             | OpenAPI 生成方案    | ✅ 已完成 |
| [OPENAPI-COMPARISON.md](./OPENAPI-COMPARISON.md)             | OpenAPI 对比方案    | ✅ 已完成 |
| [CAGE-SCAN-INTEGRATION.md](./CAGE-SCAN-INTEGRATION.md)       | Cage Scan 集成方案  | ✅ 已完成 |
| [SPECTRAL-INTEGRATION.md](./SPECTRAL-INTEGRATION.md)         | Spectral 集成方案   | ✅ 已完成 |

### 15.2 实现优先级

1. **高优先级**
   - Confluence 集成
   - OpenAPI 生成
   - OpenAPI 对比
   - Spectral 集成（优先）
2. **中优先级**
   - Web UI 开发
   - 报告模板定制
3. **低优先级**
   - Cage Scan 集成（后续）
   - 监控和日志

### 15.3 下一步行动

1. **立即开始**
   - 搭建开发环境
   - 实现 Confluence 客户端
   - 实现 OpenAPI 生成模块（使用 OpenAI API + Prompt）
   - 部署 Spectral 服务
2. **短期目标（1-2 周）**
   - 完成 Confluence 集成
   - 完成 OpenAPI 生成和对比
   - 集成 Spectral 扫描
   - 开发基础 Web UI
3. **中期目标（3-4 周）**
   - 完善 Web UI
   - 优化报告模板
   - 测试和性能优化
4. **长期目标（1-2 月）**
   - 集成 Cage Scan（公司环境）
   - 部署到生产环境
   - 监控和日志系统
   - 用户培训

