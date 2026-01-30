from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy import text
import uvicorn
from contextlib import asynccontextmanager
from app.database import create_tables, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head><title>Test Page</title></head>
        <body style="font-family: sans-serif; padding: 20px;">
            <h1>Работает</h1>
            <div id="status">Connecting to DB...</div>
            <script>
                fetch('/api/health')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('status').innerText = 
                            data.db_status ? 
                            'Бд работает Result: ' + data.math_result : 
                            'Error: ' + data.error;
                    })
                    .catch(e => document.getElementById('status').innerText = '❌ API Error');
            </script>
        </body>
    </html>
    """

@app.get("/api/health")
async def health_check():
    try:
        async with engine.connect() as conn:
            # Простейшая математика в БД
            result = await conn.execute(text("SELECT 100 + 55"))
            value = result.scalar()
        return {"db_status": True, "math_result": value}
    except Exception as e:
        return {"db_status": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
