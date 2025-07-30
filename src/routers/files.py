from threading import Thread

from flask import Blueprint, jsonify

from injectors import services

file_bp = Blueprint("file", __name__, url_prefix="/api/")


@file_bp.route("/files/sync", methods=["POST"])
def sync_files():
    fs = services.file_service()
    thread = Thread(target=fs.sync_storage_and_db())
    thread.start()
    return jsonify({"detail": "Sync started in background"})


# Для фильтрации по пути хранения files?path=my_path
@file_bp.route("/files", methods=["GET"])
def get_files():
    fs = services.file_service()
    files = fs.get_all_files()
    if not files:
        return jsonify(status_code=404, detail="No files found")
    return jsonify(files)


@file_bp.route("/file/<int:file_id>", methods=["GET"])
def get_file(file_id):
    fs = services.file_service()
    file = fs.get_file_by_id(file_id)
    return jsonify(file)


@file_bp.route("/file/<int:file_id>/download", methods=["GET"])
def download_file(file_id):
    fs = services.file_service()
    return fs.download_file(file_id)


@file_bp.route("/file", methods=["POST"])
def upload_file():
    fs = services.file_service()
    file = fs.upload_file()
    return jsonify(file)


@file_bp.route("/file/<int:file_id>", methods=["PATCH"])
def update_file(file_id):
    fs = services.file_service()
    file = fs.update_file(file_id)
    return jsonify(file)


@file_bp.route("/file/<int:file_id>", methods=["DELETE"])
def delete_file(file_id: int):
    fs = services.file_service()
    file = fs.delete_file(file_id)
    return jsonify(file)
