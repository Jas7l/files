## Содержимое проекта
### FastAPI: port 8000
```
@router.post("/files/sync") - синхронизация базы данных и локального хранилища
@router.get("/files") - возвращает JSON со списком файлов из базы данных, ?path=mypath для фильтра по пути файла
@router.get("/files/{file_id}) - возвращает файл из базы данных по ID
@router.get("/files/{file_id}/download) - скачивает файл с указанным ID на локальный компьютер 
@router.post("/files") - загружает файл в базу данных и на локальное хранилище
@router.patch("/files/{file_id}) - даёт возможность обновить некоторые свойства файла
@router.delete("/files/{file_id}) - удаляет файл по id
```

### Postgres data base: port 5432
#### Настройка в .env

### pgAdmin 4: port 8080
#### Для просмотра базы данных и взаимодействия с ней

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
DEBUG=True
APP_NAME=File Manager API
VERSION=1.0.0
POSTGRES_USER=user_name
POSTGRES_PASSWORD=your_password
POSTGRES_DB=db_name
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Запуск Docker
```bash
docker compose build --no-cache
docker compose up
```

