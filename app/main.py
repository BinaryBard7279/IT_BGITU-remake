import os
import uvicorn
from fastapi import FastAPI
# StaticFiles больше не нужен в основном приложении, так как статику отдаст Caddy
# from fastapi.staticfiles import StaticFiles 
from fastapi.templating import Jinja2Templates
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.routers import auth, public # cms убрали
from app.admin import setup_admin    

app = FastAPI(title="IT BGITU Remake")


SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-me")
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=True,
    same_site="lax"
)

# Оптимизация: статика теперь на стороне Caddy, Python её не обрабатывает
# app.mount("/static", StaticFiles(directory="app/static"), name="static")
# os.makedirs("app/uploads", exist_ok=True)
# app.mount("/media", StaticFiles(directory="app/uploads"), name="upload")

templates = Jinja2Templates(directory="app/templates")

app.include_router(public.router)
app.include_router(auth.router)
# app.include_router(cms.router) 

# Инициализация админки 
setup_admin(app)

if __name__ == "__main__":
    # Для локальной разработки оставляем uvicorn, 
    # но в Dockerfile для продакшена заменим на Gunicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        forwarded_allow_ips='*',
        reload=True
    )