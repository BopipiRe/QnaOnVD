import asyncio

from flasgger import Swagger
from flask import Flask, jsonify
from flask import request

from blueprint import tool_bp, chroma_bp
from service import ChatService, VectorService, ToolService, ChromaService
from settings import chroma_db

# 用当前脚本名称实例化Flask对象，方便flask从该脚本文件中获取需要的内容
app = Flask(__name__)
Swagger(app)

#程序实例需要知道每个url请求所对应的运行代码是谁。
#所以程序中必须要创建一个url请求地址到python运行函数的一个映射。
#处理url和视图函数之间的关系的程序就是"路由"，在Flask中，路由是通过@app.route装饰器(以@开头)来表示的
#url映射的函数，要传参则在上述route（路由）中添加参数申明
@app.route("/chat")
def chat():
    """
    综合查询接口 - 支持工具调用与向量检索
    ---
    tags:
    - chat
    parameters:
      - name: query
        in: query
        type: string
        required: true
        description: 查询内容（支持自然语言指令或工具调用指令）
        example: "查询工具"
      - name: collection_name
        in: query
        type: string
        required: False
        description: 知识库名称
        default: "default"
    responses:
      200:
        description: 成功响应（根据查询类型返回不同结构）
        schema:
          oneOf:
            - type: array
              items:
                type: string
              example: ["tool1", "tool2"]
            - type: object
              properties:
                result:
                  type: string
                  description: 格式化后的查询结果
                  example: "以下是可用工具列表..."
      400:
        description: 参数错误
        schema:
          type: object
          properties:
            error:
              type: string
              example: "缺少查询参数 'query'"
      500:
        description: 服务端错误
        schema:
          type: object
          properties:
            error:
              type: string
              example: "数据库连接失败"
    """
    # 从查询参数中获取 query
    query = request.args.get("query")
    collection_name = request.args.get("collection_name") if request.args.get("collection_name") else "default"
    if not query:
        return {"error": "缺少查询参数 'query'"}, 400
    if collection_name not in ChromaService.get_collections():
        return {"error": "知识库不存在"}, 400
    try:
        if query == '查询工具':
            tools_name = [tool['name'] for tool in ToolService.tools.values()]
            return tools_name if tools_name else '暂无工具'
        # 判断是否调用工具，若需要调用则解析query并返回调用结果（格式化后）
        tool_res = asyncio.run(ToolService.tool_invoke(query))
        if tool_res:
            return tool_res
        db = VectorService(persist_directory=chroma_db, collection_name=collection_name).db
        chat_service = ChatService(vector_store=db)
        result = chat_service.invoke(query)
        return jsonify(result)
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/test")
def test():
    """
    测试API
    ---
    tags:
    - chat
    parameters:
      - name: input1
        in: query
        type: string
        required: true
      - name: input2
        in: query
        type: string
        required: true
    responses:
      200:
        description: 成功响应（根据查询类型返回不同结构）
        schema:
          type: object
          properties:
            output1:
              type: string
            output2:
              type: string
    """
    kwarg = request.args
    input1 = kwarg.get('input1')
    input2 = kwarg.get('input2')
    return {"output1": input1, "output2": input2}

app.register_blueprint(chroma_bp)
app.register_blueprint(tool_bp)

if __name__ == '__main__':
    app.run(debug=True) # 多进程 生产：gunicorn -w 4 myapp:app 开发：app.run(processes=N)

