import os.path
import shutil
import uuid

from flask import Blueprint, jsonify, request
from zipp.compat.overlay import zipfile

from service import VectorService, ChromaService

chroma_bp = Blueprint('chroma', __name__, url_prefix='/chroma')


@chroma_bp.route('/collections', methods=['GET'])
def get_collections():
    """获取知识库列表"""
    try:
        return ChromaService.get_collections()
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chroma_bp.route('/collections/delete', methods=['DELETE'])
def delete_collection():
    """删除知识库"""
    collection_name = request.args.get('collection_name')
    if not collection_name:
        return jsonify({'error': '参数collection_name缺失'}), 400
    try:
        ChromaService.delete_collection(collection_name)  # 删除知识库
        if os.path.exists(os.path.join('resources', collection_name)):
            shutil.rmtree(os.path.join('resources', collection_name))  # 删除知识库对应的文件夹
        return jsonify({'message': '知识库删除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chroma_bp.route('/collections/<collection_name>/get', methods=['GET'])
def get_documents(collection_name):
    """获取知识库中的文档列表"""
    try:
        if collection_name not in ChromaService.get_collections():
            return jsonify({'error': '没有找到知识库' + collection_name}), 404
        documents_name = VectorService(collection_name=collection_name).get_documents()
        return documents_name
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chroma_bp.route('/collections/<collection_name>/add', methods=['POST'])
def add_documents(collection_name):
    # 检查是否有文件上传
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

        return jsonify({'message': message})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chroma_bp.route('/collections/<collection_name>/update', methods=['POST'])
def update_document(collection_name):
    # 检查是否有文件上传
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
            vector_service.delete_document([filename])
            old_file_path = os.path.join("resources", collection_name, filename)
            os.rename(old_file_path, os.path.join(old_file_path, '.bak')) if os.path.exists(old_file_path) else None
        uploaded_file.save(filename)
        res = vector_service.file_index(filename)
        if res == '文件索引成功':
            shutil.move(filename, os.path.join("resources", collection_name, filename))
            os.remove(os.path.join("resources", collection_name, filename, '.bak')) if os.path.exists(
                os.path.join("resources", collection_name, filename, '.bak')) else None

        return jsonify({'message': res})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chroma_bp.route('/collections/<collection_name>/delete', methods=['DELETE'])
def delete_documents(collection_name):
    documents_source = request.args.getlist('documents_source')
    if not documents_source:
        return jsonify({'error': '参数documents_source缺失'}), 400
    try:
        if collection_name not in ChromaService.get_collections():
            return jsonify({'error': '没有找到知识库' + collection_name}), 404
        message = VectorService(collection_name=collection_name).delete_documents(documents_source)
        return jsonify({'message': message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
