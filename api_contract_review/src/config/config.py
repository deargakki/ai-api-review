import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    # Confluence 配置
    CONFLUENCE_URL = os.getenv('CONFLUENCE_URL')
    CONFLUENCE_USERNAME = os.getenv('CONFLUENCE_USERNAME')
    CONFLUENCE_API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN')
    
    # OpenAI 配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://aihubmix.com/v1')
    
    # GitHub 配置
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    
    # Spectral 配置
    SPECTRAL_SERVICE_URL = os.getenv('SPECTRAL_SERVICE_URL', 'http://localhost:8000')
    
    # Cage Scan 配置（可选）
    CAGE_SCAN_URL = os.getenv('CAGE_SCAN_URL')
    CAGE_SCAN_API_KEY = os.getenv('CAGE_SCAN_API_KEY')
    
    # LLM 配置
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'mimo-v2-flash-free')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '6000'))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.1'))

# 创建配置实例
config = Config()
