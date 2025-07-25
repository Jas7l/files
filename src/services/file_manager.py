import datetime
import json
import os
import shutil
from typing import Optional, List, Dict, Any, Union

from flask import request, send_file
from sqlalchemy.orm import Session as PGSession

from models.exception import ModuleException
from models.file import File


class FileManager:
    def __init__(
            self,
            pg_connection: PGSession,
            storage_path: str
    ):
        self._pg = pg_connection
        self._st = storage_path

    def sync_storage_and_db(self):
        # Get files from db
        print(self._st)
        with self._pg.begin():
            db_files = self._pg.query(File).all()
            db_files_path = {
                os.path.normpath(os.path.join(file.path, f"{file.name}.{file.extension}")): file for file in db_files
            }

            # Get files from system storage
            fs_files_path = {}
            for root, _, files in os.walk(self._st):
                for file in files:
                    full_path = os.path.normpath(os.path.join(root, file))
                    fs_files_path[full_path] = file

            # Delete files from DB if not on disk
            for path, file in db_files_path.items():
                if path not in fs_files_path:
                    self._pg.delete(file)

            # Add files to DB if on disk
            for path in fs_files_path:
                if path not in db_files_path:
                    dir_path, filename = os.path.split(path)
                    name, extension = os.path.splitext(filename)
                    extension = extension.lstrip('.')
                    size = os.path.getsize(path)

                    new_file = File(
                        name=name,
                        extension=extension,
                        size=size,
                        path=dir_path,
                        creation_date=datetime.datetime.utcnow(),
                        update_date=None,
                        comment=None
                    )
                    self._pg.add(new_file)

        # Delete empty directories
        for root, _, _ in os.walk(self._st, topdown=False):
            if not os.listdir(root) and os.path.abspath(root) != os.path.abspath(self._st):
                try:
                    os.rmdir(root)
                except OSError:
                    pass

    def get_all_files(self) -> List[Dict[str, Any]]:
        print(self._st)
        path = request.args.get("path")
        with self._pg.begin():
            query = self._pg.query(File)
            if path:
                query = query.filter(File.path.like(f"%{path}%"))
            files = query.all()
            return [file.dump() for file in files]

    def get_file_by_id(self, input_id: int, session: Optional[PGSession] = None) -> Union[Dict[str, Any] | File]:
        if session is None:
            with self._pg.begin():
                file = self._pg.query(File).get(input_id)

            if file is None:
                raise ModuleException("File not found", {"data": ""}, 400)
            return file.dump()

        file = session.query(File).get(input_id)
        return file

    def get_file_by_name(self, file_name: str) -> Dict[str, Any]:
        with self._pg.begin():
            try:
                name, extension = file_name.rsplit('.', 1)
            except ValueError:
                raise ModuleException()
            file = self._pg.query(File).filter(File.name == name, File.extension == extension).first()
            if not file:
                raise ModuleException("File not found", {"data": ""}, 400)
            return file.dump()

    def download_file(self, file_id: int):
        file = self.get_file_by_id(file_id)
        file_path = os.path.join(file.get("path"), f"{file.get('name')}.{file.get('extension')}")
        if not os.path.exists(file_path):
            raise ModuleException("File not found", {"data": ""}, 400)
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{file.get('name')}.{file.get('extension')}",
            mimetype="application/octet-stream"
        )

    def upload_file(self) -> Dict[str, Any]:
        raw_fields = request.form.get("fields")
        if not raw_fields:
            raise ModuleException("Missing form fields", {"data": ""}, 400)

        fields = json.loads(raw_fields)

        uploaded_file = request.files.get("attachment")
        if not uploaded_file:
            raise ModuleException("File not found", {"data": ""}, 400)

        relative_path = fields.get("path", "")

        relative_path = os.path.normpath(relative_path).lstrip(os.sep)
        full_storage_path = os.path.join(self._st, relative_path)
        filename = uploaded_file.filename

        name, extension = os.path.splitext(filename)
        extension = extension.lstrip('.')
        full_path = os.path.join(full_storage_path, filename)

        if os.path.exists(full_path):
            raise ModuleException("File already exists", {"data": ""}, 400)

        os.makedirs(full_storage_path, exist_ok=True)

        try:
            with open(full_path, 'wb') as f:
                shutil.copyfileobj(uploaded_file.stream, f)
        except Exception as e:
            raise ModuleException("Failed to write file", {"error": str(e)}, 500)

        try:
            size = os.path.getsize(full_path)
        except OSError:
            raise ModuleException("Failed to determine file size", {"data": ""}, 500)

        with self._pg.begin():
            db_file = File(
                name=name,
                extension=extension,
                size=size,
                path=full_storage_path,
                creation_date=datetime.datetime.utcnow(),
                update_date=None,
                comment=fields.get("comment", "")
            )

            self._pg.add(db_file)
            self._pg.flush()
            self._pg.refresh(db_file)

        return db_file.dump()

    def update_file(self, file_id) -> Dict[str, Any]:
        data = request.get_json()
        fields = data.get("fields", {})
        name = fields.get("name")
        path = fields.get("path")
        comment = fields.get("comment")
        if path:
            path = os.path.normpath(path)

        with self._pg.begin():
            file = self.get_file_by_id(file_id, session=self._pg)
            old_path = os.path.join(file.path, f"{file.name}.{file.extension}")

            if name:
                file.name = name
            if path:
                file.path = os.path.join(self._st, path)
            if comment:
                file.comment = comment

            new_full_path = os.path.join(file.path, f"{file.name}.{file.extension}")
            if old_path != new_full_path:
                os.makedirs(file.path, exist_ok=True)
                if not os.path.exists(old_path):
                    raise ModuleException("File not found", {"data": ""}, 400)
                os.rename(old_path, new_full_path)

            file.update_date = datetime.datetime.utcnow()
            self._pg.add(file)
            self._pg.flush()
            self._pg.refresh(file)
            return file.dump()

    def delete_file(self, file_id: int) -> Dict[str, Any]:
        with self._pg.begin():
            file = self.get_file_by_id(file_id, session=self._pg)
            full_path = os.path.join(file.path, f"{file.name}.{file.extension}")

            if os.path.exists(full_path):
                os.remove(full_path)

            self._pg.delete(file)
            return file.dump()
