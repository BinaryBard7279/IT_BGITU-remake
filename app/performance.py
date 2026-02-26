import logging
import os
import time
from functools import wraps
from typing import Callable

from sqlalchemy import event
from sqlalchemy.engine import Engine

# --- 1. Настройка логгера ---
# Используем отдельный логгер. Включаем/выключаем через .env
PERF_LOG_ENABLED = os.getenv("ENABLE_PERF_LOGGING", "True").lower() == "true"

perf_logger = logging.getLogger("perf_logger")
perf_logger.setLevel(logging.INFO if PERF_LOG_ENABLED else logging.WARNING)

# Формат лога выровнен так, чтобы цифры (миллисекунды) шли ровным столбцом
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[PERF] %(message)s"))
if not perf_logger.hasHandlers():
    perf_logger.addHandler(handler)
perf_logger.propagate = False


# --- 2. Универсальный таймер для Python-кода ---
class PerfTimer:
    """
    Таймер для точечного замера бизнес-логики.
    Использование:
        with PerfTimer("Упаковка графа roadmap"):
            ...
    """
    def __init__(self, name: str):
        self.name = name
        self.start_time = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if PERF_LOG_ENABLED:
            duration = (time.perf_counter() - self.start_time) * 1000
            perf_logger.info(f"BLOCK    | {duration:>8.2f} ms | {self.name}")

    def __call__(self, func: Callable) -> Callable:
        import asyncio
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            if PERF_LOG_ENABLED:
                duration = (time.perf_counter() - start) * 1000
                perf_logger.info(f"FUNC(A)  | {duration:>8.2f} ms | {self.name or func.__name__}")
            return result

        # Если нужно оборачивать синхронные функции
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            if PERF_LOG_ENABLED:
                duration = (time.perf_counter() - start) * 1000
                perf_logger.info(f"FUNC(S)  | {duration:>8.2f} ms | {self.name or func.__name__}")
            return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


# --- 3. Профилирование БД (SQLAlchemy + asyncpg) ---
def setup_db_profiling(engine: Engine):
    """
    Подключается к движку SQLAlchemy и прозрачно замеряет время каждого SQL-запроса.
    """
    if not PERF_LOG_ENABLED:
        return

    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        # Сохраняем время старта прямо в контексте текущего запроса
        if context:
            context._query_start_time = time.perf_counter()

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if context and hasattr(context, '_query_start_time'):
            total_time = (time.perf_counter() - context._query_start_time) * 1000

            # Чистим SQL-запрос от лишних пробелов и переносов строк для красивого лога
            clean_stmt = " ".join(statement.split())
            # Обрезаем слишком длинные запросы до 150 символов
            if len(clean_stmt) > 150:
                clean_stmt = clean_stmt[:147] + "..."

            perf_logger.info(f"DATABASE | {total_time:>8.2f} ms | {clean_stmt}")
