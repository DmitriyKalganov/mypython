#!/usr/bin/env python3
"""
Скрипт запуска Affiliate Bridge платформы
"""
import os
import sys

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'affiliate_platform'))

from affiliate_platform.backend.app import app, db

if __name__ == '__main__':
    with app.app_context():
        # Создание базы данных
        db.create_all()
        print("✓ База данных создана")

    print("\n" + "="*60)
    print("  Affiliate Bridge - Партнёрская платформа")
    print("="*60)
    print("\nСервер запущен на http://localhost:5000")
    print("\nДоступные страницы:")
    print("  • Главная: http://localhost:5000")
    print("  • Регистрация: http://localhost:5000/register")
    print("  • Вход: http://localhost:5000/login")
    print("  • Офферы: http://localhost:5000/offers")
    print("  • Личный кабинет: http://localhost:5000/dashboard")
    print("\nДля остановки нажмите Ctrl+C")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
