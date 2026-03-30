from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from typing import List
from src.tools.api_tools import (
    ConfluenceTool,
    SpectralRulesGeneratorTool,
    DiffTool,
    SpectralScanTool
)

class APIReviewAgent:
    def __init__(
        self,
        openai_api_key: str,
        confluence_url: str,
        confluence_token: str
    ):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            openai_api_key=openai_api_key
        )
        
        self.tools = self._init_tools(
            openai_api_key,
            confluence_url,
            confluence_token
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.agent_executor = self._create_agent()
    
    def _init_tools(
        self,
        openai_api_key: str,
        confluence_url: str,
        confluence_token: str
    ) -> List:
        return [
            ConfluenceTool(confluence_url, confluence_token),
            SpectralRulesGeneratorTool(openai_api_key),
            DiffTool(),
            SpectralScanTool()
        ]
    
    def _create_agent(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的 API Review Agent，负责自动审查 API 变更。

你的工作流程：
1. 使用 read_confluence 工具读取 API Review 规范
2. 使用 generate_spectral_rules 工具生成 Spectral 规则
3. 使用 compare_openapi 工具对比新旧 OpenAPI 文件
4. 使用 run_spectral 工具运行 Spectral 扫描
5. 综合所有结果，生成详细的 Review 报告

报告格式：
## 📊 API Review 报告

### 变更摘要
- Breaking Changes: X 个
- Non-Breaking Changes: Y 个
- Spectral Issues: Z 个

### 详细变更
[列出所有变更]

### 合规性检查
[列出所有问题]

### 建议
[提供改进建议]

注意事项：
- 按顺序执行每个步骤
- 在每个步骤后总结关键信息
- 如果发现 Breaking Changes，需要特别标注
- 最后生成完整的 Markdown 格式报告
            """),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="chat_history"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=15,
            handle_parsing_errors=True
        )
    
    def run(self, task: str) -> str:
        result = self.agent_executor.invoke({"input": task})
        return result["output"]
