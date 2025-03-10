from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 获取带有元数据的pdf文件内容
def get_pdf_text_with_metadata(pdf_path):
    documents = []
    pdf_reader = PdfReader(pdf_path)
    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": pdf_path,
                    "page": page_num + 1  # 页码从1开始
                }
            )
        )
    return documents

# 拆分带有元数据的文档
def split_documents_with_metadata(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n## ", "\n\n", "\n", "。", "！"]
    )
    chunks = text_splitter.split_documents(documents)  # 关键：使用 split_documents 而非 split_text
    return chunks


# 获取pdf文件内容
def get_pdf_text(pdf_path):
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        text += page.extract_text()

    return text

# 拆分文本
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        # chunk_size=768,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks