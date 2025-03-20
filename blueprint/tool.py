from flask import request, jsonify
from flask.blueprints import Blueprint

from service.tool_service import ToolService

tool_bp = Blueprint('tool', __name__, url_prefix='/tool')

@tool_bp.route('/register', methods=['POST'])
def register_tool_api():
    """注册工具API"""
    # 从请求中获取 JSON 数据
    tool_config = request.get_json()
    if not tool_config:
        return jsonify({"error": "请求体必须为 JSON 格式"}), 400
    # 调用 register_tool 方法
    if ToolService.register_tool(tool_config):
        print(ToolService.tools)
        return jsonify({"message": "工具注册成功", "tool": tool_config}), 201
    else:
        return jsonify({"error": "工具注册失败，JSON 数据不符合格式"}), 400
