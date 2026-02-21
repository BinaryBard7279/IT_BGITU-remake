import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles  # <-- 1. ВЕРНУЛИ ИМПОРТ
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.routers import auth, public 
from app.admin import setup_admin    

app = FastAPI(title="IT BGITU Remake")

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-me")
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=True,
    same_site="lax"
)

# 2. ВЕРНУЛИ ЭТУ СТРОЧКУ! Теперь FastAPI сам гарантированно отдаст стили и скрипты
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(public.router)
app.include_router(auth.router)

setup_admin(app)