from inspect import Signature, Parameter
from typing import Any, Callable

import httpx
from mcp.server.fastmcp import FastMCP

from tool_db import ToolDB

mcp = FastMCP("mcp")

TYPE_MAPPING = {
    "string": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
    "any": Any  # 任意类型
}


def parse_type(type_str: str):
    """将JSON中的类型字符串转换为Python类型"""
    return TYPE_MAPPING.get(type_str.lower(), Any)


def create_api_function(config) -> Callable:
    method = config['method']
    url = config['url']
    # 收集所有参数信息
    parameters = []

    params = config.get("input_schema")
    # 查询参数 (通常为可选参数)
    for param, param_config in params.items():
        parameters.append(
            Parameter(param, Parameter.POSITIONAL_OR_KEYWORD,
                      annotation=parse_type(param_config.get("type", "any")),
                      default=... if param_config.get('required') else None)
        )

    # 创建签名对象
    sig = Signature(parameters)

    # 创建函数
    async def api_function(*args, **kwargs):
        # 绑定参数到签名
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        print(bound_args.arguments)
        # 原有的API请求逻辑
        async with httpx.AsyncClient() as client:
            try:
                # 设置合理的超时时间
                timeout = httpx.Timeout(connect=10, read=30, write=5.0, pool=2.0)

                # 根据方法选择参数传递方式
                request_kwargs = {
                    "method": method,
                    "url": url,
                    "timeout": timeout,
                }
                if method == "GET":
                    request_kwargs["params"] = bound_args.arguments
                elif method in ["POST", "PUT", "PATCH", "DELETE"]:
                    request_kwargs["json"] = bound_args.arguments

                # 发送请求
                resp = await client.request(**request_kwargs)
                # 根据 Content-Type 解析响应内容
                content_type = resp.headers.get("content-type", "")
                if "application/json" in content_type:
                    return resp.json()
                elif "text/plain" in content_type or "text/html" in content_type:
                    return resp.text
                else:
                    return {"error": f"不支持的 Content-Type: {content_type}"}
            except Exception as e:
                return {"error": f"API调用失败: {str(e)}"}

    api_function.__signature__ = sig
    api_function.__name__ = config.get('name', 'dynamic_api_function')

    return api_function


db = ToolDB()  # "../resources/tools.db"
for config in db.load_all_tools():
    mcp.tool(name=config["name"], description=config["description"])(create_api_function(config))

if __name__ == "__main__":
    mcp.run(transport='stdio')  # 默认使用 stdio 传输
