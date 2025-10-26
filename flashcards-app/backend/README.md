# Flashcards Backend API

Безопасный backend для приложения флеш-карточек. Проксирует запросы к Claude API, скрывая API ключ от клиента.

## Возможности

- 🔒 Безопасное хранение API ключа
- 🚀 REST API для генерации карточек и переводов
- 🌐 CORS настроен для Telegram Mini Apps
- 📊 Валидация запросов
- ⚡ Быстрые ответы с таймаутами

## Установка

### Локальная разработка

1. Установите зависимости:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Создайте файл `.env`:
```bash
cp .env.example .env
```

3. Добавьте ваш API ключ в `.env`:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

4. Запустите сервер:
```bash
python app.py
```

Сервер запустится на http://localhost:5000

## API Endpoints

### GET /health
Проверка работоспособности сервера

**Response:**
```json
{
  "status": "ok",
  "message": "Server is running"
}
```

### POST /api/generate
Генерация флеш-карточек

**Request:**
```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 2000,
  "messages": [
    {
      "role": "user",
      "content": "Создай 10 флеш-карточек..."
    }
  ]
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "[{\"front\": \"...\", \"back\": \"...\"}]"
    }
  ]
}
```

### POST /api/translate
Перевод слова

**Request:**
```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 200,
  "messages": [
    {
      "role": "user",
      "content": "Переведи с русского на английский: \"привет\""
    }
  ]
}
```

## Деплой

### Вариант 1: Heroku

1. Установите Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

2. Залогиньтесь:
```bash
heroku login
```

3. Создайте приложение:
```bash
heroku create flashcards-api
```

4. Добавьте API ключ:
```bash
heroku config:set ANTHROPIC_API_KEY=your_api_key_here
```

5. Задеплойте:
```bash
git push heroku main
```

### Вариант 2: Railway

1. Зарегистрируйтесь на https://railway.app/

2. Создайте новый проект из GitHub репозитория

3. В настройках добавьте переменную окружения:
   - `ANTHROPIC_API_KEY` = ваш ключ

4. Railway автоматически задеплоит приложение

### Вариант 3: Render

1. Зарегистрируйтесь на https://render.com/

2. Создайте новый Web Service из GitHub репозитория

3. Настройте:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. Добавьте переменные окружения:
   - `ANTHROPIC_API_KEY` = ваш ключ

### Вариант 4: VPS (DigitalOcean, AWS, etc.)

1. Подключитесь к серверу:
```bash
ssh user@your-server-ip
```

2. Установите зависимости:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx
```

3. Склонируйте репозиторий и установите:
```bash
git clone your-repo
cd flashcards-app/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Создайте systemd сервис `/etc/systemd/system/flashcards.service`:
```ini
[Unit]
Description=Flashcards API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/backend/venv/bin"
Environment="ANTHROPIC_API_KEY=your_key"
ExecStart=/path/to/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

5. Настройте nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. Запустите:
```bash
sudo systemctl enable flashcards
sudo systemctl start flashcards
sudo systemctl restart nginx
```

## Безопасность

- ✅ API ключ хранится в переменных окружения
- ✅ CORS настроен для защиты от несанкционированного доступа
- ✅ Валидация входных данных
- ✅ Таймауты для защиты от зависания
- ⚠️ Рекомендуется добавить rate limiting
- ⚠️ Рекомендуется добавить аутентификацию

## Расширения

### Добавить rate limiting:

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/generate', methods=['POST'])
@limiter.limit("10 per minute")
def generate_flashcards():
    # ...
```

### Добавить аутентификацию Telegram:

```python
import hashlib
import hmac

def verify_telegram_auth(auth_data, bot_token):
    check_hash = auth_data.pop('hash', None)
    data_check_string = '\n'.join([f'{k}={v}' for k, v in sorted(auth_data.items())])
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return calculated_hash == check_hash
```

## Мониторинг

Проверка работоспособности:
```bash
curl https://your-api-url/health
```

Тестирование генерации:
```bash
curl -X POST https://your-api-url/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-sonnet-4-20250514", "max_tokens": 100, "messages": [{"role": "user", "content": "Hi"}]}'
```
