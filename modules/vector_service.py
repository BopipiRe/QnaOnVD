from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from pathlib import Path
import doc_service as dcs
# from langchain_core.documents import Document
# from langchain_community.document_loaders import DirectoryLoader
#
# # 加载文档并附加元数据
# loader = DirectoryLoader("./data/", glob="**/*.txt")
# docs = loader.load()
#
# for doc in docs:
#     doc.metadata = {
#         "source": doc.metadata["source"],  # 文件路径
#         "timestamp": "2023-10-01"  # 自定义元数据
#     }

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",  # 指定模型名称
    base_url="http://localhost:11434"  # Ollama 服务地址（默认本地）
)

# 保存
def save_vector_store(textChunks, path):
    file_name = path.split('\\')[-1].split('.', 1)[0]
    if Path('faiss\\' + file_name + '-faiss').exists():
        print('Skipping ' + file_name + '-faiss')
        return
    db = FAISS.from_texts(textChunks, embeddings)
    db.save_local('faiss\\' + file_name + '-faiss')


# 保存
def save_vector_store_with_metadata(chunks, path):
    file_name = path.split('\\')[-1].split('.', 1)[0]
    if Path('faiss\\' + file_name + '-faiss').exists():
        print('Skipping ' + file_name + '-faiss')
        return
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local('faiss\\' + file_name + '-faiss')


# 加载
def load_vector_store(path):
    file_name = path.split('\\')[-1].split('.', 1)[0]
    return FAISS.load_local('faiss\\' + file_name + '-faiss', embeddings, allow_dangerous_deserialization=True)


# 将pdf切分块，嵌入和向量存储
def generate_vector_store(path):
    # raw_text = dcs.get_pdf_text(path)
    # text_chunks = dcs.get_text_chunks(raw_text)
    # save_vector_store(text_chunks, path)
    documents = dcs.get_pdf_text_with_metadata(path)
    chunks = dcs.split_documents_with_metadata(documents)
    save_vector_store_with_metadata(chunks, path)