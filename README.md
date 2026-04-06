# API Contract Review 系统

## 项目概述

API Contract Review 系统是一个自动化工具，用于审查 API 变更，包括：
- 从 Confluence 读取 API Contract 页面
- 生成 OpenAPI 规范
- 与 GitHub 上的现有规范对比
- 识别 Breaking Changes
- 运行 Spectral 扫描
- 生成详细报告

## 技术栈

- Web 框架: Flask
- LLM API: OpenAI API
- Confluence API: atlassian-python-api
- GitHub API: PyGithub
- Spectral: @stoplight/spectral-cli
- 服务框架: FastAPI (Spectral 服务)
- 配置管理: python-dotenv

## 项目结构

```
api-review/
├── api-contract-review/       # 主项目
│   ├── src/
│   │   ├── config/           # 配置文件
│   │   ├── services/         # 核心服务
│   │   ├── web/              # Web UI
│   │   └── utils/            # 工具函数
│   ├── requirements.txt      # 依赖
│   └── .env                  # 环境变量
├── spectral-service/          # Spectral 服务
│   ├── app.py                # FastAPI 应用
│   ├── Dockerfile            # Docker 配置
│   └── requirements.txt      # 依赖
├── requirements.txt          # 主项目依赖
├── .env.example              # 环境变量示例
└── README.md                 # 项目说明
```

## 快速开始

### 1. 搭建开发环境

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
copy .env.example .env
# 编辑 .env 文件，填写相关配置
```

### 2. 部署 Spectral 服务

```bash
# 进入 spectral-service 目录
cd spectral-service

# 构建 Docker 镜像
docker build -t spectral-service .

# 运行容器
docker run -d -p 8000:8000 --name spectral-service spectral-service

# 测试服务
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"openapi_content": "openapi: 3.0.0\ninfo:\n  title: Test API\n  version: 1.0.0\npaths:\n  /test:\n    get:\n      responses:\n        \"200\":\n          description: OK"}'
```

### 3. 运行主服务

```bash
# 进入 api-contract-review 目录
cd api-contract-review

# 运行 Flask 应用
python src/web/app.py

# 访问 http://localhost:5000
```

## 开发阶段

1. **阶段 1: 基础架构搭建** (1 周)
   - 搭建开发环境
   - 实现 Confluence 客户端
   - 部署 Spectral 服务

2. **阶段 2: 核心功能实现** (2 周)
   - OpenAPI 生成模块
   - OpenAPI 对比模块
   - Spectral 集成

3. **阶段 3: Web UI 和报告** (2 周)
   - Web UI 开发
   - 报告生成
   - 测试和优化

4. **阶段 4: 部署和集成** (1 周)
   - 部署到测试环境
   - Cage Scan 集成（可选）
   - 文档和培训

## 配置说明

### 环境变量

- `CONFLUENCE_URL`: Confluence 实例 URL
- `CONFLUENCE_USERNAME`: Confluence 用户名
- `CONFLUENCE_API_TOKEN`: Confluence API 令牌
- `OPENAI_API_KEY`: OpenAI API 密钥
- `GITHUB_TOKEN`: GitHub 令牌
- `SPECTRAL_SERVICE_URL`: Spectral 服务 URL
- `CAGE_SCAN_URL`: Cage Scan 服务 URL（可选）
- `CAGE_SCAN_API_KEY`: Cage Scan API 密钥（可选）

## 技术文档

- [API-CONTRACT-REVIEW-FLOW.md](./docs/API-CONTRACT-REVIEW-FLOW.md): 核心流程文档
- [API-CONTRACT-REVIEW-IMPLEMENTATION-PLAN.md](./docs/API-CONTRACT-REVIEW-IMPLEMENTATION-PLAN.md): 技术实现路径
- [CONFLUENCE-INTEGRATION.md](./docs/CONFLUENCE-INTEGRATION.md): Confluence 集成方案
- [OPENAPI-GENERATION.md](./docs/OPENAPI-GENERATION.md): OpenAPI 生成方案
- [OPENAPI-COMPARISON.md](./docs/OPENAPI-COMPARISON.md): OpenAPI 对比方案
- [SPECTRAL-INTEGRATION.md](./docs/SPECTRAL-INTEGRATION.md): Spectral 集成方案
- [CAGE-SCAN-INTEGRATION.md](./docs/CAGE-SCAN-INTEGRATION.md): Cage Scan 集成方案
