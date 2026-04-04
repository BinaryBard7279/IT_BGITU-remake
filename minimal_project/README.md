# Minimal IT BGITU Remake Project

Это минимальная основа проекта для проверки работоспособности Docker, Caddy и FastAPI приложения.

## Структура

```
minimal_project/
├── app/
│   ├── __init__.py
│   ├── main.py           # Точка входа FastAPI
│   ├── config.py         # Настройки приложения
│   ├── database.py       # Подключение к БД
│   ├── performance.py    # Логирование производительности
│   └── routers/
│       ├── __init__.py
│       └── public.py     # Публичные роуты
├── Dockerfile
├── docker-compose.yml
├── Caddyfile
├── requirements.txt
├── .env                  # Переменные окружения
└── .env.example          # Шаблон переменных
```

## Быстрый старт

### 1. Запуск через Docker Compose

```bash
cd minimal_project
docker-compose up --build
```

После запуска:
- Приложение: http://localhost:80 (через Caddy) или http://localhost:8000 (напрямую)
- Health check: http://localhost/api/health

### 2. Локальный запуск (без Docker)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Копирование .env
cp .env.example .env

# Запуск
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/` | Главная страница (JSON) |
| GET | `/api/health` | Проверка здоровья (БД) |
| GET | `/api/test-cache` | Тест кэширования |

## Особенности

- **FastAPI** - современный асинхронный фреймворк
- **SQLAlchemy + asyncpg** - асинхронная работа с PostgreSQL
- **Caddy** - автоматический HTTPS и reverse proxy
- **Performance logging** - встроенное логирование времени выполнения запросов
- **Кэширование** - пример использования cachetools

## Переменные окружения

См. `.env.example` для всех доступных настроек.
