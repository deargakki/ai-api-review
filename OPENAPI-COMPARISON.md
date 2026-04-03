# OpenAPI 文件对比方案

## 1. 问题分析

### 1.1 核心挑战

直接对比两个 OpenAPI YAML 文件会面临以下问题：

1. **格式差异**：
   - 键值对顺序不同（YAML 解析后语义相同）
   - 缩进和换行差异
   - 注释差异
   - 引用（$ref）展开方式不同

2. **生成方式差异**：
   - GitHub 的 OpenAPI 是人工维护 + Swagger 生成
   - Confluence 生成的 OpenAPI 是 LLM 生成
   - 两者在描述风格、字段顺序、结构组织上必然存在差异

3. **无关差异干扰**：
   - 描述文本的细微差别
   - 示例数据的差异
   - 字段顺序的不同

### 1.2 正确的对比思路

**不应该**：
- ❌ 逐行文本对比
- ❌ 简单的 YAML 结构对比
- ❌ 关注描述性文字的差异

**应该**：
- ✅ 基于 API 语义进行对比
- ✅ 关注特定 API path 的改动
- ✅ 识别 Breaking Changes
- ✅ 对比 API 契约（接口签名）而非实现细节

## 2. 使用 Agent 进行 OpenAPI 对比

### 2.1 Agent 方案的优势

使用 Agent（通过 Prompt 指导 LLM）来执行 OpenAPI 对比任务具有以下优势：

1. **语义理解**：LLM 能够理解 API 的语义，而不仅仅是结构对比
2. **灵活性**：通过调整 Prompt 可以轻松改变对比策略
3. **上下文感知**：LLM 能够理解 API 的业务含义和上下文
4. **无需复杂代码**：不需要编写复杂的解析和对比逻辑
5. **适应性强**：能够处理各种格式的 OpenAPI 规范

### 2.2 Agent Prompt 设计

#### 2.2.1 Prompt 结构

一个有效的 OpenAPI 对比 Prompt 应该包含以下部分：

```
1. 角色定义（Role Definition）
   - 定义 Agent 的身份和专业领域

2. 任务描述（Task Description）
   - 清晰说明要完成的任务

3. 输入格式说明（Input Format）
   - 说明输入数据的格式和结构

4. 对比规则（Comparison Rules）
   - 定义如何对比，关注什么
   - Breaking Changes 的识别标准

5. 输出格式（Output Format）
   - 明确期望的输出格式
   - 提供输出模板

6. 示例（Examples）
   - 提供 Few-Shot Learning 示例
   - 展示期望的输入输出对

7. 约束条件（Constraints）
   - 说明必须遵守的规则
   - 列出要忽略的字段
```

#### 2.2.2 完整 Prompt 示例

```markdown
你是一个专业的 API 规范专家，擅长对比和分析 OpenAPI 规范文件。

## 任务

对比两个 OpenAPI 3.0 规范文件，识别它们之间的差异，特别关注 Breaking Changes。

## 输入

1. **Generated OpenAPI**：从 Confluence API Contract 页面生成的 OpenAPI 规范
2. **Master OpenAPI**：GitHub master 分支的 OpenAPI 规范
3. **Target Path**（可选）：只对比特定的 API path

## 对比规则

### 重点关注

1. **路径变更**：
   - 新增的路径
   - 删除的路径
   - 路径重命名或变更

2. **方法变更**：
   - 新增的 HTTP 方法
   - 删除的 HTTP 方法
   - 方法级别的参数变更

3. **参数变更**：
   - 新增必填参数（Breaking Change）
   - 新增可选参数（非 Breaking Change）
   - 删除参数（Breaking Change）
   - 参数类型变更（Breaking Change）
   - 参数位置变更（query → path 等）

4. **请求体变更**：
   - 请求体结构变更
   - 必填字段变更
   - 字段类型变更

5. **响应变更**：
   - 删除响应状态码（Breaking Change）
   - 响应结构变更
   - 字段类型变更

### Breaking Changes 识别标准

以下情况被视为 Breaking Changes：
- 删除 API 路径或方法
- 新增必填参数
- 删除参数
- 修改参数类型
- 删除响应状态码
- 修改响应结构（删除字段、修改字段类型）
- 路径重命名

### 忽略的字段

以下字段的变更不应被视为 Breaking Changes：
- `description`：描述文本
- `summary`：摘要
- `example`：示例数据
- `examples`：示例集合
- `title`：标题
- `externalDocs`：外部文档

## 输出格式

请以 JSON 格式输出对比结果，包含以下结构：

```json
{
  "success": true,
  "target_path": "/users",
  "path_changes": [
    {
      "type": "path_renamed",
      "old_path": "/users/{id}",
      "new_path": "/customers/{userId}",
      "similarity": 0.8,
      "breaking": true,
      "description": "路径重命名且路径参数名称变更"
    }
  ],
  "comparison": [
    {
      "generated_path": "/users/{id}",
      "master_path": "/users/{id}",
      "differences": [
        {
          "type": "method_added",
          "method": "POST",
          "breaking": false,
          "description": "新增 POST 方法"
        },
        {
          "type": "method_modified",
          "method": "GET",
          "changes": [
            {
              "category": "parameters",
              "changes": [
                {
                  "type": "required_parameter_added",
                  "parameter": "include_deleted",
                  "breaking": true,
                  "description": "新增必填参数 include_deleted"
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "breaking_changes": [
    {
      "path": "/users/{id}",
      "type": "required_parameter_added",
      "method": "GET",
      "severity": "high",
      "description": "新增必填参数 include_deleted，可能导致现有调用失败"
    }
  ],
  "summary": {
    "total_changes": 2,
    "breaking_changes_count": 1,
    "path_changes_count": 0,
    "recommendation": "检测到 Breaking Changes，需要审查和评估影响"
  }
}
```

## 示例

### 示例 1：新增可选参数

**Generated OpenAPI:**
```yaml
paths:
  /users:
    get:
      parameters:
        - name: limit
          in: query
          required: false
          schema:
            type: integer
```

**Master OpenAPI:**
```yaml
paths:
  /users:
    get:
      parameters: []
```

**输出:**
```json
{
  "comparison": [
    {
      "generated_path": "/users",
      "master_path": "/users",
      "differences": [
        {
          "type": "method_modified",
          "method": "GET",
          "changes": [
            {
              "category": "parameters",
              "changes": [
                {
                  "type": "optional_parameter_added",
                  "parameter": "limit",
                  "breaking": false,
                  "description": "新增可选参数 limit"
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "breaking_changes": [],
  "summary": {
    "total_changes": 1,
    "breaking_changes_count": 0,
    "recommendation": "无 Breaking Changes，可以安全部署"
  }
}
```

### 示例 2：新增必填参数

**Generated OpenAPI:**
```yaml
paths:
  /users/{id}:
    get:
      parameters:
        - name: api_version
          in: header
          required: true
          schema:
            type: string
```

**Master OpenAPI:**
```yaml
paths:
  /users/{id}:
    get:
      parameters: []
```

**输出:**
```json
{
  "comparison": [
    {
      "generated_path": "/users/{id}",
      "master_path": "/users/{id}",
      "differences": [
        {
          "type": "method_modified",
          "method": "GET",
          "changes": [
            {
              "category": "parameters",
              "changes": [
                {
                  "type": "required_parameter_added",
                  "parameter": "api_version",
                  "breaking": true,
                  "description": "新增必填参数 api_version"
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "breaking_changes": [
    {
      "path": "/users/{id}",
      "type": "required_parameter_added",
      "method": "GET",
      "severity": "high",
      "description": "新增必填参数 api_version，可能导致现有调用失败"
    }
  ],
  "summary": {
    "total_changes": 1,
    "breaking_changes_count": 1,
    "recommendation": "检测到 Breaking Changes，需要审查和评估影响"
  }
}
```

### 示例 3：路径重命名

**Generated OpenAPI:**
```yaml
paths:
  /customers/{customerId}:
    get:
      summary: Get customer by ID
```

**Master OpenAPI:**
```yaml
paths:
  /users/{userId}:
    get:
      summary: Get user by ID
```

**输出:**
```json
{
  "path_changes": [
    {
      "type": "path_renamed",
      "old_path": "/users/{userId}",
      "new_path": "/customers/{customerId}",
      "similarity": 0.85,
      "breaking": true,
      "description": "路径从 /users/{userId} 重命名为 /customers/{customerId}"
    }
  ],
  "comparison": [],
  "breaking_changes": [
    {
      "path": "/users/{userId}",
      "type": "path_renamed",
      "method": null,
      "severity": "high",
      "description": "路径重命名，需要更新所有客户端代码"
    }
  ],
  "summary": {
    "total_changes": 0,
    "breaking_changes_count": 1,
    "path_changes_count": 1,
    "recommendation": "检测到路径重命名，需要更新客户端代码并设置过渡期"
  }
}
```

## 约束条件

1. 只对比 API 契约（接口签名），忽略描述性文字
2. 严格遵循 Breaking Changes 识别标准
3. 输出必须是有效的 JSON 格式
4. 如果没有差异，`differences` 数组应为空
5. 如果没有 Breaking Changes，`breaking_changes` 数组应为空
6. `recommendation` 字段应根据检测结果提供明确的建议
7. 路径变更应该通过相似度算法识别，相似度低于 0.7 的不应视为重命名

现在，请对比以下两个 OpenAPI 规范文件：

**Generated OpenAPI:**
{generated_openapi}

**Master OpenAPI:**
{master_openapi}

**Target Path:** {target_path}

请输出对比结果。
```

### 2.3 使用示例

#### 2.3.1 在主系统中调用 Agent

```python
import openai
import json
import re

def compare_openapi_with_agent(generated_openapi, master_openapi, target_path=None):
    """
    使用 Agent 对比两个 OpenAPI 文件
    
    Args:
        generated_openapi: Confluence 生成的 OpenAPI 内容（YAML 字符串）
        master_openapi: GitHub master 的 OpenAPI 内容（YAML 字符串）
        target_path: 可选，只对比特定的 API path
    
    Returns:
        对比结果（JSON 格式）
    """
    
    # 读取 Prompt 模板
    with open('prompts/openapi_comparison.txt', 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # 填充 Prompt
    prompt = prompt_template.format(
        generated_openapi=generated_openapi,
        master_openapi=master_openapi,
        target_path=target_path or "全部路径"
    )
    
    # 调用 LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一个专业的 API 规范专家。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,  # 低温度确保输出稳定
        max_tokens=4000
    )
    
    # 解析响应
    result_text = response.choices[0].message.content
    
    # 提取 JSON（处理可能的 markdown 代码块）
    if '```json' in result_text:
        result_text = result_text.split('```json')[1].split('```')[0].strip()
    elif '```' in result_text:
        result_text = result_text.split('```')[1].split('```')[0].strip()
    
    # 解析 JSON
    result = json.loads(result_text)
    
    return result
```

#### 2.3.2 处理结果

```python
# 调用 Agent
result = compare_openapi_with_agent(
    generated_openapi=generated_content,
    master_openapi=master_content,
    target_path="/users"
)

# 处理结果
if result['success']:
    print(f"检测到 {len(result['breaking_changes'])} 个 Breaking Changes")
    print(f"建议: {result['summary']['recommendation']}")
    
    # 展示路径变更
    if result['path_changes']:
        print("\n路径变更:")
        for change in result['path_changes']:
            print(f"  {change['old_path']} -> {change['new_path']} (相似度: {change['similarity']})")
    
    # 展示对比结果
    for comparison in result['comparison']:
        print(f"\n路径: {comparison['generated_path']}")
        for diff in comparison['differences']:
            print(f"  {diff['type']}: {diff.get('method', '')}")
            if diff.get('breaking'):
                print(f"    ⚠️ Breaking Change!")
```

### 2.4 注意事项

#### 2.4.1 Prompt 优化

- **Few-Shot Learning**：提供多个示例，提高输出质量
- **明确约束**：清楚说明要忽略的字段和规则
- **输出模板**：提供清晰的输出格式示例
- **温度设置**：使用低温度（0.1-0.3）确保输出稳定
- **路径相似度**：在 Prompt 中明确路径相似度的计算方法和阈值

#### 2.4.2 错误处理

- **JSON 解析失败**：处理 LLM 输出不是有效 JSON 的情况
- **不完整输出**：处理输出被截断的情况
- **格式错误**：验证输出是否符合预期格式

```python
def validate_comparison_result(result):
    """
    验证对比结果的完整性
    """
    required_fields = ['success', 'comparison', 'breaking_changes', 'summary']
    
    for field in required_fields:
        if field not in result:
            raise ValueError(f"缺少必需字段: {field}")
    
    # 验证 summary
    summary = result['summary']
    if 'breaking_changes_count' not in summary:
        raise ValueError("summary 中缺少 breaking_changes_count")
    
    if len(result['breaking_changes']) != summary['breaking_changes_count']:
        raise ValueError("breaking_changes 数量与 summary 不一致")
    
    return True
```

#### 2.4.3 性能优化

- **Token 限制**：对于大型 OpenAPI 文件，可能需要分块处理
- **缓存机制**：缓存相同输入的结果
- **模型选择**：根据复杂度选择 GPT-4 或 GPT-3.5

#### 2.4.4 路径变更检测

在 Prompt 中明确路径变更的识别逻辑：

```markdown
### 路径变更识别

当检测到以下情况时，应识别为路径变更：

1. **路径重命名**：
   - 计算路径相似度（使用编辑距离）
   - 相似度 >= 0.7 且 < 1.0 时，视为重命名
   - 相似度 < 0.7 时，视为删除+新增

2. **路径参数变更**：
   - 标准化路径（将参数名称替换为占位符）
   - 比较标准化后的路径
   - 例如：`/users/{id}` 和 `/users/{userId}` 标准化后都是 `/users/{}`

3. **路径前缀变更**：
   - 识别共同的路径后缀
   - 例如：`/api/users` 和 `/services/users` 共同后缀是 `/users`

请使用以下算法计算路径相似度：

```python
def calculate_path_similarity(path1, path2):
    # 标准化路径
    norm1 = normalize_path(path1)
    norm2 = normalize_path(path2)
    
    # 计算编辑距离
    distance = levenshtein_distance(norm1, norm2)
    
    # 计算相似度
    max_length = max(len(norm1), len(norm2))
    similarity = 1 - (distance / max_length) if max_length > 0 else 1.0
    
    return similarity
```
```

### 2.5 Prompt 模板管理

建议将 Prompt 存储在单独的文件中，便于管理和版本控制：

```
prompts/
├── openapi_comparison.txt
├── openapi_generation.txt
└── breaking_change_detection.txt
```

## 3. API 路径变更处理

### 3.1 路径变更类型

1. **完全重命名**：
   - 例如：`/users` → `/customers`
   - 检测方法：通过相似度算法识别低相似度但功能相似的路径

2. **路径参数变更**：
   - 例如：`/users/{id}` → `/users/{userId}`
   - 检测方法：标准化路径后比较（将 `{id}` 和 `{userId}` 都视为 `{}`）

3. **路径层级变更**：
   - 例如：`/v1/users` → `/v2/users`
   - 检测方法：提取核心路径部分（`/users`）进行比较

4. **路径前缀变更**：
   - 例如：`/api/users` → `/services/users`
   - 检测方法：识别共同的路径后缀

### 3.2 处理策略

#### 3.2.1 版本化处理

- **保持历史路径**：在新版本中保留旧路径，通过重定向或代理处理
- **路径映射**：建立新旧路径的映射关系，便于兼容性处理
- **版本控制**：使用路径版本号（如 `/v1/users` → `/v2/users`）

#### 3.2.2 迁移策略

1. **渐进式迁移**：
   - 先支持新旧路径并存
   - 监控旧路径使用情况
   - 逐步废弃旧路径

2. **通知机制**：
   - 在对比报告中明确标记路径变更
   - 提供详细的迁移指南
   - 建议设置过渡期

### 3.3 最佳实践

1. **路径设计一致性**：
   - 采用统一的路径命名规范
   - 避免频繁的路径变更
   - 使用版本号管理 API 变更

2. **变更管理**：
   - 建立 API 变更审批流程
   - 维护 API 变更日志
   - 为重大变更提供迁移指南

3. **自动化检测**：
   - 集成路径变更检测到 CI/CD 流程
   - 自动生成变更报告
   - 提供变更影响分析

4. **兼容性考虑**：
   - 考虑使用 API 网关进行路径映射
   - 实现请求转发机制
   - 提供详细的 API 文档

## 4. 总结

**核心原则**：
1. 关注 API 契约而非文本差异
2. 识别真正的 Breaking Changes
3. 提供可操作的对比报告
4. 支持特定 Path 的精准对比

**关键实现**：
1. 使用 Agent + Prompt 进行语义化对比
2. 精心设计的 Prompt 包含角色定义、任务描述、对比规则、输出格式、示例和约束条件
3. 通过 Few-Shot Learning 提高输出质量
4. 智能路径变更检测和 Breaking Changes 识别

通过使用 Agent 和精心设计的 Prompt，可以充分利用 LLM 的语义理解能力，更准确地识别 API 规范中的差异和 Breaking Changes，同时保持代码的简洁性和可维护性。这种方案可以有效避免"一行行对比导致的差异爆炸"问题，专注于真正影响 API 兼容性的改动。
