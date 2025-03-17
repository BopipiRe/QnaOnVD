from langchain.chains import RetrievalQA
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama


class ChatService:
    def __init__(self, model_name="qwen2.5:1.5b", base_url="http://localhost:11434"):
        """
        初始化问答系统。

        :param model_name: Ollama 模型名称
        :param base_url: Ollama 服务地址
        """
        self.model_name = model_name
        self.base_url = base_url
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.prompt_template = self._get_prompt_template

    @property
    def _get_prompt_template(self):
        """
        定义提示词模板。

        :return: PromptTemplate 对象
        """
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
                                {question}"""
        return PromptTemplate(template=prompt_template_new, input_variables=["context", "question"])

    def get_qa_chain(self, vector_store):
        """
        获取问答链。

        :param vector_store: 向量存储对象
        :return: RetrievalQA 对象
        """
        # 初始化 Ollama 模型
        llm = Ollama(model=self.model_name)
        # 创建文档组合链
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=LLMChain(llm=llm, prompt=self.prompt_template),
            document_variable_name="context"
        )
        # 创建 RetrievalQA
        return RetrievalQA(
            combine_documents_chain=combine_documents_chain,
            retriever=vector_store.as_retriever(),
            return_source_documents=True
        )