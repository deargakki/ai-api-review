from openai import OpenAI
from ..config.config import config
from ..llms.prompts import OPENAPI_GENERATION_PROMPT, OPENAPI_COMPARISON_PROMPT, SYSTEM_PROMPT_API_DESIGNER, SYSTEM_PROMPT_API_REVIEWER

class OpenAPIService:
    def __init__(self):
        """初始化 OpenAPI 服务"""
        self.api_key = config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 环境变量未设置")
        
        # 创建 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=config.OPENAI_BASE_URL
        )

    def generate_openapi(self, confluence_content):
        """从 Confluence 内容生成 OpenAPI 规范"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                if attempt == 0:
                    # 第一次尝试：使用原始 prompt
                    prompt = OPENAPI_GENERATION_PROMPT.format(api_contract=confluence_content)
                else:
                    # 后续尝试：包含之前的错误信息
                    prompt = f"{OPENAPI_GENERATION_PROMPT.format(api_contract=confluence_content)}\n\nPrevious validation error: {validation_error}\nPlease fix the error and generate a valid OpenAPI 3.0 specification."
                
                response = self.client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT_API_DESIGNER},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=config.OPENAI_TEMPERATURE,
                    max_tokens=config.OPENAI_MAX_TOKENS
                )
                
                generated_openapi = response.choices[0].message.content
                
                # 验证生成的 OpenAPI 规范
                is_valid, validation_error = self.validate_openapi(generated_openapi)
                if is_valid:
                    print(f"OpenAPI generation successful on attempt {attempt + 1}")
                    return generated_openapi
                else:
                    print(f"OpenAPI validation failed on attempt {attempt + 1}, retrying...")
                    continue
            except Exception as e:
                print(f"Error generating OpenAPI on attempt {attempt + 1}: {e}")
                continue
        
        print(f"Failed to generate valid OpenAPI after {max_attempts} attempts")
        return None

    def validate_openapi(self, openapi_content):
        """验证 OpenAPI 规范"""
        try:
            from openapi_spec_validator import validate_spec
            from openapi_spec_validator.readers import read_from_content
            spec_dict, _ = read_from_content(openapi_content)
            validate_spec(spec_dict)
            return True, None
        except Exception as e:
            error_message = f"OpenAPI validation error: {e}"
            print(error_message)
            return False, error_message

    def compare_openapi(self, generated_openapi, master_openapi):
        """对比两个 OpenAPI 规范"""
        try:
            prompt = OPENAPI_COMPARISON_PROMPT.format(
                generated_openapi=generated_openapi,
                master_openapi=master_openapi
            )
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_API_REVIEWER},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.OPENAI_TEMPERATURE,
                max_tokens=config.OPENAI_MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error comparing OpenAPI: {e}")
            return None
