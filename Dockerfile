# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаём директорию для базы данных
RUN mkdir -p affiliate_platform/database

# Экспонируем порт (Railway использует переменную PORT)
EXPOSE 5000

# Команда запуска
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -
