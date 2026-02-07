import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import auth, cms, public
import os

# Импортируем настройку админки
from app.admin import setup_admin

app = FastAPI(title="IT BGITU Remake")

# Подключаем статику
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# Важно: ensure directory exists для uploads
os.makedirs("app/uploads", exist_ok=True)
app.mount("/media", StaticFiles(directory="app/uploads"), name="upload")

templates = Jinja2Templates(directory="app/templates")

# Роутеры
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(cms.router) # Можно оставить для API загрузки картинок

# --- Инициализация админки ---
setup_admin(app)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)