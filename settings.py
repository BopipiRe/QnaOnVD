import logging
import os
from typing import Any

from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM

# 配置日志级别和输出格式
logging.basicConfig(level=logging.ERROR, format='%(asctime)s -  %(levelname)s - %(message)s')

# 设置并发参数（Ollama 0.2+ 特性）
# os.environ["OLLAMA_MAX_LOADED_MODELS"] = "2"  # 最大同时加载模型数
os.environ["OLLAMA_NUM_PARALLEL"] = str(min(32, (os.cpu_count() or 1) + 4))  # 每个模型的并行请求数

# 配置 LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "工具"

os.environ["ANONYMIZED_TELEMETRY"] = "False"

chunk_size = 500
chunk_overlap = 100
score_threshold = 0.6
langchain_llm = OllamaLLM(model="qwen2.5:1.5b")
embed_model = OllamaEmbeddings(model="bge-m3", base_url="http://localhost:11434")

# 向量数据库名称
default_db = 'default'
# 向量数据库持久化地址
chroma_db = 'resources/chroma_db'
# 工具持久化
tool_json = 'resources/tool.json'

# 工具json格式配置
_schema = {
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
                        "required": {"type": "boolean"}
                    },
                    "required": ["type"]  # , "required"
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

schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^([\u4e00-\u9fa5a-zA-Z])([\u4e00-\u9fa5a-zA-Z0-9_-]{,8})$"
        },
        "type": {"type": "string", "enum": ["SQL", "API"]},
        "url": {"type": "string", "format": "uri"},
        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
        "description": {"type": "string"},
        "input_schema": {
            "type": "object",
            "patternProperties": {
                "^([a-zA-Z])([a-zA-Z0-9_]{,8})$": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["string", "int", "float", "bool", "list", "dict", "any"]},
                        "required": {"type": "boolean"}
                    },
                    "required": ["type", "required"]  # 要求这两个字段
                }
            },
            "minProperties": 1,
            "additionalProperties": False
        }
    },
    "required": ["name", "type", "url", "method", "description", "input_schema"]
}

TYPE_MAPPING = {
    "string": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
    "any": Any  # 任意类型
}
