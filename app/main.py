import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# --- ДОБАВИТЬ ЭТОТ ИМПОРТ ---
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
# ----------------------------

from app.routers import auth, cms, public
import os

from app.admin import setup_admin

app = FastAPI(title="IT BGITU Remake")

# --- ВСТАВИТЬ ЭТОТ БЛОК СРАЗУ ПОСЛЕ СОЗДАНИЯ APP ---
# Это говорит приложению: "Ты за прокси (Caddy), используй HTTPS ссылки"
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
# ---------------------------------------------------

app.mount("/static", StaticFiles(directory="app/static"), name="static")
os.makedirs("app/uploads", exist_ok=True)
app.mount("/media", StaticFiles(directory="app/uploads"), name="upload")

templates = Jinja2Templates(directory="app/templates")

app.include_router(public.router)
app.include_router(auth.router)
app.include_router(cms.router) 

setup_admin(app)

if __name__ == "__main__":
    # Важно: forwarded_allow_ips='*' разрешает проксирование заголовков
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, forwarded_allow_ips='*', reload=True)