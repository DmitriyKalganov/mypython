# ETL Migration: BigQuery → Apache Unomi

Модуль для миграции данных из Google BigQuery в Apache Unomi.

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r ../requirements.txt
```

### 2. Настройка

Создайте `.env` файл в корне проекта:

```bash
cp ../.env.example ../.env
```

Заполните параметры BigQuery и Unomi в `.env`.

### 3. Запуск полной миграции

```bash
python full_migration.py
```

### 4. Настройка инкрементальной синхронизации

```bash
# Разовая синхронизация
python incremental_sync.py

# Автоматическая синхронизация (добавьте в crontab)
*/10 * * * * cd /path/to/project/etl_migration && python incremental_sync.py
```

## Документация

Подробная документация: [../MIGRATION_README.md](../MIGRATION_README.md)

## Структура

- `config.py` - Конфигурация
- `bigquery_extractor.py` - Извлечение из BigQuery
- `unomi_loader.py` - Загрузка в Unomi
- `checkpoint_manager.py` - Управление чекпоинтами
- `utils.py` - Вспомогательные функции
- `full_migration.py` - Полная миграция
- `incremental_sync.py` - Инкрементальная синхронизация

## Мониторинг

```bash
# Просмотр логов
tail -f logs/migration_*.log

# Проверка прогресса
cat checkpoints/full_migration_checkpoint.json

# Статистика
cat checkpoints/migration_stats.json
```
