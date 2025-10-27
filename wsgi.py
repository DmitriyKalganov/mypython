"""
WSGI entry point для production деплоя
"""
import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

from affiliate_platform.backend.app import app, db

# Инициализация базы данных при первом запуске
with app.app_context():
    db.create_all()
    print("✓ База данных инициализирована")

if __name__ == "__main__":
    app.run()
