"""
Главный файл приложения для Railway deployment
"""
import os
import sys

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from affiliate_platform.backend.app import app, db

# Инициализация базы данных
with app.app_context():
    db.create_all()
    print("✓ База данных инициализирована")

# Для gunicorn
application = app

if __name__ == "__main__":
    # Для локального запуска
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
