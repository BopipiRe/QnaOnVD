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
    if tool_config['name'] in ToolService.tools:
        return jsonify({"error": "工具名称已存在"}), 400
    # 调用 register_tool 方法
    if ToolService.register_tool(tool_config):
        return jsonify({"message": "工具注册成功", "tool": tool_config}), 201
    else:
        return jsonify({"error": "工具注册失败，JSON 数据不符合格式"}), 400

@tool_bp.route('/update', methods=['PUT'])
def update_tool_api():
    """更新工具API"""
    # 从请求中获取 JSON 数据
    tool_config = request.get_json()
    if not tool_config:
        return jsonify({"error": "请求体必须为 JSON 格式"}), 400
    if tool_config['name'] not in ToolService.tools:
        return jsonify({"error": "工具"+tool_config['name']+"不存在"}), 400
    # 调用 register_tool 方法
    if ToolService.register_tool(tool_config):
        return jsonify({"message": "工具更新成功", "tool": tool_config}), 201
    else:
        return jsonify({"error": "工具更新失败，JSON 数据不符合格式"}), 400

@tool_bp.route('/delete', methods=['DELETE'])
def delete_tool_api():
    """删除工具API"""
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "缺少查询参数 'name'"}), 400
    if ToolService.delete_tool(name):
        return jsonify({"message": "工具删除成功"}), 200
    else:
        return jsonify({"error": "工具删除失败，工具不存在"}), 400

@tool_bp.route('/find', methods=['GET'])
def find_tool_api():
    """查找工具API"""
    type = request.args.get('type')
    if not type:
        return jsonify({"error": "缺少查询参数 'type'"}), 400
    tools = ToolService.find_tool(type)
    return jsonify(tools) if tools else {"message": "未找到符合条件的工具"}, 200