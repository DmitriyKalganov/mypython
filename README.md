# Affiliate Bridge - Универсальная партнёрская платформа

Полнофункциональная партнёрская платформа для связи компаний и партнёров. Позволяет компаниям размещать офферы, а партнёрам - зарабатывать на их продвижении.

## Описание проекта

**Affiliate Bridge** - это MVP универсальной партнёрской платформы, созданной для рынка СНГ и Узбекистана. Платформа решает проблему массового привлечения партнёров для продаж и предоставляет удобный инструмент заработка для блогеров, владельцев пабликов и обычных пользователей.

### Основные возможности

#### Для компаний:
- ✅ Размещение офферов (товаров/услуг)
- ✅ Настройка процента комиссии
- ✅ Отслеживание кликов и продаж
- ✅ Статистика по партнёрам
- ✅ Управление офферами через личный кабинет

#### Для партнёров:
- ✅ Выбор офферов из каталога
- ✅ Генерация уникальных партнёрских ссылок
- ✅ Отслеживание кликов и конверсий
- ✅ Прозрачная статистика заработка
- ✅ Запрос выплат

#### Для платформы:
- ✅ Комиссия с каждой транзакции
- ✅ Масштабируемая модель бизнеса
- ✅ Автоматический трекинг

## Технологический стек

### Backend:
- **Python 3.8+**
- **Flask 3.0** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **SQLite** - база данных (можно легко мигрировать на PostgreSQL)
- **JWT** - аутентификация
- **bcrypt** - хеширование паролей

### Frontend:
- **HTML5/CSS3**
- **Vanilla JavaScript**
- **Responsive Design**

## Структура проекта

```
affiliate_platform/
├── backend/
│   ├── app.py              # Главное Flask приложение
│   └── models.py           # Модели базы данных
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css   # Стили
│   │   └── js/
│   │       └── main.js     # JavaScript
│   └── templates/
│       ├── index.html      # Главная страница
│       ├── login.html      # Авторизация
│       ├── register.html   # Регистрация
│       ├── dashboard.html  # Личный кабинет
│       └── offers.html     # Каталог офферов
├── database/
│   └── affiliate.db        # База данных SQLite
└── config/
```

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd mypython
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Инициализация базы данных

```bash
cd affiliate_platform/backend
flask init-db
```

### 4. Заполнение тестовыми данными (опционально)

```bash
flask seed-db
```

Это создаст:
- Тестовую компанию: `company@example.com` / `password123`
- Тестового партнёра: `partner@example.com` / `password123`
- 3 тестовых оффера

### 5. Запуск приложения

```bash
python app.py
```

Приложение будет доступно по адресу: `http://localhost:5000`

## API Документация

### Аутентификация

#### Регистрация
```
POST /api/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "user_type": "partner", // или "company"
  "full_name": "Иван Иванов",
  "company_name": "Моя Компания", // только для компаний
  "phone": "+998901234567"
}
```

#### Авторизация
```
POST /api/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { ... }
}
```

### Офферы

#### Получить все офферы
```
GET /api/offers
```

#### Создать оффер (только компании)
```
POST /api/offers
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Название оффера",
  "description": "Описание",
  "price": 500000,
  "commission_percent": 15,
  "category": "Образование",
  "product_url": "https://example.com/product"
}
```

#### Обновить оффер
```
PUT /api/offers/<offer_id>
Authorization: Bearer <token>
```

### Партнёрские ссылки

#### Создать партнёрскую ссылку
```
POST /api/affiliate-links
Authorization: Bearer <token>
Content-Type: application/json

{
  "offer_id": 1
}
```

#### Получить свои ссылки
```
GET /api/affiliate-links
Authorization: Bearer <token>
```

### Трекинг

#### Переход по партнёрской ссылке
```
GET /track/<tracking_code>
```
Автоматически фиксирует клик и перенаправляет на товар.

#### Создать конверсию
```
POST /api/conversions
Authorization: Bearer <token>
Content-Type: application/json

{
  "affiliate_link_id": 1,
  "sale_amount": 500000,
  "order_id": "ORDER123"
}
```

### Статистика

#### Статистика партнёра
```
GET /api/stats/partner
Authorization: Bearer <token>
```

#### Статистика компании
```
GET /api/stats/company
Authorization: Bearer <token>
```

### Выплаты

#### Запросить выплату
```
POST /api/payouts
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 100000,
  "payment_method": "card",
  "payment_details": "8600 **** **** 1234"
}
```

#### История выплат
```
GET /api/payouts
Authorization: Bearer <token>
```

## Модель базы данных

### Users (Пользователи)
- `id` - ID пользователя
- `email` - Email
- `password_hash` - Хеш пароля
- `user_type` - Тип (company/partner)
- `full_name` - ФИО
- `company_name` - Название компании
- `phone` - Телефон
- `balance` - Баланс
- `created_at` - Дата регистрации

### Offers (Офферы)
- `id` - ID оффера
- `company_id` - ID компании
- `title` - Название
- `description` - Описание
- `price` - Цена
- `commission_percent` - % комиссии
- `platform_percent` - % платформы
- `category` - Категория
- `is_active` - Активность

### AffiliateLinks (Партнёрские ссылки)
- `id` - ID ссылки
- `partner_id` - ID партнёра
- `offer_id` - ID оффера
- `tracking_code` - Уникальный код
- `created_at` - Дата создания

### Clicks (Клики)
- `id` - ID клика
- `affiliate_link_id` - ID партнёрской ссылки
- `partner_id` - ID партнёра
- `offer_id` - ID оффера
- `ip_address` - IP адрес
- `clicked_at` - Время клика

### Conversions (Конверсии/Продажи)
- `id` - ID конверсии
- `affiliate_link_id` - ID партнёрской ссылки
- `partner_id` - ID партнёра
- `offer_id` - ID оффера
- `sale_amount` - Сумма продажи
- `commission_amount` - Комиссия партнёра
- `platform_fee` - Комиссия платформы
- `status` - Статус (pending/approved/rejected/paid)

### Payouts (Выплаты)
- `id` - ID выплаты
- `partner_id` - ID партнёра
- `amount` - Сумма
- `payment_method` - Способ оплаты
- `status` - Статус

## Финансовая модель (пример)

```
Средний чек: 500,000 сум
Комиссия компании: 10% (50,000 сум)
  ├─ Партнёр получает: 40,000 сум (80% от комиссии)
  └─ Платформа удерживает: 10,000 сум (20% от комиссии)

При 10,000 заказов в месяц:
Доход платформы = 100,000,000 сум
```

## Дорожная карта

### MVP (Текущая версия)
- ✅ Регистрация и авторизация
- ✅ Создание офферов
- ✅ Генерация партнёрских ссылок
- ✅ Трекинг кликов
- ✅ Базовая статистика
- ✅ Личные кабинеты

### v1.0 (Следующий этап)
- [ ] Автоматические выплаты
- [ ] Интеграция с платёжными системами
- [ ] Email уведомления
- [ ] Расширенная аналитика
- [ ] Экспорт отчётов
- [ ] API для интеграций

### v2.0 (Будущее)
- [ ] Мобильное приложение
- [ ] Многоуровневая партнёрская программа
- [ ] AI-рекомендации офферов
- [ ] Конструктор витрин
- [ ] Система рейтингов
- [ ] Программа лояльности

## Безопасность

- Пароли хешируются с использованием bcrypt
- JWT токены для аутентификации
- CORS настроен для безопасности
- Валидация всех входных данных
- Защита от SQL-инъекций через ORM

## Производительность

Для production рекомендуется:

1. Использовать PostgreSQL вместо SQLite
2. Настроить Redis для кеширования
3. Использовать Gunicorn/uWSGI
4. Настроить Nginx как reverse proxy
5. Включить CDN для статических файлов

## Развёртывание в production

### Docker (рекомендуется)

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-b", "0.0.0.0:5000", "affiliate_platform.backend.app:app"]
```

### Переменные окружения

Создайте файл `.env`:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/affiliate_db
FLASK_ENV=production
```

## Лицензия

MIT License

## Контакты

- Email: info@affiliatebridge.uz
- Telegram: @affiliatebridge
- Сайт: https://affiliatebridge.uz

---

Создано с использованием Flask и современных веб-технологий
