import os
import sys

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama


def resource_path(relative_path):
    """获取资源的绝对路径，适配开发和打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS  # 打包后的临时解压目录
    else:
        base_path = os.path.abspath("..")  # 开发环境根目录
    return os.path.join(base_path, relative_path)

# 配置 LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "多文档"

chunk_size=1000
chunk_overlap=100
llm_name="qwen2.5:1.5b"
langchain_llm=Ollama(model=llm_name)
embed_model = OllamaEmbeddings(model="bge-m3", base_url="http://localhost:11434")