from vector_service import load_vector_store,generate_vector_store
import chat_service as chs

if __name__ == '__main__':
    path = 'doc\\xs.pdf'
    generate_vector_store(path)
    vector_store = load_vector_store(path)
    chain = chs.get_qa_chain(vector_store)

    while True:
        question = input("\n用户提问（输入q退出）: ")
        if question == "":
            continue
        elif question == "q":
            break
        result = chain.invoke({"query": question})  # 注意输入键应为 "query"

        print(result['result'])
        print("来源文档:", *[source_doc.metadata for source_doc in result["source_documents"]])  # 如果设置了
        # return_source_documents=True