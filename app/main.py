import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.routers import auth, cms, public
from app.admin import setup_admin

app = FastAPI(title="IT BGITU Remake")

# 1. Доверяем заголовкам прокси (Caddy)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 2. MIDDLEWARE ДЛЯ ИСПРАВЛЕНИЯ КНОПКИ УДАЛЕНИЯ
# Заставляет FastAPI думать, что он работает по HTTPS, чтобы ссылки в формах были правильными
class ForceHTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Проверяем заголовок от Caddy
        proto = request.headers.get("x-forwarded-proto")
        if proto == "https":
            request.scope["scheme"] = "https"
        return await call_next(request)

app.add_middleware(ForceHTTPSMiddleware)

# 3. НАСТРОЙКА СЕССИЙ (Важно для стабильной работы админки)
# secret_key берем из переменных окружения, как и в jwt_manager.py
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-me")
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    https_only=True,  # Куки будут передаваться только по HTTPS
    same_site="lax"
)

# Монтируем статику и загрузки
app.mount("/static", StaticFiles(directory="app/static"), name="static")
os.makedirs("app/uploads", exist_ok=True)
app.mount("/media", StaticFiles(directory="app/uploads"), name="upload")

templates = Jinja2Templates(directory="app/templates")

# Подключаем роутеры
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(cms.router) 

# Инициализируем админку
setup_admin(app)

if __name__ == "__main__":
    # forwarded_allow_ips='*' крайне важен для работы ProxyHeadersMiddleware
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        forwarded_allow_ips='*', 
        reload=True
    )