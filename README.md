# Сервис хранения файлов

## Установка

### docker-compose.yml

```yaml
services:
  db:
    image: postgres:15
    container_name: my_postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5442:5432"
    volumes:
      - ./pgdata:/var/lib/postgresql/data
    networks:
      - backend-network

  files:
    image: files:1.0.1
    ports:
      - "8020:8000"
    volumes:
      - ./storage:/app/storage
      - ./config.yaml:/config.yaml
    networks:
      - backend-network
    restart: always

  syncer:
    image: files:1.0.1
    command: python -m scripts.files_sync
    volumes:
      - ./storage:/app/storage
      - ./config.yaml:/config.yaml
    networks:
      - backend-network
    restart: always

networks:
  backend-network:
    driver: bridge
```

### config.yaml
```yaml
pg:
  host: db
  port: 5432
  user: postgres
  password: postgres
  database: my_db

storage_path: /app/storage
sync_interval: 3600
debug: True

```

### .env
```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=my_db
```

### Запуск
`docker build -f Dockerfile -t files:version .`
PyCharm Debug/Run 

## API

### Загрузка файла

`POST /api/files`

**Запрос** `multipart/form-data`
- `fields`: JSON-строка с полями:
  - `path`: путь хранения файла (опционально)
  - `comment`: комментарий (опционально)
- `file`: бинарный файл

Если поле `path` не указано, файл сохранится в storage
Если поле `comment` не указано, по умолчанию запишет пустую строку

**Ответ**: `application/json` `200 OK`

```json5
{
    // Комментарий
    "comment": "",
    // Дата создания
    "creation_date": "2025-07-30T08:41:26.006024",
    // Расширение файла
    "extension": "css",
    // id файла в базе данных
    "id": 3,
    // Имя файла
    "name": "styles",
    // Путь хранения
    "path": "/app/storage/.",
    // Размер файла
    "size": 2947,
    // Дата обновления
    "update_date": "2025-07-30T08:41:26.011264"
}
```

**Ошибки**:
`400` - ошибки в параметрах запроса.
`401` - файл уже существует
`500` - ошибка при записи файла.

### Список файлов с фильтрацией по пути хранения

`GET /api/files?path=`

Где:
* `path` - путь к файлу, для фильтрации

**Ответ** `application/json` `200 OK`

Аналогичен ответу при загрузке файла, вернёт множество файлов

**Ошибки**:
`401` - файл не найден.
`500` - прочие ошибки.

### Информация о файле

`GET /api/files/<int:file_id>`

Где:
* `file_id` - id файла в базе данных

**Ответ** `application/json` `200 OK`

Аналогичен ответу при загрузке файла

**Ошибки**:
`401` - файл не найден.
`500` - прочие ошибки.

### Загрузка файла

`GET /api/files/<int:file_id>/download`

Где:
* `file_id` - id файла в базе данных

**Ответ** `application/octet-stream` `200 OK`

**Ошибки**:
`401` - файл не найден.
`500` - прочие ошибки.

### Обновление файла

`PATCH /api/files/<int:file_id>`

**Запрос** `application/json`
```json5
{
    "fields": {
        // Новое имя файла
        "name": "str",
        // Новый путь хранения
        "path": "str",
        // Новый комментарий
        "comment": "str"
    }
}
```
Все поля являются необязательными, можно менять произвольное количество полей

**Ответ** `application/json` `200 OK`

Аналогичен ответу при загрузке файла

**Ошибки**:
`401` - файл не найден.
`500` - прочие ошибки.

### Удаление файла
`DELETE /api/files/<int:file_id>`
Где:
`file_id` - id файла в базе данных

**Ответ** `application/json` `200 OK`

Аналогичен ответу при загрузке файла

**Ошибки**:
`401` - файл не найден.
`500` - прочие ошибки.
