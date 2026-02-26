import asyncio
import os
import sys

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# --- 1. ГЛОБАЛЬНЫЙ ФИКС БАГА WINDOWS ---
# Устанавливаем политику глобально ДО импорта моделей и инициализации фикстур.
# Это гарантирует, что pytest-asyncio подхватит именно Selector, а не Proactor.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.database import get_db
from app.main import app
from app.models import Base

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:1234@localhost:5432/test_db"
)

# --- 2. ИЗОЛЯЦИЯ БД ---
# NullPool сбрасывает соединение после каждого запроса, гарантируя отсутствие
# коллизий ("another operation is in progress") при асинхронном тестировании.
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    """Переопределение зависимости для FastAPI"""
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True, scope="session")
async def prepare_database():
    """Создает таблицы перед началом тестов и удаляет их после завершения."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """Асинхронный HTTP-клиент для тестирования эндпоинтов."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
