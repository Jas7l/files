from threading import Thread

from flask import Blueprint, jsonify
from flask import g
from injectors import services
from routers.auth import token_required

file_bp = Blueprint('file', __name__, url_prefix='/api/files')


@file_bp.route('/sync', methods=['POST'])
@token_required
def sync_files():
    """Синхронизация локального хранилища и базы данных"""

    user_id = g.user.id
    fs = services.user_files_service(user_id=user_id)
    thread = Thread(target=fs.sync_storage_and_db)
    thread.start()
    return jsonify({'detail': 'Sync started in background'})


@file_bp.route('', methods=['GET'])
@token_required
def get_files():
    """Получение списка файлов"""

    user_id = g.user.id
    fs = services.user_files_service(user_id=user_id)
    files = fs.get_files()
    if not files:
        return jsonify(status_code=404, detail='No files found')
    return jsonify(files)


@file_bp.route('/<int:file_id>', methods=['GET'])
@token_required
def get_file(file_id):
    """Получение файла по id"""

    user_id = g.user.id
    fs = services.user_files_service(user_id=user_id)
    file = fs.get_file_by_id(file_id)
    return jsonify(file)


@file_bp.route('/<int:file_id>/download', methods=['GET'])
@token_required
def download_file(file_id):
    """Скачивание файла по id"""

    user_id = g.user.id
    fs = services.user_files_service(user_id=user_id)
    return fs.download_file(file_id)


@file_bp.route('', methods=['POST'])
@token_required
def upload_file():
    """Загрузка файла и добавление записи в БД"""

    user_id = g.user.id
    fs = services.user_files_service(user_id=user_id)
    file = fs.upload_file()
    return jsonify(file)


@file_bp.route('/<int:file_id>', methods=['PATCH'])
@token_required
def update_file(file_id):
    """Обновление файла и его записи в БД"""

    user_id = g.user.id
    fs = services.user_files_service(user_id=user_id)
    file = fs.update_file(file_id)
    return jsonify(file)


@file_bp.route('/<int:file_id>', methods=['DELETE'])
@token_required
def delete_file(file_id: int):
    """Удаление файла из хранилища и записи о нём в БД"""

    user_id = g.user.id
    fs = services.user_files_service(user_id=user_id)
    file = fs.delete_file(file_id)
    return jsonify(file)
