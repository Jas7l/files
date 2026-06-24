import io
import os
import allure
import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


@allure.epic("File Storage Service")
@allure.feature("FilesService Unit Tests")
@pytest.mark.unit
class TestFilesService:

    @allure.story("Initialization")
    @allure.title("Создание директории пользователя и установка параметров")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_init_creates_user_directory_and_sets_params(self, tmp_path,
                                                         fs_mod):
        """__init__: создает директорию пользователя и выставляет параметры"""

        with allure.step("Подготовка тестовых данных"):
            session = MagicMock()
            user_id = 42
            fake_storage = tmp_path / "storage"
            fake_storage_str = str(fake_storage)

            fs_mod.config.storage_path = fake_storage_str
            fs_mod.config.max_user_storage_bytes = 20 * 1024 * 1024 * 1024

            made_dirs = []

            def fake_makedirs(path, exist_ok=False):
                made_dirs.append(path)
                allure.attach(f"Вызван os.makedirs с путем: {path}",
                              "makedirs_call", allure.attachment_type.TEXT)

        with allure.step("Подмена os.makedirs и вызов конструктора"):
            with patch.object(fs_mod.os, "makedirs",
                              side_effect=fake_makedirs) as makedirs_mock:
                svc = fs_mod.FilesService(session, user_id=user_id)

        with allure.step("Проверка результатов"):
            makedirs_mock.assert_called()
            expected_path = os.path.join(fake_storage_str, str(user_id))
            assert expected_path in made_dirs
            assert svc._user_id == user_id
            assert svc.max_user_storage == fs_mod.config.max_user_storage_bytes / 1024 / 1024
            assert svc._st == expected_path

            allure.attach(f"Ожидаемый путь: {expected_path}", "expected_path",
                          allure.attachment_type.TEXT)
            allure.attach(f"Фактический путь: {svc._st}", "actual_path",
                          allure.attachment_type.TEXT)

    @allure.story("Get User Used Bytes")
    @allure.title("Получение использованного места через scalar()")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_user_used_bytes_uses_db_scalar(self, monkeypatch, fs_mod):
        """_get_user_used_bytes: подменяем результат scalar() и проверяем возврат"""

        with allure.step("Подготовка моков"):
            session = MagicMock()
            q = MagicMock()
            q.filter.return_value.with_entities.return_value.scalar.return_value = 987654
            session.query.return_value = q
            allure.attach("Mock настроен на возврат 987654", "mock_setup",
                          allure.attachment_type.TEXT)

        with allure.step("Создание сервиса и вызов метода"):
            svc = fs_mod.FilesService(session, user_id=1)
            used = svc._get_user_used_bytes()

        with allure.step("Проверка результата"):
            assert used == 987654
            session.query.assert_called()
            q.filter.assert_called()
            allure.attach(f"Возвращенное значение: {used}", "result",
                          allure.attachment_type.TEXT)

    @allure.story("User Statistics")
    @allure.title("Подсчет статистики с категоризацией файлов")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_user_statistics_categorization(self, monkeypatch,
                                                session_factory,
                                                files_service_factory, fs_mod):
        """get_user_statistics: корректный подсчёт total_used_mb, категорий и free_mb"""

        with allure.step("Создание тестовых файлов с разными категориями"):
            FileObj = SimpleNamespace
            files = [
                FileObj(size=5 * 1024 * 1024, extension="mp3"),  # audio 5 MB
                FileObj(size=20 * 1024 * 1024, extension="mp4"),  # video 20 MB
                FileObj(size=3 * 1024 * 1024, extension="jpg"),  # images 3 MB
                FileObj(size=7 * 1024 * 1024, extension="pdf"),
                # documents 7 MB
                FileObj(size=1 * 1024 * 1024, extension="xyz"),  # other 1 MB
            ]
            allure.attach(f"Создано {len(files)} файлов", "files_count",
                          allure.attachment_type.TEXT)

        with allure.step("Настройка фейковой сессии"):
            session = session_factory(items=files,
                                      scalar_value=sum(f.size for f in files))
            svc = files_service_factory(session, user_id=100)

        with allure.step("Вызов get_user_statistics()"):
            stats = svc.get_user_statistics()

        with allure.step("Проверка общей суммы"):
            assert pytest.approx(stats["total_used_mb"],
                                 rel=1e-3) == pytest.approx(
                (5 + 20 + 3 + 7 + 1), rel=1e-3)
            allure.attach(f"total_used_mb: {stats['total_used_mb']}",
                          "total_used", allure.attachment_type.TEXT)

        with allure.step("Проверка категорий"):
            assert stats["by_category_mb"]["audio"] == 5.0
            assert stats["by_category_mb"]["video"] == 20.0
            assert stats["by_category_mb"]["images"] == 3.0
            assert stats["by_category_mb"]["documents"] == 7.0
            assert stats["by_category_mb"]["other"] == 1.0
            allure.attach(str(stats["by_category_mb"]), "categories",
                          allure.attachment_type.JSON)

        with allure.step("Проверка лимита и свободного места"):
            assert stats[
                       "limit_mb"] == fs_mod.config.max_user_storage_bytes / 1024 / 1024
            assert stats["free_mb"] == pytest.approx(
                stats["limit_mb"] - stats["total_used_mb"], rel=1e-6)
            allure.attach(f"free_mb: {stats['free_mb']}", "free_space",
                          allure.attachment_type.TEXT)

    @allure.story("Delete File")
    @allure.title("Удаление файла с проверкой os.remove и удаления из БД")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_file_calls_remove_and_deletes_db_record(self, monkeypatch,
                                                            files_service_factory,
                                                            session_factory,
                                                            dummy_file_obj,
                                                            fs_mod):
        """delete_file: если файл существует — вызывается os.remove и запись удаляется из БД"""

        with allure.step("Создание тестового файла"):
            dummy = dummy_file_obj(id=7, name="file", extension="txt",
                                   stored_name="deadbeefdead",
                                   relative_path="p", owner_id=1)
            session = session_factory(items=[dummy], scalar_value=0)
            svc = files_service_factory(session, user_id=1)
            allure.attach(f"Создан файл с ID: {dummy.id}", "file_info",
                          allure.attachment_type.TEXT)

        with allure.step("Мокаем get_file_by_id"):
            monkeypatch.setattr(svc, "get_file_by_id",
                                lambda fid, session=None: SimpleNamespace(
                                    stored_name=dummy.stored_name,
                                    extension=dummy.extension,
                                    relative_path=dummy.relative_path,
                                    name=dummy.name,
                                    id=dummy.id,
                                    dump=lambda: {"id": dummy.id},
                                ))

        with allure.step("Мокаем os.remove"):
            removed = {"called": False, "path": None}

            def fake_exists(p):
                return True

            def fake_remove(p):
                removed["called"] = True
                removed["path"] = p
                allure.attach(f"Удален файл: {p}", "removed_file",
                              allure.attachment_type.TEXT)

            monkeypatch.setattr(fs_mod.os.path, "exists", fake_exists)
            monkeypatch.setattr(fs_mod.os, "remove", fake_remove)

        with allure.step("Вызов delete_file"):
            result = svc.delete_file(7)

        with allure.step("Проверка результатов"):
            assert removed["called"] is True
            assert removed["path"] is not None
            if hasattr(session, "deleted"):
                assert len(session.deleted) == 1
            assert result == {"id": 7}

    @allure.story("Get File By ID")
    @allure.title("Получение файла по ID с проверкой ошибок")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_file_by_id_behaviour(self, session_factory,
                                      files_service_factory, fs_mod,
                                      dummy_file_obj):
        """get_file_by_id: успешное получение и ошибки 404 для не найденного и другого владельца"""

        with allure.step("Тест успешного получения файла"):
            obj = dummy_file_obj(id=11, name="ok", extension="txt",
                                 stored_name="sname", owner_id=1)
            q = MagicMock()
            q.get.return_value = obj
            session = MagicMock()
            session.begin.return_value.__enter__.return_value = session
            session.query.return_value = q

            svc = files_service_factory(session, user_id=1)
            got = svc.get_file_by_id(11)

            assert isinstance(got, dict)
            assert got["id"] == 11
            allure.attach(f"Получен файл: {got}", "file_data",
                          allure.attachment_type.JSON)

        with allure.step("Тест: файл не найден"):
            q.get.return_value = None
            with pytest.raises(Exception) as exinfo:
                svc.get_file_by_id(99)
            assert "File not found" in str(
                exinfo.value) or "access denied" in str(exinfo.value)
            allure.attach(str(exinfo.value), "error_message",
                          allure.attachment_type.TEXT)

        with allure.step("Тест: доступ запрещен (чужой файл)"):
            obj2 = dummy_file_obj(id=12, name="other", extension="txt",
                                  stored_name="s2", owner_id=999)
            q.get.return_value = obj2
            with pytest.raises(Exception) as exinfo2:
                svc.get_file_by_id(12)
            assert "access denied" in str(
                exinfo2.value) or "File not found" in str(exinfo2.value)
            allure.attach(str(exinfo2.value), "error_message",
                          allure.attachment_type.TEXT)

    @allure.story("Upload File")
    @allure.title("Загрузка файла: валидация, лимит и успешный сценарий")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_upload_file_validation_and_limit_and_success(self, monkeypatch,
                                                          files_service_factory,
                                                          session_factory,
                                                          dummy_uploaded_file,
                                                          fs_mod):
        """upload_file: проверка наличия полей/attachment, проверка лимита и успешный путь загрузки"""

        session = session_factory(items=[], scalar_value=0)
        svc = files_service_factory(session, user_id=1)

        with allure.step("Сценарий 1: нет fields → исключение"):
            fake_request = SimpleNamespace(form={}, files={})
            monkeypatch.setattr(fs_mod, "request", fake_request)
            with pytest.raises(Exception):
                svc.upload_file()
            allure.attach("Проверка: отсутствие fields вызывает исключение",
                          "validation_1", allure.attachment_type.TEXT)

        with allure.step(
                "Сценарий 2: есть fields, нет attachment → исключение"):
            fake_request = SimpleNamespace(form={"fields": '{"path": ""}'},
                                           files={})
            monkeypatch.setattr(fs_mod, "request", fake_request)
            with pytest.raises(Exception):
                svc.upload_file()
            allure.attach(
                "Проверка: отсутствие attachment вызывает исключение",
                "validation_2", allure.attachment_type.TEXT)

        with allure.step(
                "Сценарий 3: превышение лимита хранилища → исключение"):
            uploaded = dummy_uploaded_file()
            fake_request = SimpleNamespace(form={"fields": '{"path": ""}'},
                                           files={"attachment": uploaded})
            monkeypatch.setattr(fs_mod, "request", fake_request)

            fs_mod.config.max_user_storage_bytes = 1
            monkeypatch.setattr(svc, "_get_user_used_bytes", lambda: 1024)

            with pytest.raises(Exception) as exinfo:
                svc.upload_file()
            assert "Storage limit exceeded" in str(
                exinfo.value) or "413" in str(exinfo.value)
            allure.attach(str(exinfo.value), "limit_error",
                          allure.attachment_type.TEXT)

        with allure.step("Сценарий 4: успешная загрузка файла"):
            fs_mod.config.max_user_storage_bytes = 20 * 1024 * 1024 * 1024
            uploaded = dummy_uploaded_file(data=b"content", filename="ok.txt")
            fake_request = SimpleNamespace(
                form={"fields": '{"path": "p","comment":"c"}'},
                files={"attachment": uploaded})
            monkeypatch.setattr(fs_mod, "request", fake_request)

            monkeypatch.setattr(fs_mod.os, "makedirs", lambda *a, **k: None)

            def fake_copy(src, dst):
                dst.write(src.read())

            monkeypatch.setattr(fs_mod.shutil, "copyfileobj", fake_copy)

            class DummyFileIO(io.BytesIO):
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    self.close()

            monkeypatch.setattr("builtins.open", lambda *a, **k: DummyFileIO())
            monkeypatch.setattr(fs_mod.os.path, "getsize",
                                lambda p: len(b"content"))

            result = svc.upload_file()

            assert isinstance(result, dict)
            assert result.get("name") == "ok"
            allure.attach(f"Результат загрузки: {result}", "upload_result",
                          allure.attachment_type.JSON)

            if hasattr(session, "added"):
                assert len(session.added) == 1 or session.flushed is True

    @allure.story("Update File")
    @allure.title("Обновление файла: имя, путь и комментарий")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_file_changes(self, monkeypatch, files_service_factory,
                                 session_factory, dummy_file_obj, fs_mod):
        """update_file: обновление имени, пути (и os.rename) и комментария"""

        with allure.step("Подготовка исходного файла"):
            original = dummy_file_obj(id=3, name="old", extension="txt",
                                      stored_name="s", relative_path="a",
                                      owner_id=1, comment="oldc")
            session = session_factory(items=[original], scalar_value=0)
            svc = files_service_factory(session, user_id=1)

        with allure.step("Подмена get_file_by_id"):
            class ORMFile:
                def __init__(self, obj):
                    self.id = obj.id
                    self.name = obj.name
                    self.extension = obj.extension
                    self.stored_name = obj.stored_name
                    self.relative_path = obj.relative_path
                    self.comment = obj.comment
                    self.update_date = None

                def dump(self):
                    return {"id": self.id, "name": self.name,
                            "relative_path": self.relative_path,
                            "comment": self.comment}

            orm = ORMFile(original)

            def fake_get_file_by_id(fid, session=None):
                return orm

            monkeypatch.setattr(svc, "get_file_by_id", fake_get_file_by_id)

        with allure.step("Подготовка данных для обновления"):
            fake_json = {
                "fields": {"name": "newname", "path": "b", "comment": "newc"}}
            monkeypatch.setattr(fs_mod, "request",
                                SimpleNamespace(get_json=lambda: fake_json))

        with allure.step("Мокаем os.rename"):
            monkeypatch.setattr(fs_mod.os.path, "exists", lambda p: True)
            renamed = {"called": False, "src": None, "dst": None}

            def fake_rename(s, d):
                renamed["called"] = True
                renamed["src"] = s
                renamed["dst"] = d
                allure.attach(f"Переименован: {s} → {d}", "rename_call",
                              allure.attachment_type.TEXT)

            monkeypatch.setattr(fs_mod.os, "rename", fake_rename)
            monkeypatch.setattr(fs_mod.os, "makedirs", lambda *a, **k: None)

        with allure.step("Вызов update_file и проверка"):
            result = svc.update_file(3)

            assert result["name"] == "newname"
            assert result["relative_path"] == os.path.normpath("b")
            assert result["comment"] == "newc"
            assert renamed["called"] is True

            allure.attach(f"Результат: {result}", "update_result",
                          allure.attachment_type.JSON)