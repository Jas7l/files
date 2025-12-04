import datetime
import json
import os
import shutil
from typing import Optional, List, Dict, Any, Union

from base_module.models import ModuleException
from base_module.models.logger import ClassesLoggerAdapter
from config import config
from flask import request, send_file
from models.file import File
from sqlalchemy.orm import Session as PGSession
from werkzeug.utils import secure_filename


class FilesService:
    """Сервис работы с файлами"""

    def __init__(self, pg_connection: PGSession, user_id: int | None = None):
        self._pg = pg_connection
        self._user_id = user_id
        self._logger = ClassesLoggerAdapter.create(self)
        base_path = config.storage_path
        if self._user_id is not None:
            self._st = os.path.join(base_path, str(self._user_id))
        else:
            self._st = base_path
        os.makedirs(self._st, exist_ok=True)

    def sync_storage_and_db(self):
        """Глобальная синхронизация хранилища и БД"""

        local_files = {}
        for root, _, files in os.walk(config.storage_path):
            for filename in files:
                full_path = os.path.normpath(os.path.join(root, filename))
                dir_path, fname = os.path.split(full_path)
                name, extension = os.path.splitext(fname)
                extension = extension.lstrip('.')

                try:
                    relative_parts = os.path.relpath(
                        dir_path, config.storage_path
                    ).split(os.sep)
                    owner_id = int(relative_parts[0])
                    relative_path = (
                        os.path.join(*relative_parts[1:])
                        if len(relative_parts) > 1 else ''
                    )
                except (ValueError, IndexError):
                    owner_id = None
                    relative_path = os.path.relpath(
                        dir_path, config.storage_path
                    )

                key = (owner_id, relative_path, name, extension)
                local_files[key] = full_path

        with self._pg.begin():
            db_files = self._pg.query(File).all()
            db_files_map = {
                (f.owner_id, f.relative_path, f.name, f.extension): f
                for f in db_files
            }

            for key, file in db_files_map.items():
                if key not in local_files:
                    self._pg.delete(file)

            for key, full_path in local_files.items():
                if key not in db_files_map:
                    owner_id, relative_path, name, extension = key
                    size = os.path.getsize(full_path)

                    if owner_id is not None:
                        path = os.path.join(config.storage_path, str(owner_id))
                    else:
                        path = config.storage_path

                    new_file = File(
                        name=name,
                        extension=extension,
                        size=size,
                        path=path,
                        relative_path=relative_path,
                        owner_id=owner_id,
                        creation_date=datetime.datetime.utcnow(),
                        update_date=None,
                        comment=None,
                    )
                    self._pg.add(new_file)

        for root, _, _ in os.walk(config.storage_path, topdown=False):
            if (
                not os.listdir(root)
                and os.path.abspath(root) != os.path.abspath(config.storage_path)
            ):
                try:
                    os.rmdir(root)
                except OSError:
                    self._logger.warning(f'Не удаётся удалить {root}')

        self._logger.debug('Синхронизация прошла успешно')

    def get_files(self) -> List[Dict[str, Any]]:
        """Получение списка файлов"""

        path_filter = request.args.get('path')

        with self._pg.begin():
            query = self._pg.query(File).filter(File.owner_id == self._user_id)
            if path_filter:
                query = query.filter(
                    File.relative_path.like(f'%{path_filter}%')
                )
            files = query.all()
            if not files:
                raise ModuleException('No files found', {'data': ''}, 404)
            self._logger.debug('Файлы успешно получены')

            return [file.dump() for file in files]

    def get_file_by_id(
        self,
        input_id: int,
        session: Optional[PGSession] = None,
    ) -> Union[Dict[str, Any], File]:
        """Получение файла по ID"""

        if session is None:
            with self._pg.begin():
                file = self._pg.query(File).get(input_id)
                if not file or (self._user_id and file.owner_id != self._user_id):
                    raise ModuleException(
                        'File not found or access denied', {'data': ''}, 404
                    )
                self._logger.debug(
                    'Файл успешно получен',
                    extra={'id': input_id},
                )

                return file.dump()
        else:
            file = session.query(File).get(input_id)
            if not file or (self._user_id and file.owner_id != self._user_id):
                raise ModuleException(
                    'File not found or access denied', {'data': ''}, 404
                )
            self._logger.debug('Файл успешно получен', extra={'id': input_id})

            return file

    def get_file_by_name(self, file_name: str) -> Dict[str, Any]:
        """Получение файла по имени пользователя"""

        try:
            name, extension = file_name.rsplit('.', 1)
        except ValueError:
            raise ModuleException('Invalid filename', {'data': ''}, 400)
        with self._pg.begin():
            file = (
                self._pg.query(File).filter(
                    File.name == name,
                    File.extension == extension,
                    File.owner_id == self._user_id,
                ).first()
            )
            if not file:
                raise ModuleException('File not found', {'data': ''}, 404)
            self._logger.debug('Файл успешно получен')

            return file.dump()

    def download_file(self, file_id: int):
        """Скачивание файла по ID"""

        file = self.get_file_by_id(file_id)  # здесь вернётся словарь
        full_path = os.path.join(
            self._st,
            file['relative_path'],
            f"{file['name']}.{file['extension']}",
        )
        if not os.path.exists(full_path):
            raise ModuleException('File not found', {'data': ''}, 404)
        self._logger.debug(
            'Файл найден, начинаем скачивание', extra={'id': file_id}
        )

        return send_file(
            full_path,
            as_attachment=True,
            download_name=f"{file['name']}.{file['extension']}",
            mimetype='application/octet-stream',
        )

    def upload_file(self) -> Dict[str, Any]:
        """Загрузка файла в хранилище пользователя и БД"""

        raw_fields = request.form.get('fields')
        if not raw_fields:
            raise ModuleException('Missing form fields', {'data': ''}, 400)
        fields = json.loads(raw_fields)
        uploaded_file = request.files.get('attachment')
        if not uploaded_file:
            raise ModuleException('File not found', {'data': ''}, 400)

        relative_path = os.path.normpath(fields.get('path', '')).lstrip(os.sep)
        full_storage_path = os.path.join(self._st, relative_path)

        filename = uploaded_file.filename
        if not filename:
            raise ModuleException('Invalid filename', {'data': ''}, 400)

        if '.' in filename:
            name, extension = filename.rsplit('.', 1)
        else:
            name, extension = filename, ''

        full_path = os.path.join(full_storage_path, filename)

        if os.path.exists(full_path):
            raise ModuleException('File already exists', {'data': ''}, 400)

        os.makedirs(full_storage_path, exist_ok=True)
        try:
            with open(full_path, 'wb') as f:
                shutil.copyfileobj(uploaded_file.stream, f)
        except Exception as e:
            raise ModuleException(
                'Failed to write file', {'error': str(e)}, 500
            )

        size = os.path.getsize(full_path)
        with self._pg.begin():
            db_file = File(
                name=name,
                extension=extension,
                size=size,
                path=self._st,
                relative_path=relative_path,
                owner_id=self._user_id,
                creation_date=datetime.datetime.utcnow(),
                update_date=None,
                comment=fields.get('comment', ''),
            )
            self._pg.add(db_file)
            self._pg.flush()
            self._pg.refresh(db_file)
            self._logger.debug(
                'Файл успешно загружен', extra={'filename': filename}
            )

        return db_file.dump()

    def update_file(self, file_id: int) -> Dict[str, Any]:
        """Обновление файла и записи о нём"""

        data = request.get_json()
        fields = data.get('fields', {})
        name = fields.get('name')
        path = fields.get('path')
        comment = fields.get('comment')

        if path:
            path = os.path.normpath(path)

        with self._pg.begin():
            file = self.get_file_by_id(file_id, session=self._pg)
            old_full_path = os.path.join(
                self._st, file.relative_path, f'{file.name}.{file.extension}'
            )

            if name:
                file.name = name
            if path:
                file.relative_path = path
            if comment:
                file.comment = comment

            new_full_path = os.path.join(
                self._st, file.relative_path, f'{file.name}.{file.extension}'
            )

            if old_full_path != new_full_path:
                os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                if not os.path.exists(old_full_path):
                    raise ModuleException('File not found', {'data': ''}, 404)
                os.rename(old_full_path, new_full_path)

            file.update_date = datetime.datetime.utcnow()
            self._pg.add(file)
            self._pg.flush()
            self._pg.refresh(file)
            self._logger.debug('Файл успешно обновлён', extra={'id': file_id})

            return file.dump()

    def delete_file(self, file_id: int) -> Dict[str, Any]:
        """Удаление файла и записи о нём"""

        with self._pg.begin():
            file = self.get_file_by_id(file_id, session=self._pg)  # ORM-объект
            full_path = os.path.join(
                self._st, file.relative_path, f'{file.name}.{file.extension}'
            )
            if os.path.exists(full_path):
                os.remove(full_path)
            self._pg.delete(file)
            self._logger.debug('Файл успешно удалён', extra={'id': file_id})

            return file.dump()