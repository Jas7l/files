import os
import shutil
import datetime
import mimetypes
from typing import Optional, List
from app.config import settings

from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.models.file import File
from app.schemas.file import FileRead, FileUpdate

# Setup storage
STORAGE_PATH = settings.STORAGE_PATH
os.makedirs(STORAGE_PATH, exist_ok=True)


class FileManager:
    def __init__(self, db: Session):
        self.db = db

    def sync_storage_and_db(self):
        # Get files from db
        db_files = self.db.query(File).all()
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
                self.db.delete(file)

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
                self.db.add(new_file)

        self.db.commit()

        # Delete empty directories
        for root, _, _ in os.walk(STORAGE_PATH, topdown=False):
            if not os.listdir(root) and os.path.abspath(root) != os.path.abspath(STORAGE_PATH):
                try:
                    os.rmdir(root)
                except OSError:
                    pass

    # Get all files, or filter by path by using "like"
    def get_all_files(self, path: Optional[str] = None) -> List[File]:
        query = self.db.query(File)
        if path:
            query = query.filter(File.path.like(f"%{path}%"))
        return query.all()

    def get_file_by_id(self, file_id: int) -> File:
        file = self.db.query(File).filter(File.id == file_id).first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return file

    def get_file_by_name(self, file_name: str) -> File:
        try:
            name, extension = file_name.rsplit('.', 1)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid file name format. Expected 'name.extension'")
        file = self.db.query(File).filter(File.name == name, File.extension == extension).first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return file

    def download_file(self, file_id: int) -> FileResponse:
        file = self.get_file_by_id(file_id)
        file_path = os.path.join(file.path, f"{file.name}.{file.extension}")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")
        return FileResponse(
            path=file_path,
            filename=f"{file.name}.{file.extension}",
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file.name}.{file.extension}"}
        )

    def fetch_file(self, file_name: str) -> FileResponse:
        file = self.get_file_by_name(file_name)
        file_path = os.path.join(file.path, f"{file.name}.{file.extension}")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")
        mime_type, _ = mimetypes.guess_type(file_path)
        media_type = mime_type or "application/octet-stream"
        return FileResponse(
            path=file_path,
            filename=f"{file.name}.{file.extension}",
            media_type=media_type
        )

    def upload_file(self, uploaded_file: UploadFile, path: str = "", comment: Optional[str] = None) -> File:
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
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file

    def update_file(self, file_id: int, file_data: FileUpdate) -> File:
        file = self.get_file_by_id(file_id)
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
        self.db.commit()
        self.db.refresh(file)
        return file

    def delete_file(self, file_id: int) -> File:
        file = self.get_file_by_id(file_id)
        full_path = os.path.join(file.path, f"{file.name}.{file.extension}")
        # Remove file from dir
        if os.path.exists(full_path):
            os.remove(full_path)
        # Remove file from DB
        self.db.delete(file)
        self.db.commit()
        return file
