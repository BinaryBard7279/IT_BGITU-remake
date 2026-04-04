import os
import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.performance import PERF_LOG_ENABLED, perf_logger

# Импорты роутеров
from app.routers import public

app = FastAPI(title="IT BGITU Remake")


# --- Middleware для замера времени (TTR) ---
class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not PERF_LOG_ENABLED:
            return await call_next(request)

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000

        path = request.url.path
        # Игнорируем запросы за статикой
        if not path.startswith(("/static", "/media")):
            ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
            perf_logger.info(f"ENDPOINT | {process_time:>8.2f} ms | {response.status_code} | {request.method} {path} | IP: {ip}")

        response.headers["Server-Timing"] = f"app;desc=\"FastAPI Server\";dur={process_time:.2f}"

        return response

app.add_middleware(PerformanceMiddleware)
# -------------------------------------------

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
app.add_middleware(GZipMiddleware, minimum_size=1000)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = "dev-secret-key-change-it-in-production"
    print("WARNING: SECRET_KEY is not set. Using default development key.")

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=True,
    same_site="lax",
    max_age=3600 * 24
)

# Монтирование статики и медиа
os.makedirs("app/static", exist_ok=True)
os.makedirs("app/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/media", StaticFiles(directory="app/uploads"), name="upload")

templates = Jinja2Templates(directory="app/templates")

# Подключение роутеров
app.include_router(public.router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        forwarded_allow_ips='*',
        reload=True
    )
