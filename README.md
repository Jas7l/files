# Сервис хранения файлов

## Установка

### docker-compose.yml

```yaml
services:
  db:
    image: postgres:15
    container_name: postgres_container
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - backend-network

  backend:
    image:  files:latest
    ports:
      - "8000:8000"
    depends_on:
      - db
    env_file:
      - .env
    volumes:
      - ./src/storage:/app/storage
      - ./src:/opt/project:cached
    networks:
      - backend-network
    restart: always

  syncer:
    image:  files:latest
    command: python -m scripts.files_sync
    depends_on:
      - db
    env_file:
      - .env
    volumes:
      - ./src/storage:/app/storage
      - ./src:/opt/project:cached
    networks:
      - backend-network
    restart: always

volumes:
  pgdata:

networks:
  backend-network:
    driver: bridge
```

### FastAPI: port 8000
```
@router.post("/api/files/sync") - синхронизация базы данных и локального хранилища
@router.get("/api/files") - возвращает JSON со списком файлов из базы данных, ?path=mypath для фильтра по пути файла
@router.get("/api/files/{file_id}) - возвращает файл из базы данных по ID
@router.get("/api/files/{file_id}/download) - скачивает файл с указанным ID на локальный компьютер 
@router.post("/api/files") - загружает файл в базу данных и на локальное хранилище
@router.patch("/api/files/{file_id}) - даёт возможность обновить некоторые свойства файла
@router.delete("/api/files/{file_id}) - удаляет файл по id
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

