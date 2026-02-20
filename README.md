# Job Tracker

Система автоматического отслеживания вакансий с уведомлениями в Telegram.

**На данный момент поддерживается только HH**

## Описание

Job Tracker — это асинхронное приложение, которое мониторит сайты с вакансиями (например, hh.ru) по заданным параметрам и отправляет уведомления о новых вакансиях в Telegram. Система состоит из двух сервисов:

- **Observer** — периодически сканирует источники вакансий, обнаруживает новые публикации и публикует сообщения в RabbitMQ
- **Telegram Bot** — получает сообщения из RabbitMQ и отправляет уведомления пользователям

## Установка

### Требования

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) — менеджер пакетов
- Docker и Docker Compose

### Быстрый старт с Docker Compose

1. Клонируйте репозиторий:

```bash
git clone <repository-url>
cd job-tracker
```

2. Создайте файл `.env` на основе `.env.dist`:

```bash
cp .env.dist .env
```

3. Настройте переменные окружения в `.env`:

- `TG_BOT__TOKEN` — токен вашего Telegram-бота (получить у [@BotFather](https://t.me/BotFather))
- `TG_BOT__USER_IDS` — список ID пользователей, которые будут получать уведомления

4. Запустите сервисы:

```bash
docker compose up -d
```

### Локальная разработка

1. Установите зависимости:

```bash
uv sync
```

2. Активируйте виртуальное окружение:

```bash
source .venv/bin/activate
```

3. Настройте переменные окружения (см. `.env.dist`)

4. Запустите миграции БД:

```bash
alembic upgrade head
```

5. Запустите сервисы:

```bash
# Observer
python run_observer.py

# Telegram bot (в отдельном терминале)
python run_bot.py
```

## Конфигурация

### Настройка источников вакансий

Отредактируйте `settings.toml`, чтобы добавить или изменить источники:

```toml
[[sources]]
url = "https://hh.ru/search/vacancy?text=python+fastapi&area=1"
source_type = "HH"
period_minutes = 5
```

Параметры:

- `url` — URL страницы с вакансиями
- `source_type` — тип источника (HH, Habr, и т.д.)
- `period_minutes` — интервал проверки в минутах

### Переменные окружения

| Переменная         | Описание                     |
| ------------------ | ---------------------------- |
| `TG_BOT__TOKEN`    | Токен Telegram-бота          |
| `TG_BOT__USER_IDS` | JSON-список ID пользователей |
| `RABBITMQ__URL`    | URL подключения к RabbitMQ   |

## Структура проекта

```
job-tracker/
├── src/
│   ├── core/           # Ядро: конфиги, БД, утилиты
│   └── services/       # Сервисы
│       ├── observer/   # Сервис мониторинга вакансий
│       └── tg_bot/     # Telegram-бот
├── alembic/            # Миграции базы данных
├── data/               # Данные приложения (БД)
├── logs/               # Логи
├── scripts/            # Вспомогательные скрипты
├── compose.yml         # Docker Compose конфигурация
├── Dockerfile          # Docker образ
├── pyproject.toml      # Зависимости и настройки проекта
└── settings.toml       # Настройки приложения
```

## Разработка

### Запуск линтеров и тестов

```bash
# Проверка кода
ruff check .

# Форматирование
ruff format .

# Проверка типов
mypy .

# Запуск тестов
pytest
```

### Pre-commit хуки

Проект использует pre-commit для автоматической проверки кода:

```bash
pre-commit install
```

## Логи

Логи сохраняются в директорию `logs/`:

- `observer.log` — логи сервиса мониторинга
- `tg_bot.log` — логи Telegram-бота

## Лицензия

MIT
