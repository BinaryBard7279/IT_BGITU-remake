import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

# Все публичные эндпоинты твоего сайта
ENDPOINTS = [
    "/",
    "/api/health",
    "/achievements",
    "/features",
    "/directions-with-disciplines",
    "/speciality",
    "/subjects",
    "/teachers"
]

@pytest.mark.asyncio
@pytest.mark.parametrize("path", ENDPOINTS)
async def test_endpoint_performance(benchmark, path):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        
        # Функция, которую замеряем
        async def fetch():
            return await ac.get(path)

        # Запускаем бенчмарк (автоматически прогоняет много раз)
        response = await benchmark.pedantic(
            fetch, 
            iterations=5, 
            rounds=2
        )
        
        assert response.status_code == 200