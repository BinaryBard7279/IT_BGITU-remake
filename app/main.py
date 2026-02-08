import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.routers import auth, cms, public
from app.admin import setup_admin

app = FastAPI(title="IT BGITU Remake")

# 1. Самое важное для работы за Caddy
# forwarded_allow_ips="*" говорит приложению: "Верь заголовкам от Caddy, он не врет про HTTPS"
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*", forwarded_allow_ips="*")

# 2. Сессии (нужны для админки)
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-me")
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    https_only=True, # Важно: если Caddy дает HTTPS, куки тоже должны быть Secure
    same_site="lax"
)

# 3. Статика и медиа
app.mount("/static", StaticFiles(directory="app/static"), name="static")
os.makedirs("app/uploads", exist_ok=True)
app.mount("/media", StaticFiles(directory="app/uploads"), name="upload")

templates = Jinja2Templates(directory="app/templates")

# 4. Роутеры
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(cms.router) 

# 5. Админка
setup_admin(app)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        forwarded_allow_ips='*',  # Дублируем настройку здесь для надежности
        reload=True
    )