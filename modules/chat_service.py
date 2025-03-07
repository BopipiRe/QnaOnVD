from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# 获取检索型问答链
def get_qa_chain(vector_store):
    prompt_template = """### 规则
                        1. 仅使用以下上下文回答问题
                        2. 若答案不在上下文中，必须返回："根据已知信息无法回答"

                        上下文
                        {context}

                        问题
                        {question}

                        回答（严格遵循规则）"""

    prompt = PromptTemplate(template=prompt_template,
                            input_variables=["context", "question"])
    try:
        # 初始化 Ollama 模型
        llm = Ollama(model="qwen2.5:0.5b")  # 确保本地已下载该模型 (ollama pull qwen2.5:1.5b)
    except Exception as e:
        raise RuntimeError(f"Ollama 模型初始化失败: {str(e)}")

    return RetrievalQA.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),  # 返回前3个相关文档块
        # chain_type="map_reduce",  # 处理长文本
        return_source_documents=True,  # 返回来源文档（调试用）
        prompt=prompt
    )

