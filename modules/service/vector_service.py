from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings

from modules import resource_path
from modules.utils import DocUtil


class VectorService:
    def __init__(self, collection_name="test", persist_directory=resource_path("chroma_db"), model="nomic-embed-text",
                 base_url="http://localhost:11434"):
        """
        初始化向量存储管理器。

        :param collection_name: 集合名称
        :param persist_directory: 持久化存储目录
        :param model: Ollama 嵌入模型名称
        :param base_url: Ollama 服务地址
        """
        self.embeddings = OllamaEmbeddings(
            model=model,
            base_url=base_url
        )
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory,
            collection_metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )

    def generate_vector_store(self, path):
        """
        将指定路径的文档（PDF 或 DOCX）切分、嵌入并存储到向量数据库中。

        :param path: 文档路径
        """
        self.vector_store.add_documents(DocUtil.process_file(path))
        print(f"文档 {path} 已成功添加到向量存储中。")

    def delete_vector_store(self, path):
        """
        从向量存储中删除指定路径的文档。

        :param path: 文档路径
        """
        self.vector_store.delete(where={"source": path})
        print(f"文档 {path} 已从向量存储中删除。")

    def check_document_exists(self, path):
        """
        检查指定路径的文档是否已存在于向量存储中。

        :param path: 文档路径
        :return: 是否存在（True/False）
        """
        existing_docs = self.vector_store.get(where={"source": path})
        return len(existing_docs["ids"]) > 0