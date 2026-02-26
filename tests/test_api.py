import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Тест: Проверяет, что БД отвечает и математика работает"""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["db_status"] is True
    assert data["math_result"] == 155

@pytest.mark.asyncio
async def test_get_specialities_empty(client):
    """Тест: Эндпоинт отдает 200 OK (даже если БД пока пустая)"""
    response = await client.get("/speciality")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_directions_with_disciplines(client):
    """Тест: Твой сложный роут собирается без ошибок"""
    response = await client.get("/directions-with-disciplines")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
