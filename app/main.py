import uvicorn
from fastapi import FastAPI
from app.routers import public, admin

app = FastAPI(title="IT BGITU Remake")

# Подключаем роутеры (разделы сайта)
app.include_router(public.router)
app.include_router(admin.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
