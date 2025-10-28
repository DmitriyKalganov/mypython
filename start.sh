#!/bin/bash
# Скрипт запуска для Railway

echo "🚀 Запуск Affiliate Bridge Platform..."

# Инициализация БД (если нужно)
# python init_db.py

# Запуск приложения
exec gunicorn app:app \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
