import asyncio

from flask import Flask
from flask import request

from blueprint import tool_bp, chroma_bp
from service import ChatService, VectorService
from service.tool_service import ToolService
from settings import resource_path, chroma_db

# 用当前脚本名称实例化Flask对象，方便flask从该脚本文件中获取需要的内容
app = Flask(__name__)

#程序实例需要知道每个url请求所对应的运行代码是谁。
#所以程序中必须要创建一个url请求地址到python运行函数的一个映射。
#处理url和视图函数之间的关系的程序就是"路由"，在Flask中，路由是通过@app.route装饰器(以@开头)来表示的
#url映射的函数，要传参则在上述route（路由）中添加参数申明
@app.route("/chat")
def chat():
    """聊天APPI"""
    # 从查询参数中获取 query
    query = request.args.get("query")
    if not query:
        return {"error": "缺少查询参数 'query'"}, 400
    try:
        if query == '查询工具':
            tools_name = [tool['name'] for tool in ToolService.tools.values()]
            return tools_name if tools_name else '暂无工具'
        # 判断是否调用工具，若需要调用则解析query并返回调用结果（格式化后）
        tool_res = asyncio.run(ToolService.tool_invoke(query))
        if tool_res:
            return tool_res
        db = VectorService(persist_directory=resource_path(chroma_db)).db
        doc_chain = ChatService().get_qa_chain(db)
        result = doc_chain.invoke({"query": query})
        return result['result']
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/test")
def test():
    """测试API"""
    kwarg = request.args
    input1 = kwarg.get('input1')
    input2 = kwarg.get('input2')
    return {"output1": input1, "output2": input2}

app.register_blueprint(chroma_bp)
app.register_blueprint(tool_bp)

app.run(debug=True)

