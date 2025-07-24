# Python image
FROM python:3.12-slim

WORKDIR /app
RUN apt update && apt install -y locales
RUN locale-gen ru_RU && locale-gen ru_RU.UTF-8 && update-locale

COPY requirements.txt /app/
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .
WORKDIR /app/src

# Start command
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000", "--reload"]
