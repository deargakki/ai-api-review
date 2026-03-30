# API Review Agent (LangChain)

基于 LangChain 的 API Review Agent，自动审查 OpenAPI 规范变更。

## 功能

- 自动读取 Confluence 中的 API Review 规范
- 智能生成 Spectral 规则配置
- 对比新旧 OpenAPI 文件，识别 Breaking Changes
- 运行 Spectral 扫描，检查合规性
- 生成详细的 Markdown 格式报告
- 自动发布到 GitHub PR 评论

## 架构

```
GitHub Action 负责生成 OpenAPI 文件
         ↓
    main-openapi.yaml
    pr-openapi.yaml
         ↓
LangChain Agent 负责分析
    ├── ConfluenceTool (读取规范)
    ├── SpectralRulesGeneratorTool (生成规则)
    ├── DiffTool (对比变更)
    └── SpectralScanTool (合规检查)
         ↓
    生成 Review 报告
         ↓
    发布到 PR 评论
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
npm install -g @stoplight/spectral-cli
```

### 2. 配置环境变量

```bash
export OPENAI_API_KEY="your-openai-api-key"
export CONFLUENCE_URL="https://your-domain.atlassian.net"
export CONFLUENCE_TOKEN="your-confluence-token"
export CONFLUENCE_PAGE_ID="123456789"
export GITHUB_TOKEN="your-github-token"
export GITHUB_REPOSITORY="owner/repo"
export PR_NUMBER="123"
export MAIN_OPENAPI_PATH="main-openapi.yaml"
export PR_OPENAPI_PATH="pr-openapi.yaml"
```

### 3. 运行

```bash
python src/main.py
```

## GitHub Actions 配置

### Secrets 配置

在 GitHub 仓库的 Settings → Secrets and variables → Actions 中添加：

| Secret 名称 | 说明 |
|------------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 |
| `CONFLUENCE_URL` | Confluence URL |
| `CONFLUENCE_TOKEN` | Confluence API Token |
| `CONFLUENCE_PAGE_ID` | API 规范页面 ID |
| `GITHUB_TOKEN` | GitHub Token（自动提供） |

### 触发条件

- PR 修改了 `src/**/*.java` 文件
- PR 修改了 `src/**/*.py` 文件
- PR 修改了 `**/openapi.yaml` 文件

## 项目结构

```
api-review-agent/
├── .github/
│   └── workflows/
│       └── api-review.yml      # GitHub Action 配置
├── src/
│   ├── __init__.py
│   ├── main.py                 # 主入口
│   ├── config.py               # 配置管理
│   ├── tools/
│   │   ├── __init__.py
│   │   └── api_tools.py        # LangChain Tools
│   └── agents/
│       ├── __init__.py
│       └── api_review_agent.py # Agent 定义
├── requirements.txt
├── setup.py
└── README.md
```

## 自定义

### 添加新工具

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class MyCustomInput(BaseModel):
    param: str = Field(description="参数说明")

class MyCustomTool(BaseTool):
    name = "my_custom_tool"
    description = "工具说明"
    args_schema = MyCustomInput
    
    def _run(self, param: str) -> str:
        # 实现逻辑
        return "结果"
```

### 修改 Agent 提示词

编辑 `src/agents/api_review_agent.py` 中的 `prompt` 变量。

## 输出示例

```markdown
## 📊 API Review 报告

### 变更摘要
- Breaking Changes: 1 个
- Non-Breaking Changes: 3 个
- Spectral Issues: 2 个

### 详细变更
- ❌ 端点 `/users/{id}` 被删除
- ✅ 新增端点 `/orders`
- 🔄 修改端点 `/users`

### 合规性检查
- [error] 缺少 description
- [warning] 路径不符合 kebab-case

### 建议
1. 恢复被删除的端点或提供迁移方案
2. 为所有端点添加 description
3. 使用 kebab-case 命名路径
```

## 许可证

MIT
