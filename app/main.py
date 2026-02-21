import os
import uvicorn
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastAPIIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from pyinstrument import Profiler

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.routers import auth, cms, public
from app.admin import setup_admin

# 1. Инициализация Sentry для мониторинга сервера
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastAPIIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=1.0,
)

app = FastAPI(title="IT BGITU Remake")

# 2. Middleware для профилирования (только если DEBUG=True в .env)
if os.getenv("DEBUG") == "True":
    @app.middleware("http")
    async def profile_request(request: Request, call_next):
        profiler = Profiler(async_mode="enabled")
        profiler.start()
        response = await call_next(request)
        profiler.stop()
        profiler.print()
        return response

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

class ForceHTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        proto = request.headers.get("x-forwarded-proto")
        if proto == "https":
            request.scope["scheme"] = "https"
        return await call_next(request)

app.add_middleware(ForceHTTPSMiddleware)

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-me")
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=True,
    same_site="lax"
)

# Монтирование статики и загрузок
app.mount("/static", StaticFiles(directory="app/static"), name="static")
os.makedirs("app/uploads", exist_ok=True)
app.mount("/media", StaticFiles(directory="app/uploads"), name="upload")

# Подключение роутеров
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(cms.router)

# Настройка админки sqladmin
setup_admin(app)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, forwarded_allow_ips='*', reload=True)