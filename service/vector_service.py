import logging
import os.path

import chromadb
from deprecated import deprecated
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

from settings import embed_model, chunk_size, chunk_overlap, langchain_llm, default_db, resource_path, chroma_db


class VectorService:
    def __init__(self, persist_directory=resource_path(chroma_db), collection_name=default_db):
        """
        初始化向量存储管理器。

        :param collection_name: 集合名称
        :param persist_directory: 持久化存储目录
        """
        self.db = Chroma(
            collection_name=collection_name,
            embedding_function=embed_model,
            persist_directory=persist_directory,
            collection_metadata={"hnsw:space": "cosine"}  # 使用余弦相似度("hnsw:space": "cosine")l2
        )

    def _file_chunks(self, file):
        """
        将指定路径的文档（PDF 或 DOCX）切分成较小的块。
        :param file: 文档
        :return: 文档的chunks
        """
        if not os.path.exists(file):
            raise FileNotFoundError(f"文件 {file} 不存在。")
        if file.endswith(".pdf"):
            loader = PyPDFLoader(file)
        elif file.endswith('.docx') or file.endswith('.doc'):
            loader = Docx2txtLoader(file)
        elif file.endswith('.txt'):
            loader = TextLoader(file)
        else:
            raise ValueError(f"不支持的文件类型: {file}")
        document = loader.load()
        # Split the documents into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n\n", "\n", "。", "！"]
        )
        documents = text_splitter.split_documents(document)
        return documents

    def file_index(self, file):
        """
        将指定路径的文档（PDF 或 DOCX）嵌入并存储到向量数据库中。
        :param file: 文档路径
        """
        try:
            if file in self.get_documents():
                return "文件已存在"
            self.db.add_documents(self._file_chunks(file))
            return "文件索引成功"
        except Exception as e:
            return f"文件索引失败: {e}"

    @deprecated(version='1.0', reason="This function will be removed soon")
    def text_index(self, text, source):
        """
        将文本数据嵌入并存储到向量数据库中，source作为标识
        :param text: 文本
        :param source: 来源，标识
        """
        text_with_source = Document(page_content=text, metadata={'source': source})
        self.db.add_documents([text_with_source])

    @deprecated(version='1.0', reason="This function will be removed soon")
    def file_summary_index_by_refine(self, file):
        """
        对单个文档进行摘要并嵌入、持久化
        :param file: 文档
        """
        # 加载文档并保留元数据
        split_documents = self._file_chunks(file)

        # Initial 提示词模板
        initial_prompt_template = """请根据以下文本生成中文摘要，涵盖以下内容：
        1. **核心主题**：文档的主要目标或主题是什么？
        2. **关键方法**：文档中使用了哪些方法、技术或流程？
        3. **主要结果**：文档得出了哪些重要结论、发现或数据？
        4. **结论或建议**：文档的最终结论或建议是什么？
        
        要求：
        - 摘要长度控制在100字以内，语言简洁明了。
        - 确保逻辑连贯，结构清晰，避免冗长的句子。
        - 保留文档的核心信息，避免遗漏关键细节。
        
        文本：
        {text}
        
        中文摘要："""
        INITIAL_PROMPT = PromptTemplate(template=initial_prompt_template, input_variables=["text"])

        # Refine 提示词模板
        refine_prompt_template = """请根据以下文本和已有的摘要，生成一个更完善的中文摘要，确保：
        1. **总分结构**：
           - 总：提炼所有摘要的核心主题或目的形成一句全文总结；
           - 分：保留每个摘要的核心信息，避免遗漏关键细节。
        2. **逻辑连贯**：确保摘要逻辑清晰，避免重复或冗余信息。
        3. **长度控制**：摘要长度控制在500字以内。
        
        已有摘要：
        {existing_answer}
        
        文本：
        {text}
        
        更完善的中文摘要："""
        REFINE_PROMPT = PromptTemplate(template=refine_prompt_template, input_variables=["existing_answer", "text"])

        # 设置摘要链
        chain = load_summarize_chain(
            langchain_llm,
            chain_type="refine",
            question_prompt=INITIAL_PROMPT,
            refine_prompt=REFINE_PROMPT,
        )

        # 生成摘要并保留元数据
        summary = chain.run(split_documents)
        logging.info("中文摘要:", summary)
        logging.info("Metadata:", split_documents[0].metadata)  # 保留元数据

        # 创建langchain文档对象
        document = Document(page_content=summary, metadata=split_documents[0].metadata)
        # 将文档添加到向量数据库
        try:
            self.db.add_documents([document])
        except Exception as e:
            logging.error(f"文档的摘要 {file} 添加到向量存储时出错：{e}")
        logging.info(f"文档的摘要 {file} 添加到向量存储时成功。")

    @deprecated(version='1.0', reason="This function will be removed soon")
    def file_summary_index(self, file):
        """
        对单个文档进行摘要并嵌入、持久化
        :param file: 文档
        """
        # 加载文档并保留元数据
        split_documents = self._file_chunks(file)

        # Map 提示词模板
        map_prompt_template = """请根据以下文本生成中文摘要，涵盖以下内容：
        -确保逻辑连贯，结构清晰，避免冗长的句子；
        -保留文档的核心信息，避免遗漏关键细节；
        -文档的核心主题或目的；
        -涉及的关键方法、技术或流程；
        -主要结果或发现；
        -结论或建议；
        -长度在100字符内；

        文本：
        {text}

        中文摘要："""
        MAP_PROMPT = PromptTemplate(template=map_prompt_template, input_variables=["text"])

        # Reduce 提示词模板
        reduce_prompt_template = """请将以下多个中文摘要合并为一个完整的中文摘要，确保：
        -总分结构
            总：提炼所有摘要的核心主题或目的形成一句全文总结，且这句总结一定要包含文档的主体对象；
            分：保留每个摘要的核心信息，避免遗漏关键细节；
        -确保逻辑连贯，结构清晰，避免冗长的句子；
        -长度在500字符内。

        摘要列表：
        {text}

        合并后的中文摘要："""
        REDUCE_PROMPT = PromptTemplate(template=reduce_prompt_template, input_variables=["text"])

        # 设置摘要链
        chain = load_summarize_chain(
            langchain_llm,
            chain_type="map_reduce",
            map_prompt=MAP_PROMPT,
            combine_prompt=REDUCE_PROMPT,
            collapse_prompt=REDUCE_PROMPT,  # 递归压缩提示词
        )

        # 生成摘要并保留元数据
        summary = chain.run(split_documents)
        logging.info("中文摘要:", summary)
        logging.info("Metadata:", split_documents[0].metadata)  # 保留元数据

        # 创建langchain文档对象
        document = Document(page_content=summary, metadata=split_documents[0].metadata)
        # 将文档添加到向量数据库
        try:
            self.db.add_documents([document])
        except Exception as e:
            logging.error(f"文档的摘要 {file} 添加到向量存储时出错：{e}")
        logging.info(f"文档的摘要 {file} 添加到向量存储时成功。")

    def check_document_exists(self, file):
        """
        检查指定路径的文档是否已存在于向量存储中。

        :param file: 文档路径
        :return: 是否存在（True/False）
        """
        existing_docs = self.db.get(where={"source": file})
        return len(existing_docs["ids"]) > 0

    def get_documents(self):
        documents = self.db.get()
        metadatas = documents["metadatas"]
        documents_source = [metadata["source"] for metadata in metadatas]
        documents_source = list(set(documents_source))
        return documents_source

    def delete_documents(self, documents_source):
        result = []
        for document_source in documents_source:
            source_format = os.path.normpath(document_source)
            try:
                if source_format not in self.get_documents():
                    result.append(f"{source_format}不存在于向量存储中，无法删除")
                    continue
                self.db.delete(where={"source": source_format})
                result.append(f"{source_format}删除成功")
            except Exception as e:
                result.append(f"{source_format}删除失败，错误信息：{e}")
        return result


class ChromaService:
    # 初始化 Chroma 客户端
    client = chromadb.PersistentClient(path=resource_path(chroma_db))  # 指定持久化目录

    @classmethod
    def get_collections(cls):
        collections = cls.client.list_collections()
        return collections

    @classmethod
    def delete_collection(cls, collection_name):
        cls.client.delete_collection(collection_name)


if __name__ == "__main__":
    detail_service = VectorService("detail")
    queries = ["销售管理平台的要求",
               "吴催波的教育经历",
               "财务协同平台的要求",
               "量子计算的优势是什么"]
    for query in queries:
        results = detail_service.db.similarity_search_with_score(query)
        for i, (doc, score) in enumerate(results):
            print(f"\n===== 第 {i + 1} 个文档块（分数: {score:.3f}） =====")
            print("内容:", doc.page_content)  # 文本内容
            print("元数据:", doc.metadata["source"])  # 来源文件、页码等附加信息
            source = doc.metadata["source"]
