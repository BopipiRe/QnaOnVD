from functools import wraps

from flask import request, jsonify

from service import ChromaService


def validate_collection_name(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 检查请求中是否有 collection_name 字段
        if 'collection_name' in kwargs:
            collection_name = kwargs['collection_name']
        else:
            collection_name = request.args.get('collection_name')
        if not collection_name:
            return jsonify({"error": "Missing 'collection_name' field"}), 400
        # 检查 collection_name 是否存在于 ChromaService.collections 中
        if collection_name not in ChromaService.get_collections():
            return jsonify({"error": f"Collection '{collection_name}' does not exist"}), 404

        return func(*args, **kwargs)

    return wrapper

