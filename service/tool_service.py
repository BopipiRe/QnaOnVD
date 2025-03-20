import asyncio
import logging
import re

import httpx
import jsonschema
from jsonschema import validate

from settings import schema


class ToolService:
    tools = {}  # 存储工具名称的映射

    @staticmethod
    def _validate_json(data):
        """校验 JSON 数据是否符合 Schema"""
        try:
            validate(instance=data, schema=schema)
            logging.info("JSON 数据符合格式")
            return True
        except jsonschema.exceptions.ValidationError as e:
            logging.error(f"JSON 数据不符合格式: {str(e)}")
            return False

    @classmethod
    def _tool_router_by_name(cls, user_input: str):
        """基于工具名称匹配工具"""
        name = re.split(r'[:：]', user_input, 1)[0]
        if name in cls.tools:
            return cls.tools[name]
        return None

    @staticmethod
    async def _call_tool_api(url: str, params: dict, method='GET') -> dict:
        """调用工具API"""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.request(
                    method=method,
                    url=url,
                    json=params if method == "POST" else None,
                    params=params if method == "GET" else None,
                    timeout=None
                )
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

    @staticmethod
    def _parse_parameters(user_input: str, input_schema: dict) -> dict:
        """
        解析用户输入，根据 input_schema 提取参数。

        参数：
            user_input (str): 用户输入字符串。
            input_schema (dict): 工具的输入模式。

        返回：
            dict: 解析后的参数字典。
        """
        params = {}

        name, params_str = re.split(r'[:：]', user_input, 1)
        params_raw = re.split(r'[,，]', params_str)
        if len(input_schema) != len(params_raw):
            raise ValueError("参数数量不匹配")

        for index, key in enumerate(input_schema):
            # 从用户输入中提取参数值
            value = params_raw[index].strip()  # 提取值
            # 根据 schema 类型转换值
            if input_schema[key].get("type") == "integer":
                value = int(value)
            elif input_schema[key].get("type") == "number":
                value = float(value)
            params[key] = value
        return params

    @staticmethod
    def _format_tool_output(tool_config: dict, result: dict) -> str:
        """
        根据工具配置格式化 API 调用结果。

        参数：
            tool_config (dict): 工具配置。
            result (dict): API 调用结果。

        返回：
            str: 格式化后的输出字符串。
        """
        if "response_format" in tool_config:
            # 使用正则表达式提取所有占位符字段（如 {content} 和 {artifact}）
            placeholders = re.findall(r'{(.*?)}', tool_config['response_format'])

            # 动态构建格式化参数
            format_kwargs = {}
            for field in placeholders:
                format_kwargs[field] = result.get(field, "")  # 从 result 中获取值，默认为空字符串
            return tool_config["response_format"].format(**format_kwargs)
        else:
            # 默认返回 JSON 字符串
            return str(result)

    @classmethod
    def register_tool(cls, tool_config: dict):
        """注册工具"""
        # 参数校验逻辑
        if not cls._validate_json(tool_config):
            return False

        name = tool_config["name"]
        cls.tools[name] = tool_config
        return True

    @classmethod
    async def tool_invoke(cls, user_input: str):
        """工具调用主流程"""
        # 步骤1：判断是否需要调用工具
        tool_config = ToolService._tool_router_by_name(user_input)
    
        if tool_config:
            if re.search(r'[:：]', user_input):
                # 步骤2：参数解析
                params = cls._parse_parameters(user_input, tool_config["input_schema"])

                # 步骤3：执行API调用
                result = await cls._call_tool_api(
                    url=tool_config["url"],
                    method=tool_config["method"],
                    params=params
                )
                # 步骤4：格式化输出
                return cls._format_tool_output(tool_config, result)
            else:
                return "请提供参数，模式：\n"+str(tool_config['input_schema'])
        else:
            return None


if __name__ == '__main__':
    # 测试 GET 请求
    # 符合格式的 JSON 数据
    valid_data = {
        "name": "chat",
        "type": "API",
        "url": "http://127.0.0.1:5000/chat",
        "method": "GET",
        "description": "AI对话",
        "input_schema": {
            "query": {
                "type": "string"
            }
        }
    }

    ToolService.register_tool(valid_data)
    result = asyncio.run(ToolService.tool_invoke('chat:吴催波的教育经历'))
    print(type(result))