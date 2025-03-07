from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import doc_service as dcs

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",  # 指定模型名称
    base_url="http://localhost:11434"  # Ollama 服务地址（默认本地）
)

# 保存
def save_vector_store(textChunks):
    db = FAISS.from_texts(textChunks, embeddings)
    # HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")
    db.save_local('faiss')


# 加载
def load_vector_store():
    return FAISS.load_local('faiss', embeddings, allow_dangerous_deserialization=True)


# 将pdf切分块，嵌入和向量存储
def generate_vector_store(path):
    raw_text = dcs.get_pdf_text(path)
    text_chunks = dcs.get_text_chunks(raw_text)
    save_vector_store(text_chunks)
