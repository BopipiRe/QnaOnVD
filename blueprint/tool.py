from flasgger import swag_from
from flask import request, jsonify
from flask.blueprints import Blueprint

from service import ToolDB
from settings import schema

tool_bp = Blueprint('tool', __name__, url_prefix='/tool')


@tool_bp.route('', methods=['POST'])
@swag_from({
    'tags': ['工具管理'],
    'summary': '注册或更新工具',
    'description': '注册或更新一个工具',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': schema
        }
    ],
    'responses': {
        201: {
            'description': '工具注册成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'tool': schema
                }
            }
        },
        400: {
            'description': '工具注册失败',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def register_tool():
    tool_config = request.get_json()
    if not tool_config:
        return jsonify({"error": "请求体必须为 JSON 格式"}), 400
    try:
        ToolDB().save_tool(tool_config)
        return jsonify({"message": "工具注册成功", "tool": tool_config}), 201
    except Exception as e:
        return jsonify({"error": f"工具注册失败{str(e)}"}), 400


@tool_bp.route('', methods=['DELETE'])
@swag_from({
    'tags': ['工具管理'],
    'summary': '删除工具',
    'description': '根据名称删除一个工具',
    'parameters': [
        {
            'name': 'name',
            'in': 'query',
            'required': True,
            'type': 'string'
        }
    ],
    'responses': {
        200: {
            'description': '工具删除成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        400: {
            'description': '工具删除失败',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def delete_tool_api():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "缺少查询参数 'name'"}), 400
    try:
        ToolDB().delete_tool(name)
        return jsonify({"message": "工具删除成功"}), 200
    except Exception as e:
        return jsonify({"error": f"工具删除失败{str(e)}"}), 400


@tool_bp.route('', methods=['GET'])
@swag_from({
    'tags': ['工具管理'],
    'summary': '查找工具',
    'description': '根据类型查找工具',
    'parameters': [
        {
            'name': 'type',
            'in': 'query',
            'required': False,
            'type': 'string',
            'description': '为空时查询所有工具'
        }
    ],
    'responses': {
        200: {
            'description': '查找成功',
            'schema': {
                'type': 'array',
                'items': schema
            }
        }
    }
})
def find_tool_api():
    type = request.args.get('type')
    if not type:
        return jsonify(ToolDB().load_all_tools()), 200
    if type and type not in ["API", "SQL"]:
        return jsonify({"error": "查询参数 'type' 必须为 'API' 或 'SQL'"}), 400
    tools = ToolDB().load_tools_by_type(type)
    return jsonify(tools) if tools else jsonify({"message": "未找到符合条件的工具"}), 200
