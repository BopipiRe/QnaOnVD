import logging
import os

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama

# 配置日志级别和输出格式
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -  %(levelname)s - %(message)s')

# 配置 LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "工具"

chunk_size=1000
chunk_overlap=100
llm_name="qwen2.5:1.5b"
langchain_llm=Ollama(model=llm_name)
embed_model = OllamaEmbeddings(model="bge-m3", base_url="http://localhost:11434")

# 向量数据库名称
default_db='default'
# 向量数据库持久化地址
chroma_db='resources/chroma_db'
# 工具持久化
tool_json='resources/tool.json'

# 工具json格式配置
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string",
                 "pattern": "^[^:]+$"},
        "type": {"type": "string", "enum": ["SQL", "API"]},
        "url": {"type": "string", "format": "url"},
        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
        "description": {"type": "string"},
        "input_schema": {
            "type": "object",
            "patternProperties": {
                # 定义属性名称的规则：长度 2-10，且不包含冒号
                "^.+$": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["string", "number", "boolean", "object", "array"]},
                        # "required": {"type": "boolean"}
                    },
                    "required": ["type"] #, "required"
                }
            },
            # 至少需要一个属性
            "minProperties": 1,
            # 不允许其他不符合规则的属性名称
            "additionalProperties": False
        },
        "response_format": {"type": "string"}
    },
    "required": ["name", "type", "url", "method", "description"]
}