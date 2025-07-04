## Содержимое проекта
### FastAPI + SQLite Backend: port 8000
```
@router.post("/sync") - синхронизация базы данных и локального хранилища
@router.get("/files") - возвращает JSON со списком файлов из базы данных, ?path=mypath для фильтра по пути файла
@router.get("/files/{file_id}) - возвращает файл из базы данных по ID
@router.get("/download/{file_id}) - скачивает файл с указанным ID на локальный компьютер 
@router.get("/fetch") - возвращает файл с указанным в ?file_name= именем для использования на фронтенде
@router.post("/upload") - загружает файл в базу данных и на локальное хранилище
@router.patch("/files/{file_id}) - даёт возможность обновить некоторые свойства файла
@router.delete("/files/{file_id}) - удаляет файл по id
```

## Установка и запуск
### Клонирование репозитория
```bash
git clone https://github.com/Jas7l/backend-app.git
cd backend-app
```

### Настройка .env
#### Создание .env
```bash
New-Item -Name ".env" -ItemType "File"
```
#### Настройки для дебага
```bash
STORAGE_PATH=./storage
DATABASE_URL=sqlite:///./files.db
DEBUG=True
APP_NAME=File Manager API
VERSION=1.0.0
```

### Запуск Docker
```bash
docker compose build --no-cache
docker compose up
```

