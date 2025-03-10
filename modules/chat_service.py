from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# 获取检索型问答链
def get_qa_chain(vector_store):
    prompt_template = """### 规则
                        1. 仅使用提供的上下文回答问题
                        2. 若答案不在提供的上下文中，只需要回答："根据已知信息无法回答"
                        ### 上下文
                        {context}
                        ### 问题
                        {question}
                        ### 回答（严格遵循规则）"""

    prompt_template_new = """# 角色设定
                            你是一名专业文档分析员，严格基于提供的上下文信息回答问题
                            
                            # 输入规范
                            <上下文>
                            {context}
                            </上下文>
                            
                            # 应答规则
                            1. 答案必须完全来源于<上下文>，禁止编造信息
                            2. 若上下文不包含有效信息，只需要回复："根据提供资料无法回答"
                            3. 若问题与上下文无关，只需要回复："问题超出知识范围"
                            4. 答案使用中文
                            
                            # 当前问题
                            {question}
                            
                            # 响应格式
                            <答案>
                            [在此填写结构化回答]
                            </答案>"""

    prompt = PromptTemplate(template=prompt_template_new,
                            input_variables=["context", "question"])

    # 初始化 Ollama 模型
    llm = Ollama(model="qwen2.5:0.5b")  # 确保本地已下载该模型 (ollama pull qwen2.5:1.5b)

    return RetrievalQA.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        chain_type="map_reduce",  # 处理长文本
        return_source_documents=True,  # 返回来源文档（调试用）
        prompt=prompt
    )

