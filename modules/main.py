import os

from modules import resource_path
from modules.service import VectorService, ChatService

vector_service = VectorService(persist_directory=resource_path('chroma_db'))

def add_db(path=resource_path('doc')):
    for file in os.listdir(path):
        vector_service.file_detail_index(os.path.join(path, file))


if __name__ == '__main__':
    # add_db()
    chain = ChatService().get_qa_chain(vector_service.db)

    while True:
        question = input("\n用户提问（输入q退出）: ")
        if question == "":
            continue
        elif question == "q":
            break
        result = chain.invoke({"query": question})  # 注意输入键应为 "query"

        print(result['output_text'])# 输出答案和得分
        print("来源文档:", *[source_doc.metadata for source_doc in result["source_documents"]])  # 如果设置了
        # return_source_documents=True