import os
import shutil
import datetime
import mimetypes
from typing import Optional, List, Union
from app.config import settings
from sqlalchemy.orm import Session

from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse

from app.models.file import File
from app.schemas.file import FileRead, FileUpdate
from app.database import context_db

# Setup storage
STORAGE_PATH = settings.STORAGE_PATH
os.makedirs(STORAGE_PATH, exist_ok=True)


class FileManager:
    @staticmethod
    def sync_storage_and_db():
        # Get files from db
        with context_db() as db:
            db_files = db.query(File).all()
            db_files_path = {
                os.path.normpath(os.path.join(file.path, f"{file.name}.{file.extension}")): file for file in db_files
            }

            # Get files from system storage
            fs_files_path = {}
            for root, _, files in os.walk(STORAGE_PATH):
                for file in files:
                    full_path = os.path.normpath(os.path.join(root, file))
                    fs_files_path[full_path] = file

            # Delete files from DB if not on disk
            for path, file in db_files_path.items():
                if path not in fs_files_path:
                    db.delete(file)

            # d
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
                    db.add(new_file)



        # Delete empty directories
        for root, _, _ in os.walk(STORAGE_PATH, topdown=False):
            if not os.listdir(root) and os.path.abspath(root) != os.path.abspath(STORAGE_PATH):
                try:
                    os.rmdir(root)
                except OSError:
                    pass

    # Get all files, or filter by path by using "like"
    @staticmethod
    def get_all_files(path: Optional[str] = None) -> List[FileRead]:
        with context_db() as db:
            query = db.query(File)
            if path:
                query = query.filter(File.path.like(f"%{path}%"))
            files = query.all()
            return [FileRead.model_validate(f) for f in files]

    @staticmethod
    def get_file_by_id(file_id: int,db: Optional[Session] = None) -> Union[File, FileRead]:
        own_session = False
        if db is None:
            db = context_db().__enter__()
            own_session = True

        file = db.query(File).filter(File.id == file_id).first()
        if not file:
            if own_session:
                db.__exit__(None, None, None)
            raise HTTPException(status_code=404, detail="File not found")

        if own_session:
            result = FileRead.model_validate(file)
            db.__exit__(None, None, None)
            return result
        return file

    @staticmethod
    def get_file_by_name(file_name: str) -> FileRead:
        with context_db() as db:
            try:
                name, extension = file_name.rsplit('.', 1)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid file name format. Expected 'name.extension'")
            file = db.query(File).filter(File.name == name, File.extension == extension).first()
            if not file:
                raise HTTPException(status_code=404, detail="File not found")
            return FileRead.model_validate(file)

    @staticmethod
    def download_file(file_id: int) -> FileResponse:
        file = FileManager.get_file_by_id(file_id)
        file_path = os.path.join(file.path, f"{file.name}.{file.extension}")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")
        return FileResponse(
            path=file_path,
            filename=f"{file.name}.{file.extension}",
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file.name}.{file.extension}"}
        )

    @staticmethod
    def upload_file(uploaded_file: UploadFile, path: str = "", comment: Optional[str] = None) -> FileRead:
        os.path.normpath(path)
        filename = uploaded_file.filename
        name, extension = os.path.splitext(filename)
        extension = extension.lstrip('.')
        full_storage_path = os.path.join(STORAGE_PATH, path)
        full_path = os.path.join(full_storage_path, filename)

        if os.path.exists(full_path):
            raise HTTPException(status_code=400, detail="File already exists")

        # Creating dir if it doesn't exist
        os.makedirs(full_storage_path, exist_ok=True)

        # Writing file on local storage
        with open(full_path, 'wb') as f:
            shutil.copyfileobj(uploaded_file.file, f)

        size = os.path.getsize(full_path)

        # Creating file for load to DB
        with context_db() as db:
            db_file = File(
                name=name,
                extension=extension,
                size=size,
                path=full_storage_path,
                creation_date=datetime.datetime.utcnow(),
                update_date=None,
                comment=comment
            )

            # Update DB
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
            return FileRead.model_validate(db_file)

    @staticmethod
    def update_file(file_id: int, file_data: FileUpdate) -> FileRead:
        with context_db() as db:
            file = FileManager.get_file_by_id(file_id, db=db)
            old_path = os.path.join(file.path, f"{file.name}.{file.extension}")

            # Update fields if needed
            if file_data.name:
                file.name = file_data.name
            if file_data.path:
                file.path = file_data.path
            if file_data.comment is not None:
                file.comment = file_data.comment

            # Move and rename file if needed
            new_full_path = os.path.join(file.path, f"{file.name}.{file.extension}")
            if old_path != new_full_path:
                os.makedirs(file.path, exist_ok=True)
                if not os.path.exists(old_path):
                    raise HTTPException(status_code=404, detail="File not found on disk")
                os.rename(old_path, new_full_path)

            # Update DB
            file.update_date = datetime.datetime.utcnow()
            db.add(file)
            return FileRead.model_validate(file)

    @staticmethod
    def delete_file(file_id: int) -> FileRead:
        with context_db() as db:
            file = FileManager.get_file_by_id(file_id, db=db)
            full_path = os.path.join(file.path, f"{file.name}.{file.extension}")
            # Remove file from dir
            if os.path.exists(full_path):
                os.remove(full_path)
            # Remove file from DB
            db.delete(file)
            return FileRead.model_validate(file)
