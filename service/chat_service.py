from langchain.chains import RetrievalQA, LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate

from settings import langchain_llm


class ChatService:
    def __init__(self, llm=langchain_llm):
        self.llm = llm
        # self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.prompt_template = self._get_prompt_template()

    def _get_prompt_template(self):
        """
        定义提示词模板。
        :return: PromptTemplate 对象
        """
        prompt_template = """# 角色设定
        你是一名专业文档分析员，严格基于提供的上下文信息回答问题。

        # 输入规范
        <上下文>
        {context}
        </上下文>

        # 应答规则
        1. 答案必须完全来源于<上下文>，禁止编造信息。
        2. 若上下文不包含有效信息，只需要回复："根据提供资料无法回答"。
        3. 若问题与上下文无关，只需要回复："问题超出知识范围"。
        4. 答案使用中文。

        # 当前问题
        {question}"""
        return PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    def get_qa_chain(self, vector_store):
        """
        获取问答链。
        :param vector_store: 向量存储对象
        :return: RetrievalQA 对象
        """
        # 配置检索器
        retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.6}  # 设置得分阈值
        )

        # 创建 LLMChain
        llm_chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

        # 创建 StuffDocumentsChain
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_variable_name="context"
        )

        # 创建自定义 RetrievalQA
        class CustomRetrievalQA(RetrievalQA):
            def _call(self, inputs):
                # 检查是否检索到相关文档
                query = inputs["query"]
                docs = self.retriever.invoke(query)

                # 如果没有检索到相关文档，直接返回预设提示
                if not docs:
                    return {"result": "根据提供资料无法回答"} # , "source_documents": docs}

                # 调用父类的 _call 方法生成答案(多一次数据库查询操作)
                # return super()._call(inputs)

                # 构造 combine_documents_chain 所需的输入
                inputs_for_combine = {
                    "input_documents": docs,  # 检索到的文档
                    "question": query  # 用户的问题
                }

                # 调用 combine_documents_chain 生成答案
                result = self.combine_documents_chain.invoke(inputs_for_combine)

                # 返回结果
                return {"result": result["output_text"]} # , "source_documents": docs}

        # 返回自定义 RetrievalQA
        return CustomRetrievalQA(
            combine_documents_chain=combine_documents_chain,
            retriever=retriever,
            # return_source_documents=True
        )
