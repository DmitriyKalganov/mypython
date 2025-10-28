"""
Flask приложение для Railway deployment
"""
import os
import sys

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from affiliate_platform.backend.app import app as flask_app, db

# Экспортируем app для Railway auto-detection
app = flask_app

def init_db():
    """Инициализация базы данных"""
    with app.app_context():
        db.create_all()
        print("✓ База данных инициализирована")

# Инициализируем БД при первом запуске
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
