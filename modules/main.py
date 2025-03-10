from vector_service import generate_vector_store,vector_store,delete_vector_store
import chat_service as chs

if __name__ == '__main__':
    path = 'doc\\cw.pdf'
    generate_vector_store(path)
    # results = vector_store.similarity_search(
    #     "项目名称是什么",
    #     k=2,
    # )
    # for res in results:
    #     print(f"* {res.page_content} [{res.metadata}]")

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