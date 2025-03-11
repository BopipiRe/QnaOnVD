from langchain_community.embeddings import OllamaEmbeddings
from pathlib import Path
import doc_service as dcs
from langchain_chroma import Chroma

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",  # 指定模型名称
    base_url="http://localhost:11434"  # Ollama 服务地址（默认本地）
)

vector_store = Chroma(
    collection_name="test",
    embedding_function=embeddings,
    persist_directory="../chroma_db",
    collection_metadata={"hnsw:space": "cosine"}  # 余弦相似度计算
)


# 将pdf切分块，嵌入和向量存储
def generate_vector_store(path):
    # TODO:增量更新
    # delete_vector_store(path)
    # if vector_store.get(where={"source":path}):
    #     print("Already exists")
    #     return
    doc_format = path.split('.')[-1]
    documents = []
    if doc_format == 'pdf':
        documents = dcs.get_pdf_text_with_metadata(path)
    elif doc_format == 'docx':
        documents = dcs.get_docx_text_with_metadata(path)
    chunks = dcs.split_documents_with_metadata(documents)
    vector_store.add_documents(chunks)


def delete_vector_store(path):
    vector_store.delete(where={"source":path})