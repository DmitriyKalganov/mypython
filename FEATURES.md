# Новые возможности Affiliate Bridge

## 🔐 Восстановление пароля через Email

### Настройка Email (для продакшна)

Для отправки email необходимо настроить SMTP в переменных окружения:

```bash
# Пример для Gmail
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=ваш-email@gmail.com
MAIL_PASSWORD=app-password  # НЕ обычный пароль!
MAIL_DEFAULT_SENDER=noreply@affiliatebridge.com
```

### Получение App Password для Gmail

1. Включите 2FA для вашего Gmail аккаунта
2. Перейдите: https://myaccount.google.com/apppasswords
3. Создайте новый App Password для "Mail"
4. Используйте сгенерированный пароль в `MAIL_PASSWORD`

### Альтернативные SMTP сервисы

**SendGrid** (бесплатно до 100 писем/день):
```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

**Mailgun** (бесплатно до 5000 писем/месяц):
```
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USERNAME=postmaster@your-domain.mailgun.org
MAIL_PASSWORD=your-mailgun-password
```

### Режим разработки (без email)

Если SMTP не настроен, система автоматически вернет ссылку для восстановления пароля в API ответе (только для разработки!).

---

## 📊 UTM Метки для партнерских ссылок

### Что такое UTM метки?

UTM метки — это параметры, добавляемые к ссылкам для отслеживания эффективности разных рекламных каналов.

### Доступные UTM параметры

| Параметр | Описание | Примеры |
|----------|----------|---------|
| **utm_source** | Источник трафика (обязательный) | `instagram`, `facebook`, `telegram`, `youtube` |
| **utm_medium** | Тип канала | `social`, `cpc`, `email`, `stories`, `post` |
| **utm_campaign** | Название кампании | `summer_sale_2024`, `black_friday`, `new_year` |
| **utm_content** | Вариант объявления | `banner_top`, `video_ad`, `link_in_bio` |
| **utm_term** | Ключевое слово (для контекстной рекламы) | `купить онлайн`, `скидки` |

### Как использовать в UI

1. Войдите в **Личный кабинет** как партнер
2. В разделе **Мои партнёрские ссылки** найдите нужный оффер
3. Нажмите кнопку **"Добавить UTM метки"**
4. Заполните параметры (обязательный только `utm_source`)
5. Скопируйте сгенерированную ссылку
6. Используйте её в своей рекламе

### Пример сгенерированной ссылки

```
https://affiliatebridge.com/track/abc123?utm_source=instagram&utm_medium=stories&utm_campaign=summer_sale
```

### API для создания ссылок с UTM

**POST** `/api/affiliate-links`

```json
{
  "offer_id": 1,
  "utm_source": "instagram",
  "utm_medium": "stories",
  "utm_campaign": "summer_sale_2024",
  "utm_content": "video_15sec",
  "utm_term": ""
}
```

**Ответ:**
```json
{
  "message": "Партнёрская ссылка создана",
  "link": {
    "id": 5,
    "offer_id": 1,
    "tracking_code": "abc123",
    "tracking_url": "https://affiliatebridge.com/track/abc123?utm_source=instagram&utm_medium=stories&utm_campaign=summer_sale_2024&utm_content=video_15sec",
    "utm_source": "instagram",
    "utm_medium": "stories",
    "utm_campaign": "summer_sale_2024",
    "utm_content": "video_15sec"
  }
}
```

### Отслеживание UTM в кликах

Все UTM параметры автоматически сохраняются при клике и доступны в статистике:

```json
{
  "id": 42,
  "affiliate_link_id": 5,
  "partner_id": 10,
  "offer_id": 1,
  "utm_source": "instagram",
  "utm_medium": "stories",
  "utm_campaign": "summer_sale_2024",
  "clicked_at": "2024-10-28T10:30:00"
}
```

### Примеры использования

#### Instagram Stories
```
utm_source=instagram
utm_medium=stories
utm_campaign=autumn_promo
utm_content=swipe_up
```

#### Facebook Post
```
utm_source=facebook
utm_medium=post
utm_campaign=product_launch
utm_content=carousel_ad
```

#### Telegram Channel
```
utm_source=telegram
utm_medium=channel
utm_campaign=daily_deal
utm_content=pinned_message
```

#### YouTube Video
```
utm_source=youtube
utm_medium=video
utm_campaign=review_2024
utm_content=description_link
```

---

## 🚀 Deployment на Railway

### Настройка переменных окружения

В Railway добавьте следующие переменные:

```
SECRET_KEY=your-random-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@affiliatebridge.com
```

### Автоматическая миграция БД

При деплое автоматически создаются новые таблицы для:
- `password_resets` - токены восстановления пароля
- `affiliate_links` - добавлены UTM поля
- `clicks` - добавлены UTM поля

---

## 📝 Changelog

### v2.0.0 (2024-10-28)

**Добавлено:**
- ✅ Восстановление пароля через email с токенами
- ✅ UTM метки для партнерских ссылок
- ✅ Генератор UTM ссылок в UI
- ✅ Отслеживание UTM параметров в кликах
- ✅ Flask-Mail для отправки email
- ✅ HTML шаблоны для email уведомлений

**Улучшено:**
- Аутентификация теперь персистентна между страницами
- Динамическая навигация на основе статуса входа
- UI партнерского кабинета с UTM генератором

**Безопасность:**
- Токены восстановления пароля с истечением (24 часа)
- Одноразовые токены (нельзя использовать повторно)
- Валидация JWT токенов на клиенте
