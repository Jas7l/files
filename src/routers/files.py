from threading import Thread

from flask import Blueprint, jsonify
from injectors import services

file_bp = Blueprint('file', __name__, url_prefix='/api/files')


@file_bp.route('/sync', methods=['POST'])
def sync_files():
    """Синхронизация локального хранилища и базы данных"""

    fs = services.files_service()
    thread = Thread(target=fs.sync_storage_and_db())
    thread.start()
    return jsonify({'detail': 'Sync started in background'})


@file_bp.route('', methods=['GET'])
def get_files():
    """Получение списка файлов"""

    fs = services.files_service()
    files = fs.get_files()
    if not files:
        return jsonify(status_code=404, detail='No files found')
    return jsonify(files)


@file_bp.route('/<int:file_id>', methods=['GET'])
def get_file(file_id):
    """Получение файла по id"""

    fs = services.files_service()
    file = fs.get_file_by_id(file_id)
    return jsonify(file)


@file_bp.route('/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    """Скачивание файла по id"""

    fs = services.files_service()
    return fs.download_file(file_id)


@file_bp.route('', methods=['POST'])
def upload_file():
    """Загрузка файла и добавление записи в БД"""

    fs = services.files_service()
    file = fs.upload_file()
    return jsonify(file)


@file_bp.route('/<int:file_id>', methods=['PATCH'])
def update_file(file_id):
    """Обновление файла и его записи в БД"""

    fs = services.files_service()
    file = fs.update_file(file_id)
    return jsonify(file)


@file_bp.route('/<int:file_id>', methods=['DELETE'])
def delete_file(file_id: int):
    """Удаление файла из хранилища и записи о нём в БД"""

    fs = services.files_service()
    file = fs.delete_file(file_id)
    return jsonify(file)
