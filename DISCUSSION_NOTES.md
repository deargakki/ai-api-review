# API Review Agent - 讨论记录

> **创建日期**: 2026-03-20  
> **最后更新**: 2026-03-20  
> **文档版本**: v1.0

---

## 目录

1. [项目概述](#1-项目概述)
2. [技术选型](#2-技术选型)
3. [核心组件详解](#3-核心组件详解)
4. [架构设计](#4-架构设计)
5. [Breaking Change](#5-breaking-change)
6. [自定义规则](#6-自定义规则)
7. [实施计划](#7-实施计划)

---

## 1. 项目概述

### 1.1 项目目标

开发一个自动化 API Review Agent，用于：
- 监控 API 规范（OpenAPI.yaml）的变更
- 结合 Confluence 中的 API Review 规范进行合规性检查
- 使用 Spectral 进行自定义规则扫描
- 生成结构化的 API 变更报告

### 1.2 核心价值

- **自动化**: 减少 API Review 的工作量
- **标准化**: 确保 API 规范符合团队标准
- **可追溯**: 记录 API 的演进历史和变更影响
- **质量保障**: 提前发现 Breaking Changes 和潜在问题

### 1.3 确认的技术环境

- ✅ **Git 平台**: GitHub
- ✅ **运行环境**: GitHub Action
- ✅ **触发方式**: PR 时自动触发
- ✅ **报告输出**: PR 评论

---

## 2. 技术选型

### 2.1 核心技术栈

| 组件 | 技术 | 版本 | 选择理由 |
|------|------|------|---------|
| **开发语言** | Python | 3.9+ | 丰富的库支持，易于维护 |
| **GitHub API** | PyGithub | 2.1.0+ | 官方 Python 客户端，功能完整 |
| **OpenAPI Diff** | openapi-diff | 0.2.0+ | 专门用于 OpenAPI 变更检测 |
| **规则引擎** | Spectral | 6.0+ | 强大的 API 规范检查工具 |
| **LLM** | OpenAI GPT-4 | - | 最先进的自然语言处理能力 |
| **Confluence API** | atlassian-python-api | 3.40.0+ | 官方 Python 客户端 |
| **报告生成** | Jinja2 | 3.1.0+ | 灵活的模板引擎 |

### 2.2 技术决策讨论

#### Q: 为什么选择 Python？
**A**: 
- 丰富的库支持（PyGithub、openapi-diff、Jinja2 等）
- 易于维护和扩展
- 团队熟悉度高

#### Q: 为什么需要 LLM？
**A**: 
- Confluence 中的规范通常是自然语言描述
- 纯规则方案无法理解自然语言
- LLM 可以将自然语言规范转换为可执行的 Spectral 规则

#### Q: LLM 增强方案 vs 纯规则方案？
**A**: 
- **纯规则方案**: 快速、低成本，但需要手动维护规则
- **LLM 增强方案**: 智能化、自动化，但有一定成本
- **推荐**: 混合方案 - 规则优先 + LLM 增强

---

## 3. 核心组件详解

### 3.1 openapi-diff

#### 是什么？
- **本质**: 本地软件工具（命令行工具 + 编程库）
- **不是**: 在线 API 服务（不需要网络调用）

#### 核心功能
- 对比两个 OpenAPI 规范文件
- 识别所有变更（新增、删除、修改）
- 自动识别 Breaking Changes

#### 检测的变更类型

| 变更类型 | 示例 | 是否 Breaking |
|---------|------|-------------|
| **端点变更** | 新增/删除端点 | 删除 = Breaking |
| **方法变更** | 新增/删除方法 | 删除 = Breaking |
| **参数变更** | 新增/删除/修改参数 | 删除/改必填/改类型 = Breaking |
| **响应变更** | 新增/删除响应码 | 删除 = Breaking |
| **Schema 变更** | 新增/删除/修改字段 | 删除/改必填/改类型 = Breaking |

#### 使用示例

```python
import openapi_diff

# 加载两个规范
old_spec = openapi_diff.load_spec("old.yaml")
new_spec = openapi_diff.load_spec("new.yaml")

# 执行对比
diff = openapi_diff.compare(old_spec, new_spec)

# 输出结果
print(f"Breaking changes: {len(diff.breaking_changes)}")
print(f"Non-breaking changes: {len(diff.non_breaking_changes)}")
```

---

### 3.2 Spectral

#### 是什么？
- 开源的 API 规范 Lint 工具
- 专门用于检查 OpenAPI、JSON Schema 等规范的合规性
- 支持高度可定制的规则配置

#### 核心功能
- 规则检查（命名规范、必填字段、数据类型等）
- 内置规则集（OpenAPI 官方规则集）
- 自定义规则支持

#### 输出格式

```json
[
  {
    "code": "operation-description",
    "message": "Operation must have \"description\"",
    "severity": "error",
    "path": ["paths", "/users", "get"],
    "range": {
      "start": {"line": 10, "character": 5},
      "end": {"line": 15, "character": 3}
    },
    "source": "openapi.yaml"
  }
]
```

#### 规则语法

```yaml
规则名称:
  description: 规则描述
  severity: error | warning | info | hint
  given: JSONPath表达式（定位要检查的位置）
  then:
    field: 要检查的字段
    function: 检查函数
    functionOptions: 函数选项
```

#### 常用检查函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `truthy` | 值必须存在且非空 | 检查 description 是否存在 |
| `falsy` | 值必须不存在或为空 | 检查 deprecated 是否为 false |
| `pattern` | 匹配正则表达式 | 检查命名格式 |
| `enum` | 值必须在枚举中 | 检查 HTTP 方法 |
| `schema` | 验证 JSON Schema | 检查字段类型 |

---

### 3.3 LLM 模块

#### 作用
- 理解 Confluence 中的自然语言规范
- 生成 Spectral 规则配置
- 智能分析业务规则

#### 工作流程

```
Confluence 规范（自然语言）
        ↓
    LLM 理解
        ↓
生成 Spectral 规则
        ↓
    .spectral.yml
        ↓
  Spectral 扫描
```

#### 实现示例

```python
import openai

class LLMGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        openai.api_key = api_key
        self.model = model
    
    def generate_spectral_rules(self, confluence_content: str) -> str:
        prompt = f"""
你是一位API规范专家。请根据以下Confluence中的API Review规范，生成对应的Spectral规则配置：

{confluence_content}

规则要求：
1. 所有规则必须有清晰的描述
2. 规则级别（severity）根据重要性设置为error、warning或info
3. 使用正确的JSONPath表达式
4. 覆盖所有提到的规范要求
5. 保持规则格式的一致性
6. 生成完整的YAML配置，包括extends部分

请只输出YAML内容，不要包含其他说明。
        """
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
```

---

### 3.4 Confluence 读取

#### 作用
- 从 Confluence 获取 API Review 规范文档
- 支持自然语言和结构化规范

#### 实现示例

```python
from atlassian import Confluence

class ConfluenceReader:
    def __init__(self, url: str, token: str):
        self.confluence = Confluence(url=url, token=token)
    
    def get_api_specs(self, page_id: str) -> str:
        page = self.confluence.get_page_by_id(page_id, expand="body.storage")
        return page["body"]["storage"]["value"]
```

---

## 4. 架构设计

### 4.1 完整流程

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Review Agent                        │
├─────────────────────────────────────────────────────────────────┤
│  1. Confluence 读取 → 2. LLM 规则生成 → 3. OpenAPI Diff → 4. Spectral → 5. 报告  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  步骤1: 读取 Confluence 规范                                     │
│  步骤2: LLM 生成 Spectral 规则                                  │
│  步骤3: 对比 OpenAPI 变更（Diff 引擎）                           │
│  步骤4: 运行 Spectral 扫描                                      │
│  步骤5: 生成 Review 报告并发布到 PR                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 详细流程

#### 步骤 1: 读取 Confluence 规范
- 从 Confluence 获取 API Review 规范文档
- 支持自然语言和结构化规范

#### 步骤 2: LLM 生成 Spectral 规则
- LLM 理解 Confluence 中的自然语言规范
- 生成对应的 Spectral 规则配置
- 保存为 `.spectral.generated.yml`

#### 步骤 3: OpenAPI Diff
- 获取 PR 分支和主分支的 OpenAPI 规范
- 对比两个版本，识别所有变更
- 分类为 Breaking Changes 和 Non-Breaking Changes

#### 步骤 4: Spectral 扫描
- 使用生成的规则扫描 OpenAPI 规范
- 检查规范合规性
- 输出规则违规列表

#### 步骤 5: 生成报告
- 整合 Diff 结果和 Spectral 扫描结果
- 生成 Markdown 格式的 Review 报告
- 发布到 PR 评论

### 4.3 项目结构

```
api-review-agent/
├── .github/
│   └── workflows/
│       └── api-review.yml          # GitHub Action 配置
├── src/
│   ├── __init__.py
│   ├── main.py                     # 主入口
│   ├── config.py                   # 配置管理
│   ├── confluence/
│   │   ├── __init__.py
│   │   └── reader.py               # Confluence 读取
│   ├── llm/
│   │   ├── __init__.py
│   │   └── generator.py            # LLM 规则生成
│   ├── github/
│   │   ├── __init__.py
│   │   └── client.py               # GitHub API
│   ├── diff/
│   │   ├── __init__.py
│   │   └── engine.py               # OpenAPI Diff
│   ├── spectral/
│   │   ├── __init__.py
│   │   └── runner.py               # Spectral 扫描
│   └── report/
│       ├── __init__.py
│       ├── generator.py           # 报告生成
│       └── templates/
│           └── review.md.jinja2    # 报告模板
├── requirements.txt
├── setup.py
└── README.md
```

---

## 5. Breaking Change

### 5.1 定义

**Breaking Change**（破坏性变更）是指那些会导致现有客户端不兼容的 API 变更。

**简单来说**：如果这个变更上线后，已经使用你 API 的客户端会报错或无法正常工作，那就是 Breaking Change。

### 5.2 标准定义

Breaking Change 的定义基于 **OpenAPI 社区的标准定义**，不是自定义的。

openapi-diff 库内置了完整的 Breaking Change 检测规则，这些规则基于 OpenAPI 社区的最佳实践。

### 5.3 常见的 Breaking Change 类型

| 变更类型 | 示例 | 为什么是 Breaking |
|---------|------|-----------------|
| **删除端点** | 删除 `/users` | 客户端调用会 404 |
| **删除方法** | 删除 `DELETE /users` | 客户端调用会 405 |
| **删除参数** | 删除 `page` 参数 | 客户端传参会被忽略或报错 |
| **删除字段** | 删除 `User.email` | 客户端读取会出错 |
| **字段类型变更** | `age` 从 `integer` 改为 `string` | 客户端解析会出错 |
| **参数改为必填** | `page` 从可选改为必填 | 客户端不传参会报错 |
| **字段改为必填** | `email` 从可选改为必填 | 客户端不传会报错 |
| **删除响应码** | 删除 `200` 响应 | 客户端无法处理成功响应 |
| **枚举值变更** | 删除枚举中的一个值 | 客户端使用该值会出错 |

### 5.4 Non-Breaking Change

| 变更类型 | 示例 | 为什么不是 Breaking |
|---------|------|-------------------|
| **新增端点** | 新增 `/orders` | 客户端不知道也不影响 |
| **新增方法** | 新增 `DELETE /users` | 客户端不知道也不影响 |
| **新增参数** | 新增 `limit` 参数 | 客户端不传也不影响 |
| **新增字段** | 新增 `User.phone` | 客户端不知道也不影响 |
| **新增响应码** | 新增 `401` 响应 | 客户端不知道也不影响 |
| **字段改为可选** | `email` 从必填改为可选 | 客户端传了也不影响 |
| **参数改为可选** | `page` 从必填改为可选 | 客户端传了也不影响 |

### 5.5 Diff 引擎 vs Spectral

| 维度 | Diff 引擎 | Spectral |
|------|-----------|----------|
| **输入** | 两个 OpenAPI 文件 | 一个 OpenAPI 文件 |
| **目的** | 对比变更 | 检查合规性 |
| **输出** | 变更列表 | 规则违规列表 |
| **检查内容** | 新增、删除、修改 | 命名、格式、完整性 |
| **Breaking Change** | ✅ 专门识别 | ❌ 不识别 |

---

## 6. 自定义规则

### 6.1 可以自定义 Breaking Change 吗？

**完全可以！** 你有完全的控制权，可以根据团队需求自定义 Breaking Change 的定义。

### 6.2 自定义方式

#### 方式 1: 扩展 openapi-diff（推荐）

在 openapi-diff 的基础上添加自定义规则：

```python
import openapi_diff

class CustomDiffEngine:
    def __init__(self):
        self.base_engine = openapi_diff
    
    def compare(self, old_spec: dict, new_spec: dict) -> dict:
        # 先使用内置规则
        diff = self.base_engine.compare(old_spec, new_spec)
        
        # 添加自定义 Breaking Change 规则
        custom_breaking = self._check_custom_breaking_rules(old_spec, new_spec)
        diff.breaking_changes.extend(custom_breaking)
        
        return diff
    
    def _check_custom_breaking_rules(self, old_spec: dict, new_spec: dict) -> list:
        """自定义 Breaking Change 规则"""
        breaking_changes = []
        
        # 规则 1: 检查是否删除了认证
        if self._auth_removed(old_spec, new_spec):
            breaking_changes.append({
                "code": "auth-removed",
                "message": "Authentication was removed from API",
                "path": ["security"],
                "severity": "critical"
            })
        
        # 规则 2: 检查是否将 HTTPS 改为 HTTP
        if self._https_downgraded(old_spec, new_spec):
            breaking_changes.append({
                "code": "https-downgraded",
                "message": "HTTPS was downgraded to HTTP",
                "path": ["servers"],
                "severity": "critical"
            })
        
        return breaking_changes
```

#### 方式 2: 完全自定义 Diff 引擎

如果你想要完全控制 Breaking Change 的定义，可以自己实现：

```python
class CustomDiffEngine:
    def __init__(self):
        # 自定义 Breaking Change 规则
        self.breaking_change_rules = [
            self._check_endpoint_removed,
            self._check_method_removed,
            self._check_parameter_removed,
            self._check_auth_removed,
            self._check_https_downgraded,
            # 添加更多自定义规则...
        ]
    
    def compare(self, old_spec: dict, new_spec: dict) -> dict:
        """对比两个 OpenAPI 规范"""
        breaking_changes = []
        
        # 执行所有 Breaking Change 规则
        for rule in self.breaking_change_rules:
            result = rule(old_spec, new_spec)
            if result:
                breaking_changes.extend(result)
        
        return {
            "breaking_changes": breaking_changes,
            "non_breaking_changes": non_breaking_changes
        }
```

#### 方式 3: 配置文件定义

将自定义规则放在配置文件中，更灵活：

```yaml
# custom-breaking-rules.yml
breaking_changes:
  - code: auth-removed
    description: Authentication was removed
    severity: critical
    enabled: true
  
  - code: https-downgraded
    description: HTTPS was downgraded to HTTP
    severity: critical
    enabled: true
  
  - code: required-header-removed
    description: Required response header was removed
    severity: error
    enabled: false  # 可以禁用某些规则
```

### 6.3 常见的自定义 Breaking Change 场景

| 场景 | 自定义规则示例 |
|------|--------------|
| **安全要求** | 删除认证、HTTPS 降级 |
| **业务规则** | 删除必需字段、改变错误码语义 |
| **性能要求** | 删除分页参数、改变响应格式 |
| **合规要求** | 删除审计日志字段、改变数据格式 |

---

## 7. 实施计划

### 7.1 开发阶段

#### Phase 1: 项目初始化（30分钟）
- [ ] 创建项目目录结构
- [ ] 配置 Python 环境
- [ ] 编写基础配置文件

#### Phase 2: 核心功能实现（2-3小时）
- [ ] GitHub API 集成
- [ ] OpenAPI Diff 实现
- [ ] Spectral 规则扫描
- [ ] 报告生成

#### Phase 3: LLM 增强（1-2小时）
- [ ] Confluence 规范读取
- [ ] LLM 规则生成
- [ ] 规则验证和优化

#### Phase 4: GitHub Action 集成（1小时）
- [ ] 编写 Action 配置
- [ ] 测试和调试
- [ ] 部署和发布

### 7.2 环境变量配置

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `GITHUB_TOKEN` | GitHub API 令牌 | `ghp_123...` |
| `GITHUB_REPOSITORY` | GitHub 仓库 | `owner/repo` |
| `PR_NUMBER` | PR 编号 | `123` |
| `OPENAPI_PATH` | OpenAPI 文件路径 | `openapi.yaml` |
| `BASE_BRANCH` | 基础分支 | `main` |
| `CONFLUENCE_URL` | Confluence URL | `https://your-domain.atlassian.net` |
| `CONFLUENCE_TOKEN` | Confluence API 令牌 | `atlassian-token-123` |
| `CONFLUENCE_PAGE_ID` | 规范文档页面 ID | `123456789` |
| `LLM_API_KEY` | LLM API 密钥 | `sk-123...` |
| `LLM_MODEL` | LLM 模型 | `gpt-4` |

### 7.3 后续优化方向

1. **缓存机制**: 缓存 Confluence 内容和生成的规则
2. **并行处理**: 并行处理多个 API 规范
3. **智能提示**: 基于 LLM 生成更详细的修复建议
4. **历史分析**: 分析 API 演进历史，识别趋势
5. **可视化**: 提供更直观的报告界面

---

## 8. 总结

### 8.1 关键决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| **技术栈** | Python | 丰富的库支持，易于维护 |
| **Diff 引擎** | openapi-diff | 专门的 OpenAPI 变更检测工具 |
| **规则引擎** | Spectral | 强大的 API 规范检查工具 |
| **LLM 集成** | 是 | 支持自然语言规范，提高自动化程度 |
| **部署方式** | GitHub Action | 与 GitHub 深度集成，易于使用 |

### 8.2 核心优势

- ✅ **完全自动化**: PR 创建时自动触发，无需人工干预
- ✅ **智能分析**: LLM 理解自然语言规范，智能识别 Breaking Changes
- ✅ **高度可定制**: 可以根据团队需求自定义规则
- ✅ **易于集成**: 作为 GitHub Action，无需额外服务器
- ✅ **提升质量**: 确保 API 设计符合团队标准，提前发现问题

### 8.3 下一步行动

1. ✅ 确认技术选型和架构设计
2. ⏳ 创建项目目录结构
3. ⏳ 实现核心功能模块
4. ⏳ 编写 GitHub Action 配置
5. ⏳ 本地测试和调试
6. ⏳ 提交到 GitHub 仓库
7. ⏳ 创建测试 PR 验证功能

---

## 9. 附录

### 9.1 参考资料

- [OpenAPI Specification](https://swagger.io/specification/)
- [Spectral Documentation](https://meta.stoplight.io/docs/spectral/)
- [openapi-diff Documentation](https://github.com/backstage/openapi-diff)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Confluence REST API](https://developer.atlassian.com/cloud/confluence/rest/)

### 9.2 术语表

| 术语 | 解释 |
|------|------|
| **OpenAPI** | API 规范标准，前身为 Swagger |
| **Spectral** | 开源的 OpenAPI/Lint 工具 |
| **Breaking Change** | 破坏性变更，可能导致客户端不兼容的修改 |
| **Diff** | 差异对比 |
| **LLM** | 大语言模型（Large Language Model） |
| **PR** | Pull Request |
| **CI/CD** | 持续集成/持续部署 |

### 9.3 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0 | 2026-03-20 | 初始版本，记录所有讨论内容 |

---

> **文档说明**: 本文档记录了 API Review Agent 项目的所有讨论内容，包括技术选型、架构设计、核心组件详解、实施计划等。随着项目进展，本文档将持续更新。
