import os
import time
from datetime import datetime
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

# --- Профилирование и мониторинг ---
from pyinstrument import Profiler
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# [PERF] Импорт нашей новой системы логирования
from app.performance import perf_logger, PERF_LOG_ENABLED
# -----------------------------------

# Импорты роутеров
from app.routers import public
# from app.routers import auth, cms
from app.admin import setup_admin

# --- Настройка OpenTelemetry (Zipkin) ---
resource = Resource.create({"service.name": "it-bgitu-fastapi"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

zipkin_endpoint = os.getenv("OTEL_EXPORTER_ZIPKIN_ENDPOINT", "http://localhost:9411/api/v2/spans")
zipkin_exporter = ZipkinExporter(endpoint=zipkin_endpoint)

provider.add_span_processor(BatchSpanProcessor(zipkin_exporter))
SQLAlchemyInstrumentor().instrument()
# ----------------------------------------

app = FastAPI(title="IT BGITU Remake")

# [PERF] Наш новый легковесный секундомер HTTP-запросов
class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not PERF_LOG_ENABLED:
            return await call_next(request)

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000

        path = request.url.path
        # Игнорируем запросы за статикой, чтобы не засорять логи консоли
        if not path.startswith(("/static", "/media")):
            perf_logger.info(f"ENDPOINT | {process_time:>8.2f} ms | {request.method} {path}")
            
        # Добавляем заголовок Server-Timing для анализа во вкладке Network в браузере
        response.headers["Server-Timing"] = f"app;desc=\"FastAPI Server\";dur={process_time:.2f}"
        
        return response

app.add_middleware(PerformanceMiddleware)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

class ForceHTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        proto = request.headers.get("x-forwarded-proto")
        if proto == "https":
            request.scope["scheme"] = "https"
        return await call_next(request)

app.add_middleware(ForceHTTPSMiddleware)

# --- Текстовый профайлер (Pyinstrument) ---
@app.middleware("http")
async def profile_request(request: Request, call_next):
    if request.query_params.get("profile") == "text":
        profiler = Profiler(async_mode="enabled")
        profiler.start()
        
        response = await call_next(request)
        
        profiler.stop()
        
        # Сохраняем отчет внутри контейнера
        os.makedirs("/code/profiling_reports", exist_ok=True)
        safe_path = request.url.path.strip("/").replace("/", "_") or "root"
        timestamp = datetime.now().strftime("%H-%M-%S")
        filename = f"/code/profiling_reports/{safe_path}_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"ENDPOINT: {request.url.path}\n")
            f.write(f"TIME: {timestamp}\n")
            f.write("="*60 + "\n")
            f.write(profiler.output_text(unicode=True, color=False))
            
        return response
        
    return await call_next(request)
# ------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-me")
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=True,
    same_site="lax"
)

# Монтирование статики и медиа
app.mount("/static", StaticFiles(directory="app/static"), name="static")
os.makedirs("app/uploads", exist_ok=True)
app.mount("/media", StaticFiles(directory="app/uploads"), name="upload")

templates = Jinja2Templates(directory="app/templates")

# Подключение роутеров
app.include_router(public.router)
# app.include_router(auth.router)
# app.include_router(cms.router)

# Подключение админки
setup_admin(app)

# Инструментирование FastAPI для Zipkin
FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        forwarded_allow_ips='*',
        reload=True
    )