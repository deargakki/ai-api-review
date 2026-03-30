api-review-agent/
├── .github/
│   └── workflows/
│       └── api-review.yml          # GitHub Action配置文件
├── src/
│   ├── __init__.py
│   ├── main.py                     # 主入口
│   ├── config.py                   # 配置管理
│   ├── github/
│   │   ├── __init__.py
│   │   └── client.py               # GitHub API封装
│   ├── diff/
│   │   ├── __init__.py
│   │   └── engine.py               # Diff引擎
│   ├── spectral/
│   │   ├── __init__.py
│   │   └── runner.py               # Spectral扫描
│   ├── confluence/
│   │   ├── __init__.py
│   │   └── reader.py               # Confluence规范读取
│   └── report/
│       ├── __init__.py
│       ├── generator.py           # 报告生成器
│       └── templates/
│           └── review.md.jinja2    # 报告模板
├── tests/
│   ├── __init__.py
│   ├── test_diff.py
│   ├── test_spectral.py
│   └── test_report.py
├── .spectral.yml                   # Spectral规则配置
├── requirements.txt                # Python依赖
├── setup.py                        # 安装配置
├── README.md
└── .gitignore
