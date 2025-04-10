from deprecated import deprecated
from langchain.chains import RetrievalQA, LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain, create_stuff_documents_chain
from langchain.prompts import PromptTemplate
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from settings import langchain_llm, score_threshold


class ChatService:
    def __init__(self, llm=langchain_llm, vector_store=None):
        self.llm = llm
        # self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.prompt_template = self._get_prompt_template()
        self.vector_store = vector_store

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

    @deprecated(version='1.0', reason="This function will be removed soon")
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
                    return {"result": "根据提供资料无法回答", "source_documents": []}  #

                # 调用父类的 _call 方法生成答案(多一次数据库查询操作)
                # return super()._call(inputs)

                # 构造 combine_documents_chain 所需的输入
                inputs_for_combine = {
                    "input_documents": docs,  # 检索到的文档
                    "question": query  # 用户的问题
                }

                # 调用 combine_documents_chain 生成答案
                result = self.combine_documents_chain.invoke(inputs_for_combine)
                source_documents = []
                for doc in docs:
                    source_document = doc.dict()
                    source_documents.append(source_document)
                # 返回结果
                return {"result": result["output_text"], "source_documents": source_documents}  #

        # 返回自定义 RetrievalQA
        return CustomRetrievalQA(
            combine_documents_chain=combine_documents_chain,
            retriever=retriever,
            return_source_documents=True
        )

    def _invoke(self, query):
        # 配置检索器
        retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": score_threshold}  # 设置得分阈值
        )

        # 创建 StuffDocumentsChain
        combine_documents_chain = create_stuff_documents_chain(llm=self.llm, prompt=self.prompt_template)

        docs = retriever.invoke(query)
        # 如果没有检索到相关文档，直接返回预设提示
        if not docs:
            return {"result": "根据提供资料无法回答", "source_documents": []}
        result = combine_documents_chain.invoke({"context": docs, "question": query})
        source_documents = [{"page_content": doc.page_content, "source": doc.metadata["source"]} for doc in docs]
        # 返回结果
        return {"result": result, "source_documents": source_documents}

    async def invoke(self, query):
        # 创建服务器参数
        server_params = StdioServerParameters(
            command="python",
            # 确保更新为 math_server.py 文件路径
            args=["service/mcp_service.py"],
        )

        # 使用 stdio_client 进行连接
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化连接
                await session.initialize()

                # 加载工具
                mcp_tools = await load_mcp_tools(session)
                print("加载工具完成: ", [tool.name for tool in mcp_tools])

                # 创建代理
                agent = create_react_agent(ChatOllama(model="qwen2.5:1.5b", temperature=0.7), mcp_tools)

                # 调用代理处理问题
                agent_response = await agent.ainvoke({"messages": [{"role": "user", "content": query},
                                                                   {"role": "system", "content": "使用中文进行回答"}]})

                # 打印完整响应（调试用）
                # print("\n完整响应:", agent_response)
                for message in agent_response["messages"]:
                    if message.type == "tool":
                        print(f"工具调用: {message.name}\n结果：{message.content}")

                if any(message.type == "tool" for message in agent_response["messages"]):
                    return {"result": agent_response["messages"][-1].content, "source_documents": "工具调用"}
                else:
                    return self._invoke(query)
