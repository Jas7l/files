import sys
import os
from pathlib import Path
import types
import io
from types import SimpleNamespace
import pytest
from src.services import files_service
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def fake_config(tmp_path, monkeypatch):
    """
    Возвращает и авт��матически патчит config в модуле services.files_service при импорте через fs_mod fixture.
    """
    cfg = SimpleNamespace(
        storage_path=str(tmp_path),
        max_user_storage_bytes=20 * 1024 * 1024 * 1024,  # 20 GB
    )
    return cfg


@pytest.fixture
def fs_mod(monkeypatch, fake_config):
    monkeypatch.setattr(files_service, "config", fake_config)
    return files_service


class FakeQuery:
    def __init__(self, items=None, scalar_value=0):
        self._items = items or []
        self._scalar = scalar_value
        # support .first() and .get()
        self._first = self._items[0] if self._items else None
        self._get_map = {}

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return self._items

    def first(self):
        return self._first

    def get(self, pk):
        # if explicit map present, use it
        if pk in self._get_map:
            return self._get_map[pk]
        return self._first

    def with_entities(self, *a, **k):
        return self

    def scalar(self):
        return self._scalar


class FakeSession:
    """
    Лёгкий фэйковый PG session, поддерживает контекстный менеджер begin(),
    query(File).all(), query(File).first(), with_entities(...).scalar(),
    add/flush/refresh/delete записи.
    """
    def __init__(self, items=None, scalar_value=0):
        self._items = items or []
        self._scalar = scalar_value
        self.added = []
        self.deleted = []
        self.flushed = False
        self.refreshed = []
        self._query = FakeQuery(items, scalar_value)

    def begin(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    # query(File)
    def query(self, model):
        return self._query

    def add(self, obj):
        self.added.append(obj)

    def flush(self):
        self.flushed = True

    def refresh(self, obj):
        self.refreshed.append(obj)

    def delete(self, obj):
        self.deleted.append(obj)


@pytest.fixture
def session_factory():
    """
    Возвращает фабрику для создания FakeSession с разными параметрами.
    """
    def _factory(items=None, scalar_value=0):
        return FakeSession(items=items, scalar_value=scalar_value)
    return _factory


@pytest.fixture
def files_service_factory(fs_mod):
    """
    Возвращает фабрику для создания экземпляра FilesService.
    Usage: svc = files_service_factory(session, user_id=1)
    """
    def _factory(session, user_id=1):
        return fs_mod.FilesService(session, user_id=user_id)
    return _factory


@pytest.fixture
def dummy_file_obj():
    """
    Возвращает объект, имитирующий ORM File с полями и методом dump()
    """
    class DummyFile:
        def __init__(self, id=1, name="file", extension="txt", stored_name="deadbeef", size=123, path="/", relative_path="", owner_id=1, comment=""):
            self.id = id
            self.name = name
            self.extension = extension
            self.stored_name = stored_name
            self.size = size
            self.path = path
            self.relative_path = relative_path
            self.owner_id = owner_id
            self.comment = comment
            self.update_date = None
            self.creation_date = None

        def dump(self):
            return {
                "id": self.id,
                "name": self.name,
                "extension": self.extension,
                "stored_name": self.stored_name,
                "size": self.size,
                "path": self.path,
                "relative_path": self.relative_path,
                "owner_id": self.owner_id,
                "comment": self.comment,
            }
    return DummyFile


@pytest.fixture
def dummy_uploaded_file():
    """
    Возвращает "загружаемый" файл с stream и filename
    """
    class UFile:
        def __init__(self, data=b"hello", filename="test.txt"):
            self.stream = io.BytesIO(data)
            self.filename = filename

    return UFile
