from langchain.memory import ConversationBufferMemory

from .chat_service import ChatService
from .vector_service import VectorService

# 初始化对话记忆
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)