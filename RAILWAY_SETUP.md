# Railway Deployment - Affiliate Bridge

## ✅ Проект готов к деплою на Railway!

### Файлы конфигурации:

- ✅ `Dockerfile` - Docker образ (основной способ деплоя)
- ✅ `app.py` - Flask приложение (entry point)
- ✅ `railway.toml` - конфигурация Railway (использует Docker)
- ✅ `requirements.txt` - Python зависимости
- ✅ `.dockerignore` - исключения для Docker
- ✅ `Procfile` - резервная команда запуска
- ✅ `.python-version` - Python 3.11

---

## 🚀 Быстрый деплой:

### Шаг 1: Откройте Railway
```
https://railway.app
```

### Шаг 2: New Project → Deploy from GitHub

Выберите репозиторий: **DmitriyKalganov/mypython**

Выберите ветку: **claude/partner-platform-mvp-011CUX7DkfAzmKDte1WzQf3f**

### Шаг 3: Добавьте переменную окружения

В разделе **Variables**:

```
SECRET_KEY=ваш-случайный-секретный-ключ-32-символа
```

Генератор ключа:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Шаг 4: Деплой!

Railway автоматически:
- Обнаружит Python 3.11
- Установит зависимости из requirements.txt
- Запустит: `gunicorn app:app`
- Создаст публичный URL

---

## 🔍 Что должно произойти:

```
[Build]
✓ Detected Python project
✓ Installing Python 3.11
✓ Installing dependencies from requirements.txt
✓ Build complete

[Deploy]
✓ Starting application...
✓ База данных инициализирована
✓ Starting gunicorn
✓ Listening at: http://0.0.0.0:XXXX
✓ Deployment successful
```

---

## 🧪 Проверка после деплоя:

```bash
# Получите ваш Railway URL из dashboard
# Затем протестируйте:

curl https://your-app.railway.app/api/offers

# Должен вернуть JSON с офферами
```

---

## ⚙️ Переменные окружения:

| Переменная | Обязательна | Значение по умолчанию |
|-----------|-------------|---------------------|
| SECRET_KEY | ✅ Да | - |
| PORT | ❌ Нет | Автоматически от Railway |
| DATABASE_URL | ❌ Нет | SQLite в файловой системе |

---

## 🗄️ Рекомендация: Используйте PostgreSQL

Для production лучше использовать PostgreSQL:

1. В Railway: нажмите **+ New** → **Database** → **PostgreSQL**
2. Railway автоматически создаст `DATABASE_URL`
3. Добавьте в `requirements.txt`:
   ```
   psycopg2-binary==2.9.9
   ```
4. Обновите код для использования PostgreSQL вместо SQLite

---

## 🐛 Устранение неполадок:

### "No start command was found"
**Решение:** Railway должен автоматически найти `app.py` и запустить gunicorn. Если нет:
- Проверьте, что `app.py` в корне проекта
- Проверьте `Procfile` и `railway.toml`

### "Module not found"
**Решение:**
```bash
# Проверьте requirements.txt
pip freeze > requirements.txt
```

### "Application failed to start"
**Решение:** Проверьте логи в Railway:
- Dashboard → Deployments → Latest → View Logs

---

## 📋 Команда запуска:

```bash
gunicorn app:app \
  --bind 0.0.0.0:$PORT \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

---

## ✅ Готово!

После успешного деплоя, ваша платформа будет доступна по адресу:

```
https://your-app-name.railway.app
```

Тестовые аккаунты:
- **Компания:** company@example.com / password123
- **Партнёр:** partner@example.com / password123
