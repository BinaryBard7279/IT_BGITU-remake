import pytest
from httpx import AsyncClient
from app.main import app

# Список ВСЕХ эндпоинтов для проверки: и публичных, и внутренних страниц sqladmin.
# Это позволит тебе видеть производительность админки наравне с сайтом.
ENDPOINTS = [
    # --- Публичные страницы (из routers/public.py) ---
    "/",
    "/api/health",
    "/achievements",
    "/features",
    "/directions-with-disciplines",
    "/speciality",
    "/subjects",
    "/teachers",
    
    # --- Страницы sqladmin (из admin.py) ---
    # Мы замеряем время генерации списков (list views), 
    # где происходят основные SELECT-запросы к базе.
    "/admin/user/list",
    "/admin/speciality/list",
    "/admin/direction/list",
    "/admin/discipline/list",
    "/admin/teacher/list",
    "/admin/subject/list",
    "/admin/achievement/list",
]

@pytest.mark.asyncio
@pytest.mark.parametrize("path", ENDPOINTS)
async def test_endpoint_performance(benchmark, path):
    """
    Автоматический бенчмарк для всех разделов сайта и админки.
    benchmark заставляет код выполниться многократно, собирая статистику (min, max, mean).
    """
    # Используем follow_redirects=True, так как админка может перенаправлять 
    # неавторизованного пользователя на страницу логина.
    async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as ac:
        
        # Асинхронная функция для замера
        async def fetch():
            return await ac.get(path)

        # Выполняем замер производительности. 
        # iterations — количество повторов в одном раунде, rounds — количество серий замеров.
        response = await benchmark.pedantic(
            fetch, 
            iterations=5, 
            rounds=2
        )
        
        # Проверяем, что страница отдается без ошибок сервера.
        assert response.status_code == 200