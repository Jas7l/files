## Установка и запуск
### Клонирование репозитория
```bash
git clone https://github.com/Jas7l/backend-app.git
cd backend-app
```
### Установка зависимостей
```bash
pip install -r requirements.txt
```
### Настройка .env
```bash
STORAGE_PATH=./storage
DATABASE_URL=sqlite:///./files.db
DEBUG=True
APP_NAME=File Manager API
VERSION=1.0.0
```

### Запуск
```bash
uvicorn app.main:app --reload
```
