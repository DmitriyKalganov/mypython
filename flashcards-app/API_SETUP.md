# Настройка API ключа для Claude AI

Для работы функций AI-генерации и автоматического перевода необходим API ключ от Anthropic Claude.

## ⚠️ ВАЖНАЯ ИНФОРМАЦИЯ О БЕЗОПАСНОСТИ

**НЕ коммитьте API ключ в репозиторий!** Это небезопасно и может привести к несанкционированному использованию вашего ключа.

## Вариант 1: Локальная разработка (рекомендуется для тестирования)

Для локального тестирования вы можете временно добавить API ключ непосредственно в код:

1. Откройте файл `src/App.jsx`

2. Найдите функции `generateWithAI` и `autoTranslate`

3. В каждой функции, где делается fetch запрос, добавьте заголовок с API ключом:

```javascript
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "x-api-key": "ВАШ_API_КЛЮЧ_ЗДЕСЬ",  // Добавьте эту строку
    "anthropic-version": "2023-06-01"      // Добавьте эту строку
  },
  body: JSON.stringify({
    // ...
  })
});
```

4. Получите API ключ на https://console.anthropic.com/

5. **ВАЖНО:** Не коммитьте файлы с API ключом!

## Вариант 2: Backend прокси (рекомендуется для продакшена)

Для продакшен-использования создайте простой backend-сервис:

### Пример на Node.js/Express:

```javascript
// server.js
import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

app.post('/api/generate', async (req, res) => {
  try {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": process.env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
      },
      body: JSON.stringify(req.body)
    });

    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

Затем в `src/App.jsx` замените прямые вызовы API на вызовы вашего backend:

```javascript
const response = await fetch("http://localhost:3000/api/generate", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514",
    max_tokens: 2000,
    messages: [...]
  })
});
```

## Вариант 3: Serverless функции

Используйте serverless функции (Vercel, Netlify, AWS Lambda) для безопасного хранения API ключа:

### Пример для Vercel:

Создайте файл `api/generate.js`:

```javascript
export default async function handler(req, res) {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": process.env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify(req.body)
  });

  const data = await response.json();
  res.json(data);
}
```

## Получение API ключа

1. Перейдите на https://console.anthropic.com/
2. Зарегистрируйтесь или войдите в аккаунт
3. Перейдите в раздел "API Keys"
4. Создайте новый ключ
5. Скопируйте его (он будет показан только один раз!)

## Стоимость использования

- Claude API работает по модели pay-as-you-go
- Проверьте актуальные цены на https://www.anthropic.com/pricing
- Для тестирования обычно предоставляются бесплатные кредиты

## Лимиты запросов

- Anthropic устанавливает лимиты на количество запросов
- Рекомендуется добавить rate limiting в вашем приложении
- Можно кэшировать часто запрашиваемые переводы
