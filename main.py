import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
import uvicorn

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_HOST = "db"

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

app = FastAPI()

engine = create_async_engine(DATABASE_URL, echo=True)

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
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(text("SELECT 100 + 55"))
                value = result.scalar()
        return {"db_status": True, "math_result": value}
    except Exception as e:
        return {"db_status": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
