from flasgger import swag_from
from flask import request, jsonify
from flask.blueprints import Blueprint
from service.tool_service import ToolService
from settings import schema

tool_bp = Blueprint('tool', __name__, url_prefix='/tool')

@tool_bp.route('', methods=['POST'])
@swag_from({
    'tags': ['工具管理'],
    'summary': '注册工具',
    'description': '注册一个新的工具',
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
def register_tool_api():
    tool_config = request.get_json()
    if not tool_config:
        return jsonify({"error": "请求体必须为 JSON 格式"}), 400
    if tool_config['name'] in ToolService.tools:
        return jsonify({"error": "工具名称已存在"}), 400
    if ToolService.register_tool(tool_config):
        return jsonify({"message": "工具注册成功", "tool": tool_config}), 201
    else:
        return jsonify({"error": "工具注册失败，JSON 数据不符合格式"}), 400

@tool_bp.route('', methods=['PUT'])
@swag_from({
    'tags': ['工具管理'],
    'summary': '更新工具',
    'description': '更新一个已存在的工具',
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
            'description': '工具更新成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'tool': schema
                }
            }
        },
        400: {
            'description': '工具更新失败',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def update_tool_api():
    tool_config = request.get_json()
    if not tool_config:
        return jsonify({"error": "请求体必须为 JSON 格式"}), 400
    if tool_config['name'] not in ToolService.tools:
        return jsonify({"error": f"工具 {tool_config['name']} 不存在"}), 400
    if ToolService.register_tool(tool_config):
        return jsonify({"message": "工具更新成功", "tool": tool_config}), 201
    else:
        return jsonify({"error": "工具更新失败，JSON 数据不符合格式"}), 400

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
    if ToolService.delete_tool(name):
        return jsonify({"message": "工具删除成功"}), 200
    else:
        return jsonify({"error": "工具删除失败，工具不存在"}), 400

@tool_bp.route('', methods=['GET'])
@swag_from({
    'tags': ['工具管理'],
    'summary': '查找工具',
    'description': '根据类型查找工具',
    'parameters': [
        {
            'name': 'type',
            'in': 'query',
            'required': True,
            'type': 'string'
        }
    ],
    'responses': {
        200: {
            'description': '查找成功',
            'schema': {
                'type': 'array',
                'items': schema
            }
        },
        400: {
            'description': '查找失败',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def find_tool_api():
    type = request.args.get('type')
    if not type:
        return jsonify({"error": "缺少查询参数 'type'"}), 400
    tools = ToolService.find_tool(type)
    return jsonify(tools) if tools else jsonify({"message": "未找到符合条件的工具"}), 200