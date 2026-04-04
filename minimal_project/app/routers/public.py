import os
from typing import List

from cachetools import TTLCache
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.performance import PerfTimer, perf_logger

# Кэш на 5 минут (300 секунд)
simple_cache = TTLCache(maxsize=1, ttl=300)

router = APIRouter(tags=["Landing"])


@router.get("/")
async def read_root():
    """Простая главная страница"""
    return {"message": "Welcome to IT BGITU Remake API", "status": "running"}


@router.get("/robots.txt", include_in_schema=False)
async def robots():
    return FileResponse(os.path.join("app", "static", "robots.txt"))


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap():
    return FileResponse(os.path.join("app", "static", "sitemap.xml"))


@router.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Проверка здоровья приложения и БД"""
    try:
        result = await db.execute(text("SELECT 100 + 55"))
        value = result.scalar()
        return {"db_status": True, "math_result": value}
    except Exception as e:
        perf_logger.error(f"HEALTH | Database connection failed: {e}")
        return {"db_status": False, "error": "Database connection failed"}


@router.get("/api/test-cache")
async def test_cache():
    """Тестирование кэширования"""
    import time
    if "data" in simple_cache:
        perf_logger.info("CACHE    | HIT      | GET /api/test-cache")
        return {"cached": True, "data": simple_cache["data"]}

    perf_logger.info("CACHE    | MISS     | GET /api/test-cache")
    with PerfTimer("Генерация данных"):
        data = {"value": 42, "timestamp": time.time()}
    
    simple_cache["data"] = data
    return {"cached": False, "data": data}
