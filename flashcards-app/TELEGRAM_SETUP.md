# Настройка Telegram Mini App

Полное руководство по развертыванию приложения флеш-карточек в Telegram без риска утечки API ключа.

## Архитектура

```
Telegram Mini App (Frontend)
         ↓
    Your Backend API (Flask)
         ↓
    Claude API (Anthropic)
```

**API ключ хранится только на backend сервере - никогда на клиенте!**

## Шаг 1: Создание Telegram бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)

2. Отправьте команду `/newbot`

3. Следуйте инструкциям:
   - Введите имя бота: `Flashcards Learning`
   - Введите username: `flashcards_learning_bot` (должен заканчиваться на `_bot`)

4. Сохраните токен бота (выглядит как `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## Шаг 2: Настройка Web App

1. Отправьте BotFather команду `/mybots`

2. Выберите вашего бота

3. Выберите `Bot Settings` → `Menu Button` → `Edit menu button URL`

4. Отправьте URL вашего frontend приложения:
   - Для GitHub Pages: `https://yourusername.github.io/mypython/`
   - Для Vercel: `https://your-app.vercel.app`
   - Для Netlify: `https://your-app.netlify.app`

5. Отправьте название кнопки: `Открыть приложение`

## Шаг 3: Деплой Backend (Flask API)

Backend хранит API ключ Claude и проксирует запросы.

### Вариант A: Heroku (Бесплатно)

```bash
# 1. Установите Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Залогиньтесь
heroku login

# 3. Создайте приложение
cd flashcards-app/backend
heroku create flashcards-api-your-name

# 4. Добавьте API ключ
heroku config:set ANTHROPIC_API_KEY=your_api_key_here

# 5. Деплой
git init
git add .
git commit -m "Initial commit"
git push heroku main

# 6. Проверьте
heroku open
```

Ваш backend будет доступен по адресу: `https://flashcards-api-your-name.herokuapp.com`

### Вариант B: Railway (Рекомендуется)

1. Зарегистрируйтесь на [Railway.app](https://railway.app/)

2. Создайте новый проект:
   - "New Project" → "Deploy from GitHub repo"
   - Выберите ваш репозиторий
   - Root Directory: `flashcards-app/backend`

3. Добавьте переменные окружения:
   - `ANTHROPIC_API_KEY` = ваш API ключ Claude

4. Railway автоматически задеплоит приложение

5. Скопируйте URL (например: `https://flashcards-api.railway.app`)

### Вариант C: Render

1. Зарегистрируйтесь на [Render.com](https://render.com/)

2. Создайте "New Web Service"

3. Подключите GitHub репозиторий

4. Настройте:
   - **Name**: `flashcards-api`
   - **Root Directory**: `flashcards-app/backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

5. Добавьте Environment Variable:
   - Key: `ANTHROPIC_API_KEY`
   - Value: ваш API ключ

6. Нажмите "Create Web Service"

## Шаг 4: Настройка Frontend

Обновите URL backend в вашем frontend:

### Для Vite (текущий проект):

Создайте файл `.env.production` в папке `flashcards-app`:

```env
VITE_API_URL=https://your-backend-url.com
```

Например:
```env
VITE_API_URL=https://flashcards-api.railway.app
```

### Для локальной разработки:

Создайте файл `.env.local`:

```env
VITE_API_URL=http://localhost:5000
```

## Шаг 5: Деплой Frontend

### Вариант A: GitHub Pages

1. Убедитесь, что в `vite.config.js` указан правильный base:
```javascript
base: '/mypython/'
```

2. Соберите и задеплойте:
```bash
cd flashcards-app
npm install
npm run build
npm run deploy
```

3. В настройках GitHub репозитория:
   - Settings → Pages → Source: `gh-pages` branch

### Вариант B: Vercel

```bash
# Установите Vercel CLI
npm i -g vercel

# В папке flashcards-app
cd flashcards-app
vercel

# Следуйте инструкциям
# Добавьте environment variable VITE_API_URL
```

### Вариант C: Netlify

1. Перейдите на [Netlify](https://www.netlify.com/)

2. "New site from Git" → выберите репозиторий

3. Настройте:
   - **Build command**: `cd flashcards-app && npm install && npm run build`
   - **Publish directory**: `flashcards-app/dist`
   - **Environment variables**: `VITE_API_URL=https://your-backend-url`

## Шаг 6: Финальная настройка бота

После деплоя frontend:

1. Откройте BotFather

2. `/mybots` → выберите бота → `Bot Settings` → `Menu Button`

3. Обновите URL на реальный адрес вашего frontend

4. Протестируйте:
   - Откройте вашего бота в Telegram
   - Нажмите кнопку "Открыть приложение"
   - Приложение должно открыться внутри Telegram!

## Шаг 7: Дополнительные настройки бота

### Установить описание:

```
/setdescription
Выберите бота
Отправьте: "Изучайте иностранные языки с AI-генерированными флеш-карточками"
```

### Установить About:

```
/setabouttext
Выберите бота
Отправьте: "Приложение для изучения языков с помощью искусственного интеллекта. Генерируйте карточки автоматически или создавайте вручную."
```

### Установить аватар:

```
/setuserpic
Выберите бота
Отправьте изображение (квадратное, минимум 512x512px)
```

## Проверка работоспособности

### Проверка backend:

```bash
# Проверка health endpoint
curl https://your-backend-url/health

# Ожидаемый ответ:
# {"status":"ok","message":"Server is running"}
```

### Проверка frontend:

Откройте ваш frontend URL в браузере и проверьте:
- Интерфейс загружается
- Можно создать карточку вручную
- AI-генерация работает

### Проверка в Telegram:

1. Откройте бота в Telegram
2. Нажмите на кнопку меню (или отправьте `/start`)
3. Приложение должно открыться в WebView
4. Попробуйте сгенерировать карточки

## Безопасность

✅ **Правильно:**
- API ключ хранится на backend сервере
- Backend использует переменные окружения
- Frontend отправляет запросы только на ваш backend
- CORS настроен правильно

❌ **Неправильно:**
- Хранить API ключ в frontend коде
- Коммитить .env файлы в Git
- Отправлять запросы напрямую к Claude API из frontend

## Мониторинг

### Логи Heroku:
```bash
heroku logs --tail --app your-app-name
```

### Логи Railway:
В веб-интерфейсе: Project → Deployments → View Logs

### Логи Render:
В веб-интерфейсе: Dashboard → Your Service → Logs

## Troubleshooting

### Проблема: "API key not configured"

**Решение:**
1. Проверьте, что переменная окружения установлена на backend
2. Перезапустите backend сервис после добавления переменной

### Проблема: CORS errors

**Решение:**
1. Убедитесь, что в `backend/app.py` включен CORS:
```python
CORS(app)
```
2. Проверьте, что frontend отправляет запросы на правильный URL

### Проблема: "Failed to fetch"

**Решение:**
1. Проверьте, что backend запущен и доступен
2. Проверьте URL в `.env.production`
3. Откройте Developer Tools в браузере и проверьте Network tab

### Проблема: Приложение не открывается в Telegram

**Решение:**
1. Проверьте URL в настройках BotFather
2. Убедитесь, что frontend деплоен и доступен по HTTPS
3. Telegram требует HTTPS для Web Apps!

## Стоимость

### Backend хостинг:
- **Heroku**: бесплатно (с ограничениями)
- **Railway**: $5/месяц (500 часов бесплатно)
- **Render**: бесплатно (с ограничениями)

### Frontend хостинг:
- **GitHub Pages**: бесплатно
- **Vercel**: бесплатно
- **Netlify**: бесплатно

### Claude API:
- Оплата по использованию
- ~$0.003 за 1000 токенов (input)
- ~$0.015 за 1000 токенов (output)
- Для генерации 10 карточек: ~$0.01

## Дальнейшее развитие

### Добавить аутентификацию пользователей:

```python
# backend/app.py
import hmac
import hashlib

def verify_telegram_auth(init_data, bot_token):
    # Проверка подлинности данных от Telegram
    # Документация: https://core.telegram.org/bots/webapps
    pass
```

### Добавить базу данных:

- SQLite для простого варианта
- PostgreSQL для продакшена
- Сохранять карточки пользователей
- История обучения

### Добавить rate limiting:

```python
from flask_limiter import Limiter

limiter = Limiter(app=app, key_func=get_remote_address)

@app.route('/api/generate')
@limiter.limit("10 per hour")
def generate():
    pass
```

## Полезные ссылки

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Web Apps](https://core.telegram.org/bots/webapps)
- [Claude API Docs](https://docs.anthropic.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Vite Documentation](https://vitejs.dev/)

## Поддержка

Если возникли проблемы:
1. Проверьте логи backend сервера
2. Проверьте Console в браузере (F12)
3. Создайте issue в GitHub репозитории
