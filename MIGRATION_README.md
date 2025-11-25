# Миграция данных из BigQuery в Apache Unomi

Этот документ описывает процесс миграции данных из Google BigQuery в Apache Unomi через REST API.

## Обзор

Система миграции состоит из двух основных компонентов:

1. **Full Migration** - Начальная полная миграция всех данных (30-40 млн строк)
2. **Incremental Sync** - Регулярная инкрементальная синхронизация новых записей

## Архитектура

```
BigQuery (30-40M строк)
    ↓
BigQueryExtractor (батчи по 1000-5000 записей)
    ↓
Transform (BigQuery → Unomi Event Format)
    ↓
UnomiLoader (REST API с retry & rate limiting)
    ↓
Apache Unomi
```

## Структура проекта

```
etl_migration/
├── __init__.py              # Инициализация модуля
├── config.py                # Конфигурация
├── bigquery_extractor.py    # Извлечение из BigQuery
├── unomi_loader.py          # Загрузка в Unomi
├── checkpoint_manager.py    # Управление чекпоинтами
├── utils.py                 # Вспомогательные функции
├── full_migration.py        # Скрипт полной миграции
├── incremental_sync.py      # Скрипт инкрементальной синхронизации
├── logs/                    # Логи миграции
└── checkpoints/             # Чекпоинты и watermarks
```

## Требования

### Python зависимости

```bash
pip install -r requirements.txt
```

Основные библиотеки:
- `google-cloud-bigquery` - работа с BigQuery
- `requests` - HTTP запросы к Unomi API
- `tenacity` - retry механизм
- `tqdm` - progress bar

### Сервисы

1. **Google Cloud Platform**
   - Доступ к BigQuery
   - Service Account с правами на чтение данных
   - JSON ключ для аутентификации

2. **Apache Unomi**
   - Работающий инстанс Unomi
   - REST API доступен
   - Учетные данные для API

## Настройка

### 1. Создание .env файла

Скопируйте `.env.example` в `.env` и заполните параметры:

```bash
cp .env.example .env
```

### 2. Конфигурация BigQuery

```bash
# BigQuery Configuration
BIGQUERY_PROJECT_ID=your-gcp-project-id
BIGQUERY_DATASET=your-dataset-name
BIGQUERY_TABLE=events_table
BIGQUERY_CREDENTIALS_PATH=/path/to/service-account-key.json
```

**Получение Service Account ключа:**

1. Откройте Google Cloud Console
2. IAM & Admin → Service Accounts
3. Создайте новый Service Account или выберите существующий
4. Keys → Add Key → JSON
5. Сохраните JSON файл и укажите путь в `BIGQUERY_CREDENTIALS_PATH`

### 3. Конфигурация Apache Unomi

```bash
# Apache Unomi Configuration
UNOMI_API_URL=http://localhost:8181
UNOMI_API_USERNAME=karaf
UNOMI_API_PASSWORD=karaf
UNOMI_SCOPE=default
```

### 4. Настройка параметров миграции

```bash
# Migration Settings
MIGRATION_BATCH_SIZE=1000        # Размер батча (рекомендуется 1000-5000)
MIGRATION_MAX_WORKERS=4          # Количество воркеров (не используется в текущей версии)
RATE_LIMIT_RPS=10                # Лимит запросов в секунду

# Retry Settings
MAX_RETRIES=3                    # Количество повторных попыток
RETRY_WAIT_MULTIPLIER=2          # Множитель для exponential backoff
RETRY_WAIT_MIN=1                 # Минимальное время ожидания (сек)
RETRY_WAIT_MAX=60                # Максимальное время ожидания (сек)
```

## Использование

### Полная миграция (первый запуск)

```bash
cd etl_migration
python full_migration.py
```

**Опции:**
- `--no-resume` - начать с нуля (игнорировать чекпоинт)

**Что происходит:**
1. Проверка подключений к BigQuery и Unomi
2. Подсчет общего количества записей
3. Извлечение данных батчами
4. Трансформация в формат Unomi Events
5. Загрузка в Unomi через REST API
6. Сохранение чекпоинтов для возможности возобновления
7. Логирование прогресса и ошибок

**Возобновление после прерывания:**

Если миграция была прервана, просто запустите снова:
```bash
python full_migration.py
```

Скрипт автоматически продолжит с последнего чекпоинта.

### Инкрементальная синхронизация

После завершения полной миграции, настройте регулярную синхронизацию новых данных:

```bash
python incremental_sync.py
```

**Опции:**
- `--reset-watermark` - сбросить watermark на текущее max значение

**Как работает:**
1. Загружает последний watermark (последнее обработанное значение `date_ev`)
2. Извлекает только новые записи где `date_ev > watermark`
3. Загружает их в Unomi
4. Обновляет watermark

**Настройка автоматической синхронизации (cron):**

```bash
# Добавьте в crontab для запуска каждые 5 минут
*/5 * * * * cd /path/to/project/etl_migration && python incremental_sync.py >> logs/cron.log 2>&1

# Или каждый час
0 * * * * cd /path/to/project/etl_migration && python incremental_sync.py >> logs/cron.log 2>&1
```

## Мониторинг и отладка

### Логи

Все логи сохраняются в `etl_migration/logs/`:

```bash
# Просмотр последнего лога
tail -f etl_migration/logs/migration_*.log

# Поиск ошибок
grep ERROR etl_migration/logs/migration_*.log

# Поиск предупреждений
grep WARNING etl_migration/logs/migration_*.log
```

### Чекпоинты

Чекпоинты сохраняются в `etl_migration/checkpoints/`:

- `full_migration_checkpoint.json` - прогресс полной миграции
- `watermark.json` - watermark для инкрементальной синхронизации
- `migration_stats.json` - статистика миграции
- `failed_records_*.json` - записи, которые не удалось загрузить

### Проверка статуса

```bash
# Просмотр чекпоинта
cat etl_migration/checkpoints/full_migration_checkpoint.json

# Просмотр watermark
cat etl_migration/checkpoints/watermark.json

# Просмотр статистики
cat etl_migration/checkpoints/migration_stats.json
```

## Устранение неполадок

### Ошибка подключения к BigQuery

```
ERROR: Failed to connect to BigQuery
```

**Решение:**
1. Проверьте путь к JSON ключу в `BIGQUERY_CREDENTIALS_PATH`
2. Убедитесь, что Service Account имеет права `BigQuery Data Viewer`
3. Проверьте правильность `PROJECT_ID`, `DATASET`, `TABLE`

### Ошибка подключения к Unomi

```
ERROR: Unomi API connection failed
```

**Решение:**
1. Убедитесь, что Unomi запущен: `curl http://localhost:8181/cxs/context.json`
2. Проверьте `UNOMI_API_URL`, `USERNAME`, `PASSWORD`
3. Проверьте firewall/network настройки

### Rate Limiting

```
WARNING: Rate limit exceeded
```

**Решение:**
1. Уменьшите `RATE_LIMIT_RPS` в .env
2. Уменьшите `MIGRATION_BATCH_SIZE`
3. Увеличьте интервал между запросами

### Недостаточно памяти

```
MemoryError
```

**Решение:**
1. Уменьшите `MIGRATION_BATCH_SIZE` (например, до 500)
2. Убедитесь, что доступно достаточно RAM

### Неудачные записи

Если некоторые записи не загрузились:

1. Проверьте файлы `failed_records_*.json` в `checkpoints/`
2. Проанализируйте причины ошибок
3. Исправьте проблемы и повторите загрузку вручную

## Формат данных

### BigQuery Schema

```sql
CREATE TABLE events_table (
  id INT64,
  user_id STRING,
  type_ev STRING,
  date_ev TIMESTAMP,
  status STRING
)
```

### Unomi Event Format

```json
{
  "eventType": "type_ev_value",
  "scope": "default",
  "source": {
    "itemId": "bigquery-migration-123",
    "itemType": "migration",
    "scope": "default"
  },
  "target": {
    "itemId": "user_id_value",
    "itemType": "profile",
    "scope": "default"
  },
  "properties": {
    "bigquery_id": "123",
    "status": "active",
    "original_date": "2025-11-25T10:30:00"
  },
  "timeStamp": 1732532400000
}
```

## Производительность

### Рекомендуемые настройки для 30-40 млн записей

```bash
MIGRATION_BATCH_SIZE=2000
RATE_LIMIT_RPS=20
MAX_RETRIES=3
```

**Ожидаемое время миграции:**
- При 20 req/s и батчах по 2000: ~7-10 часов для 40 млн записей
- При 10 req/s и батчах по 1000: ~12-16 часов для 40 млн записей

**Оптимизация:**
1. Увеличьте `RATE_LIMIT_RPS` если Unomi справляется
2. Увеличьте `MIGRATION_BATCH_SIZE` для меньшего количества запросов
3. Запускайте миграцию в непиковые часы

## Безопасность

1. **Никогда** не коммитьте `.env` файл в Git
2. Храните Service Account ключи в безопасном месте
3. Используйте принцип минимальных привилегий для Service Account
4. Рассмотрите использование Secret Manager для production
5. Ограничьте сетевой доступ к Unomi API

## Поддержка

При возникновении проблем:

1. Проверьте логи в `etl_migration/logs/`
2. Проверьте чекпоинты в `etl_migration/checkpoints/`
3. Убедитесь, что все зависимости установлены
4. Проверьте конфигурацию в `.env`

## FAQ

**Q: Можно ли запустить миграцию на нескольких машинах параллельно?**
A: Не рекомендуется. Используйте checkpoint систему для возобновления на одной машине.

**Q: Что делать если миграция очень медленная?**
A: Увеличьте `RATE_LIMIT_RPS` и `MIGRATION_BATCH_SIZE`, если Unomi справляется с нагрузкой.

**Q: Как часто запускать инкрементальную синхронизацию?**
A: Зависит от ваших требований. Для real-time данных - каждые 5-10 минут, для batch - раз в час или день.

**Q: Можно ли изменить формат Unomi событий?**
A: Да, отредактируйте функцию `transform_bigquery_to_unomi_event()` в `utils.py`.

**Q: Как проверить что данные загрузились в Unomi?**
A: Используйте Unomi REST API для запроса профилей и событий, или проверьте через UI если есть.
