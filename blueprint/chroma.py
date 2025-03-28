import os.path
import shutil
import uuid

from flask import Blueprint, jsonify, request
from zipp.compat.overlay import zipfile

from service import VectorService, ChromaService
from utils import validate_collection_name

chroma_bp = Blueprint('chroma', __name__, url_prefix='/chroma')


@chroma_bp.route('/collections', methods=['GET'])
def get_collections():
    """
    获取知识库列表
    ---
    tags:
    - Chroma
    responses:
      200:
        description: 获取知识库列表
        schema:
          type: array
          items:
            type: string
          example: ["collection1", "collection2"]
      500:
        description: 服务器内部错误
        schema:
          type: object
          properties:
            error:
              type: string
              example: "服务器内部错误"
    """
    try:
        return ChromaService.get_collections(), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chroma_bp.route('/collections', methods=['DELETE'])
@validate_collection_name
def delete_collection():
    """
    删除指定知识库
    ---
    tags:
      - Chroma
    parameters:
      - name: collection_name
        in: query
        type: string
        required: true
        description: 要删除的知识库名称
    responses:
      200:
        description: 删除成功
        schema:
          type: object
          properties:
            message:
              type: string
              example: "知识库删除成功"
      400:
        description: 参数缺失
        schema:
          type: object
          properties:
            error:
              type: string
              example: "参数collection_name缺失"
      500:
        description: 服务器内部错误
        schema:
          type: object
          properties:
            error:
              type: string
              example: "删除操作失败"
    """
    collection_name = request.args.get('collection_name')
    try:
        ChromaService.delete_collection(collection_name)  # 删除知识库
        if os.path.exists(os.path.join('resources', collection_name)):
            shutil.rmtree(os.path.join('resources', collection_name))  # 删除知识库对应的文件夹
        return jsonify({'message': '知识库删除成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chroma_bp.route('/collections/<collection_name>', methods=['GET'])
@validate_collection_name
def get_documents(collection_name):
    """
    获取知识库中的文档列表
    ---
    tags:
      - Chroma
    parameters:
      - name: collection_name
        in: path
        type: string
        required: true
        description: 知识库名称
        default: default
    responses:
      200:
        description: 文档列表
        schema:
          type: array
          items:
            type: string
          example: ["doc1.pdf", "doc2.txt"]
      404:
        description: 知识库不存在
        schema:
          type: object
          properties:
            error:
              type: string
              example: "没有找到知识库test_collection"
      500:
        description: 服务器内部错误
        schema:
          type: object
          properties:
            error:
              type: string
              example: "获取文档列表失败"
    """
    try:
        documents_name = VectorService(collection_name=collection_name).get_documents()
        return documents_name, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chroma_bp.route('/collections/<collection_name>', methods=['POST'])
def add_documents(collection_name):
    """
    上传文件到知识库
    ---
    tags:
      - Chroma
    parameters:
      - name: collection_name
        in: path
        type: string
        required: true
        description: 目标知识库名称
        default: default
      - name: file
        in: formData
        type: file
        required: true
        description: 要上传的文件（支持zip/pdf/docx/txt）
    consumes:
      - multipart/form-data
    responses:
      200:
        description: 上传结果
        schema:
          type: object
          properties:
            message:
              type: array
              items:
                type: string
              example: ["file1.pdf: 文件索引成功", "file2.txt: 不支持的文件类型"]
      400:
        description: 无效请求
        schema:
          type: object
          properties:
            error:
              type: string
              example: "未上传文件"
      500:
        description: 服务器内部错误
        schema:
          type: object
          properties:
            error:
              type: string
              example: "文件处理失败"
    """
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400

    uploaded_file = request.files['file']
    filename = uploaded_file.filename

    # 检查文件类型
    file_ext = os.path.splitext(filename)[-1].lower()
    if file_ext not in ['.zip', '.pdf', '.docx', '.txt']:
        return jsonify({'error': '不支持的文件类型'}), 400

    try:
        message = []
        if not os.path.exists(os.path.join("resources", collection_name)):
            os.makedirs(os.path.join("resources", collection_name))
        if file_ext == '.zip':
            # 处理 ZIP 文件
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                # 解压 ZIP 文件到临时目录
                temp_dir = str(uuid.uuid4())  # 临时解压目录
                os.makedirs(temp_dir, exist_ok=True)
                zip_ref.extractall(temp_dir)

                # 遍历解压后的文件
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    if os.path.splitext(file)[-1].lower() in ['.pdf', '.docx', '.txt']:
                        shutil.move(file_path, file)
                        res = VectorService(collection_name=collection_name).file_index(file)
                        shutil.move(file, os.path.join("resources", collection_name, file))
                        message.append(f"{file}: {res}")
                    else:
                        message.append(f"{file}: 不支持的文件类型")

                shutil.rmtree(temp_dir)  # 删除临时目录

        else:
            # 处理单文件
            uploaded_file.save(filename)
            res = VectorService(collection_name=collection_name).file_index(filename)
            shutil.move(filename, os.path.join("resources", collection_name, filename))
            message = f"{filename}: {res}"

        return jsonify({'message': message}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chroma_bp.route('/collections/<collection_name>', methods=['PUT'])
@validate_collection_name
def update_document(collection_name):
    """
    更新知识库中的文档
    ---
    tags:
      - Chroma
    parameters:
      - name: collection_name
        in: path
        type: string
        required: true
        description: 知识库名称
        default: default
      - name: file
        in: formData
        type: file
        required: true
        description: 要更新的文件（支持pdf/docx/txt）
    consumes:
      - multipart/form-data
    responses:
      200:
        description: 更新结果
        schema:
          type: object
          properties:
            message:
              type: string
              example: "文件更新成功"
      400:
        description: 无效请求
        schema:
          type: object
          properties:
            error:
              type: string
              example: "不支持的文件类型"
      404:
        description: 知识库不存在
        schema:
          type: object
          properties:
            error:
              type: string
              example: "没有找到知识库test_collection"
      500:
        description: 服务器内部错误
        schema:
          type: object
          properties:
            error:
              type: string
              example: "文件更新失败"
    """
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400
    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    # 检查文件类型
    file_ext = os.path.splitext(filename)[-1].lower()
    if file_ext not in ['.pdf', '.docx', '.txt']:
        return jsonify({'error': '不支持的文件类型'}), 400
    try:
        if not os.path.exists(os.path.join("resources", collection_name)):
            return jsonify({'error': '没有找到知识库' + collection_name}), 404
        vector_service = VectorService(collection_name=collection_name)
        # 处理单文件
        if filename in vector_service.get_documents():
            vector_service.delete_documents([filename])
            file = os.path.join("resources", collection_name, filename)
            os.remove(file) if os.path.exists(file) else None
        uploaded_file.save(filename)
        res = vector_service.file_index(filename)
        if res == '文件索引成功':
            shutil.move(filename, os.path.join("resources", collection_name, filename))
            os.remove(os.path.join("resources", collection_name, filename, '.bak')) if os.path.exists(
                os.path.join("resources", collection_name, filename, '.bak')) else None

        return jsonify({'message': res}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chroma_bp.route('/collections/<collection_name>', methods=['DELETE'])
@validate_collection_name
def delete_documents(collection_name):
    """
    删除知识库中的文档
    ---
    tags:
      - Chroma
    parameters:
      - name: collection_name
        in: path
        type: string
        required: true
        description: 知识库名称
        default: default
      - name: documents_source
        in: query
        type: array
        items:
          type: string
        required: true
        collectionFormat: multi
        description: 要删除的文档名称列表
    responses:
      200:
        description: 删除结果
        schema:
          type: object
          properties:
            message:
              type: string
              example: "文档删除成功"
      400:
        description: 参数缺失
        schema:
          type: object
          properties:
            error:
              type: string
              example: "参数documents_source缺失"
      404:
        description: 知识库不存在
        schema:
          type: object
          properties:
            error:
              type: string
              example: "没有找到知识库test_collection"
      500:
        description: 服务器内部错误
        schema:
          type: object
          properties:
            error:
              type: string
              example: "文档删除失败"
    """
    documents_source = request.args.getlist('documents_source')
    if not documents_source:
        return jsonify({'error': '参数documents_source缺失'}), 400
    try:
        message = VectorService(collection_name=collection_name).delete_documents(documents_source)
        for source in documents_source:
            file = os.path.join("resources", collection_name, source)
            if os.path.exists(file):
                os.remove(file)
        return jsonify({'message': message}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
