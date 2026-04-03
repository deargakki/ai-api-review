# 从 Confluence 生成 OpenAPI 规范的实现方案

## 1. 问题分析

根据 PRD 中的描述，我们需要从 Confluence API Contract 页面内容生成 OpenAPI 3.0 规范。这是一个典型的"非结构化内容转结构化格式"的任务。

**核心挑战**：
1. Confluence 页面内容是 HTML 格式，结构可能不统一
2. API Contract 的描述方式可能因团队而异
3. 需要准确提取 API 的各个要素（端点、参数、请求体、响应等）
4. 生成的 OpenAPI 规范需要符合标准格式

## 2. 实现方法对比

### 2.1 方法一：使用 LLM + Prompt Engineering（推荐）

**原理**：
通过精心设计的 prompt，让 LLM 理解 Confluence 内容并生成符合 OpenAPI 规范的输出。

**优点**：
- 灵活性高，适应不同格式的 Confluence 页面
- 实现简单，不需要复杂的代码逻辑
- 可以处理自然语言描述
- 易于迭代优化

**缺点**：
- 依赖 LLM 的理解能力
- 可能存在输出不一致的问题
- 需要精心设计 prompt

**实现示例**：

```python
class OpenAPIGenerator:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def generate_from_confluence(self, confluence_content):
        """
        从 Confluence 内容生成 OpenAPI 规范
        """
        prompt = self._build_prompt(confluence_content)
        response = self.llm_client.generate(prompt)
        
        # 验证和清理输出
        openapi_spec = self._validate_and_clean(response)
        
        return openapi_spec
    
    def _build_prompt(self, confluence_content):
        """
        构建 prompt
        """
        prompt = f"""
你是一个 API 规范专家。请根据以下 Confluence API Contract 页面内容，生成符合 OpenAPI 3.0 规范的 YAML 文件。

Confluence 页面内容：
{confluence_content}

要求：
1. 严格遵循 OpenAPI 3.0 规范
2. 提取所有 API 端点信息
3. 包含完整的请求参数、请求体和响应定义
4. 使用合理的 schema 定义
5. 添加适当的描述信息

请直接输出 OpenAPI YAML 内容，不要包含其他解释文字。
"""
        return prompt
    
    def _validate_and_clean(self, response):
        """
        验证和清理 LLM 输出
        """
        # 移除可能的 markdown 代码块标记
        if response.startswith('```yaml'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        
        # 验证 YAML 格式
        try:
            import yaml
            spec = yaml.safe_load(response)
            # 可以添加更多的验证逻辑
            return response.strip()
        except Exception as e:
            raise ValueError(f"Invalid OpenAPI spec: {e}")
```

### 2.2 方法二：使用 Skill（LangChain Agent）

**原理**：
创建一个专门的 skill，定义明确的输入输出格式和处理逻辑，让 agent 按照预定义的步骤执行。

**优点**：
- 流程标准化，输出更一致
- 可以包含多个步骤和验证环节
- 易于维护和扩展
- 可以集成多个工具

**缺点**：
- 实现复杂度较高
- 需要定义详细的步骤和规则
- 灵活性相对较低

**实现示例**：

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class OpenAPIGeneratorInput(BaseModel):
    confluence_content: str = Field(description="Confluence API Contract 页面内容")

class OpenAPIGeneratorTool(BaseTool):
    name = "generate_openapi_from_confluence"
    description = "从 Confluence API Contract 内容生成 OpenAPI 3.0 规范"
    args_schema = OpenAPIGeneratorInput
    
    def _run(self, confluence_content: str):
        """
        执行 OpenAPI 生成流程
        """
        # 步骤 1: 解析 Confluence 内容
        parsed_content = self._parse_confluence(confluence_content)
        
        # 步骤 2: 提取 API 信息
        api_info = self._extract_api_info(parsed_content)
        
        # 步骤 3: 构建 OpenAPI 结构
        openapi_structure = self._build_openapi_structure(api_info)
        
        # 步骤 4: 生成 YAML
        openapi_yaml = self._generate_yaml(openapi_structure)
        
        # 步骤 5: 验证
        validated_spec = self._validate_spec(openapi_yaml)
        
        return validated_spec
    
    def _parse_confluence(self, content):
        # 解析 HTML 内容
        pass
    
    def _extract_api_info(self, parsed_content):
        # 提取 API 信息
        pass
    
    def _build_openapi_structure(self, api_info):
        # 构建 OpenAPI 结构
        pass
    
    def _generate_yaml(self, structure):
        # 生成 YAML
        pass
    
    def _validate_spec(self, yaml_content):
        # 验证规范
        pass
```

### 2.3 方法三：规则引擎 + 模板

**原理**：
基于预定义的规则和模板，通过程序逻辑提取信息并填充模板。

**优点**：
- 输出完全可控
- 性能高，不依赖 LLM
- 适合标准化程度高的页面

**缺点**：
- 灵活性差，难以适应不同格式
- 需要编写大量解析规则
- 维护成本高

**实现示例**：

```python
import yaml
from string import Template

class OpenAPITemplateGenerator:
    def __init__(self):
        self.template = Template("""
openapi: 3.0.0
info:
  title: $api_name
  version: $api_version
  description: $api_description

paths:
$path_definitions

components:
  schemas:
$schema_definitions
""")
    
    def generate(self, confluence_content):
        # 解析内容
        api_info = self._parse_content(confluence_content)
        
        # 生成路径定义
        path_definitions = self._generate_paths(api_info['endpoints'])
        
        # 生成 schema 定义
        schema_definitions = self._generate_schemas(api_info['schemas'])
        
        # 填充模板
        openapi_yaml = self.template.substitute(
            api_name=api_info['name'],
            api_version=api_info['version'],
            api_description=api_info['description'],
            path_definitions=path_definitions,
            schema_definitions=schema_definitions
        )
        
        return openapi_yaml
```

### 2.4 方法四：混合方法（推荐）

**原理**：
结合规则引擎和 LLM 的优势，先用规则提取结构化信息，再用 LLM 生成最终规范。

**优点**：
- 兼顾灵活性和可控性
- 减少对 LLM 的依赖
- 提高输出质量

**缺点**：
- 实现复杂度较高
- 需要维护两套逻辑

**实现示例**：

```python
class HybridOpenAPIGenerator:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.rule_parser = ConfluenceParser()  # 之前定义的解析器
    
    def generate(self, confluence_content):
        # 步骤 1: 使用规则提取结构化信息
        structured_info = self.rule_parser.parse_content(confluence_content)
        
        # 步骤 2: 使用 LLM 补充和优化
        prompt = self._build_prompt_from_structured_info(structured_info)
        openapi_spec = self.llm_client.generate(prompt)
        
        # 步骤 3: 验证和清理
        validated_spec = self._validate_and_clean(openapi_spec)
        
        return validated_spec
    
    def _build_prompt_from_structured_info(self, structured_info):
        prompt = f"""
根据以下结构化的 API 信息，生成 OpenAPI 3.0 规范：

API 信息：
{structured_info}

要求：
1. 严格遵循 OpenAPI 3.0 规范
2. 补充合理的描述和示例
3. 确保类型定义准确
4. 添加适当的错误响应定义

请直接输出 OpenAPI YAML 内容。
"""
        return prompt
```

## 3. 推荐方案

### 3.1 短期方案：LLM + Prompt Engineering

**理由**：
- 实现简单，快速验证
- 适应性强，可以处理不同格式的页面
- 成本可控

**关键要素**：
1. **精心设计的 Prompt**：
   - 明确任务目标
   - 提供示例输出
   - 指定输出格式
   - 强调关键要求

2. **输出验证**：
   - YAML 格式验证
   - OpenAPI 规范验证
   - 必要字段检查

3. **迭代优化**：
   - 收集失败案例
   - 优化 prompt
   - 建立测试集

### 3.2 长期方案：混合方法

**理由**：
- 结合规则和 LLM 的优势
- 提高输出质量和一致性
- 降低成本和延迟

**实施步骤**：
1. 先实现纯 LLM 方案，收集数据
2. 分析常见模式和问题
3. 逐步引入规则引擎
4. 最终形成混合方案

## 4. Prompt 设计最佳实践

### 4.1 Prompt 结构

```
1. 角色定义：明确 LLM 的角色和任务
2. 输入描述：清晰描述输入内容的格式和来源
3. 任务要求：明确输出的格式和标准
4. 示例输出：提供期望输出的示例
5. 约束条件：强调关键要求和限制
```

### 4.2 示例 Prompt

```python
OPENAPI_GENERATION_PROMPT = """
你是一个 API 规范专家，专门负责将 API 文档转换为 OpenAPI 3.0 规范。

任务：根据提供的 Confluence API Contract 页面内容，生成符合 OpenAPI 3.0 规范的 YAML 文件。

输入内容：
{confluence_content}

输出要求：
1. 严格遵循 OpenAPI 3.0 规范（https://spec.openapis.org/oas/v3.0.0）
2. 包含以下必要字段：
   - openapi: 3.0.0
   - info: title, version, description
   - paths: 所有 API 端点定义
   - components: schemas, parameters 等

3. 对于每个 API 端点，必须包含：
   - HTTP 方法（GET, POST, PUT, DELETE 等）
   - 请求参数（path, query, header）
   - 请求体（如果有）
   - 响应定义（至少包含成功响应）

4. 使用合理的类型定义：
   - string, integer, boolean, array, object
   - 必要时使用 $ref 引用 components 中的定义

5. 添加适当的描述和示例

示例输出格式：
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
          schema:
            type: integer
          description: Maximum number of users to return
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

请直接输出 OpenAPI YAML 内容，不要包含其他解释文字。
"""
```

### 4.3 Few-Shot Learning

如果需要更高的准确性，可以使用 Few-Shot Learning：

```python
OPENAPI_GENERATION_PROMPT_FEW_SHOT = """
你是一个 API 规范专家。请参考以下示例，将 Confluence API Contract 转换为 OpenAPI 3.0 规范。

示例 1：
输入：
<h2>User API</h2>
<p>获取用户列表</p>
<h3>Endpoint</h3>
<p>GET /api/v1/users</p>
<h3>Parameters</h3>
<table>
  <tr><td>limit</td><td>integer</td><td>返回用户数量限制</td></tr>
</table>

输出：
```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /api/v1/users:
    get:
      summary: 获取用户列表
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
          description: 返回用户数量限制
      responses:
        '200':
          description: Success
```

现在请处理以下输入：
{confluence_content}

请直接输出 OpenAPI YAML 内容。
"""
```

## 5. 验证和测试

### 5.1 自动验证

```python
import yaml
import json
from openapi_spec_validator import validate

class OpenAPIValidator:
    def validate_spec(self, spec_content):
        """
        验证 OpenAPI 规范
        """
        try:
            # 解析 YAML
            spec = yaml.safe_load(spec_content)
            
            # 验证 OpenAPI 规范
            validate(spec)
            
            # 检查必要字段
            self._check_required_fields(spec)
            
            return {
                "valid": True,
                "spec": spec
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def _check_required_fields(self, spec):
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in spec:
                raise ValueError(f"Missing required field: {field}")
```

### 5.2 测试集

建立测试集，包含不同类型的 API Contract 页面：
- 简单的 CRUD API
- 复杂的业务 API
- 包含认证的 API
- 包含文件上传的 API

## 6. 成本优化

### 6.1 缓存策略

```python
import hashlib

class OpenAPIGeneratorWithCache:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.cache = {}
    
    def generate(self, confluence_content):
        # 计算内容 hash
        content_hash = hashlib.md5(confluence_content.encode()).hexdigest()
        
        # 检查缓存
        if content_hash in self.cache:
            return self.cache[content_hash]
        
        # 生成 OpenAPI
        openapi_spec = self._generate_with_llm(confluence_content)
        
        # 缓存结果
        self.cache[content_hash] = openapi_spec
        
        return openapi_spec
```

### 6.2 模型选择

- 简单页面：使用 GPT-3.5-turbo
- 复杂页面：使用 GPT-4
- 批量处理：使用更便宜的模型，人工审核关键部分

## 7. 总结

**推荐方案**：
1. **短期**：使用 LLM + 精心设计的 Prompt
2. **长期**：采用混合方法，结合规则引擎和 LLM

**关键成功因素**：
1. Prompt 设计质量
2. 输出验证机制
3. 持续优化和迭代
4. 建立测试集和评估标准

**实施建议**：
1. 先实现简单版本，快速验证
2. 收集实际数据，优化 prompt
3. 逐步引入验证和优化机制
4. 最终形成稳定可靠的生成流程