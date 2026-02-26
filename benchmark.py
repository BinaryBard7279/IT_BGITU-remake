import asyncio
import sys
import time

import httpx

BASE_URL = "http://127.0.0.1:8000"
ITERATIONS = 5

# ВАЖНО: Укажи здесь реальные данные админа из твоей базы
ADMIN_CREDENTIALS = {
    "username": "admin@bgitu.ru",
    "password": "admin123"
}

PUBLIC_ENDPOINTS = [
    "/",
    "/directions-with-disciplines",
    "/teachers",
    "/speciality"
]

ADMIN_ENDPOINTS = [
    "/admin/",
    "/admin/speciality/list",
    "/admin/teacher/list",
    "/admin/discipline/list",
    "/admin/direction/list"
]

async def test_endpoints(client: httpx.AsyncClient, endpoints: list):
    for endpoint in endpoints:
        times = []

        # 1. Запрашиваем профилирование (сохранит файл)
        try:
            await client.get(f"{endpoint}?profile=text")
        except Exception as e:
            print(f"{endpoint:<35} | ОШИБКА: {e}")
            continue

        # 2. Делаем серию запросов для статистики времени
        for _ in range(ITERATIONS):
            start_time = time.perf_counter()
            await client.get(endpoint)
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"{endpoint:<35} | {avg_time:<12.2f} | {min_time:<10.2f} | {max_time:<10.2f}")


async def run_benchmark():
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0, limits=limits, follow_redirects=True) as client:
        print("\n🚀 ЗАПУСК ВНУТРИСЕРВЕРНОГО БЕНЧМАРКА...")
        print("=" * 80)

        print("\n🌍 ПУБЛИЧНЫЕ РОУТЫ:")
        print(f"{'ЭНДПОИНТ':<35} | {'СРЕДНЕЕ (мс)':<12} | {'МИН (мс)':<10} | {'МАКС (мс)':<10}")
        print("-" * 80)
        await test_endpoints(client, PUBLIC_ENDPOINTS)

        print("\n🔐 АВТОРИЗАЦИЯ В SQLADMIN...")
        # SQLAdmin использует form-data для логина
        await client.post("/admin/login", data=ADMIN_CREDENTIALS)

        if "session" not in client.cookies:
            print("❌ Ошибка логина в админку! Проверь ADMIN_CREDENTIALS в скрипте.")
            return

        print("✅ Успешный вход в админку. Тестируем таблицы...")

        print("\n🛠️ РОУТЫ SQLADMIN:")
        print(f"{'ЭНДПОИНТ':<35} | {'СРЕДНЕЕ (мс)':<12} | {'МИН (мс)':<10} | {'МАКС (мс)':<10}")
        print("-" * 80)
        await test_endpoints(client, ADMIN_ENDPOINTS)

        print("=" * 80)
        print("✅ Готово! Детальные отчеты лежат в папке /code/profiling_reports/\n")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_benchmark())
