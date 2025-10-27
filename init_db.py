#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных и заполнения тестовыми данными
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'affiliate_platform'))

from affiliate_platform.backend.app import app, db
from affiliate_platform.backend.models import User, Offer

def init_database():
    """Инициализировать базу данных"""
    with app.app_context():
        # Создание таблиц
        db.create_all()
        print("✓ Таблицы базы данных созданы")

        # Проверка существующих данных
        if User.query.count() > 0:
            print("⚠ База данных уже содержит данные. Пропускаем заполнение.")
            return

        # Создание тестовой компании
        company = User(
            email='company@example.com',
            user_type='company',
            full_name='Дмитрий Калганов',
            company_name='Tech Solutions LLC',
            phone='+998901234567'
        )
        company.set_password('password123')
        db.session.add(company)
        db.session.flush()  # Чтобы получить ID

        # Создание тестового партнёра
        partner = User(
            email='partner@example.com',
            user_type='partner',
            full_name='Иван Иванов',
            phone='+998909876543'
        )
        partner.set_password('password123')
        db.session.add(partner)

        # Создание тестовых офферов
        offers_data = [
            {
                'title': 'Курс по программированию Python',
                'description': 'Полный курс Python от начального до продвинутого уровня. Включает практические задания и проекты.',
                'price': 500000,
                'commission_percent': 15,
                'platform_percent': 20,
                'category': 'Образование',
                'product_url': 'https://example.com/python-course'
            },
            {
                'title': 'Смартфон Samsung Galaxy A54',
                'description': 'Современный смартфон с отличной камерой, большим экраном и мощным процессором.',
                'price': 3500000,
                'commission_percent': 10,
                'platform_percent': 20,
                'category': 'Электроника',
                'product_url': 'https://example.com/samsung-a54'
            },
            {
                'title': 'Фитнес-подписка на 3 месяца',
                'description': 'Безлимитное посещение тренажёрного зала, групповые занятия и консультации тренера.',
                'price': 600000,
                'commission_percent': 20,
                'platform_percent': 20,
                'category': 'Здоровье',
                'product_url': 'https://example.com/fitness'
            },
            {
                'title': 'Курс английского языка онлайн',
                'description': 'Интерактивный курс английского языка с носителями языка.',
                'price': 800000,
                'commission_percent': 12,
                'platform_percent': 20,
                'category': 'Образование',
                'product_url': 'https://example.com/english'
            },
            {
                'title': 'Умные часы Apple Watch Series 9',
                'description': 'Последняя модель умных часов Apple с расширенными функциями здоровья.',
                'price': 5000000,
                'commission_percent': 8,
                'platform_percent': 20,
                'category': 'Электроника',
                'product_url': 'https://example.com/apple-watch'
            }
        ]

        for offer_data in offers_data:
            offer = Offer(company_id=company.id, **offer_data)
            db.session.add(offer)

        db.session.commit()

        print("\n" + "="*60)
        print("✓ База данных успешно инициализирована!")
        print("="*60)
        print("\nТестовые аккаунты:")
        print("\n1. Компания:")
        print("   Email: company@example.com")
        print("   Пароль: password123")
        print("\n2. Партнёр:")
        print("   Email: partner@example.com")
        print("   Пароль: password123")
        print("\n" + "="*60)
        print(f"✓ Создано офферов: {len(offers_data)}")
        print("="*60 + "\n")

if __name__ == '__main__':
    init_database()
