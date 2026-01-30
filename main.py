# main.py
import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import uvicorn

DB_USER = "postgres"
DB_PASS = "1234" #меняешь на СВОй пароль в pgadmin
DB_NAME = "test_db_local"
DB_HOST = "localhost"
DB_PORT = "5432"  


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"Connecting to DB at: {DATABASE_URL}")

app = FastAPI()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def run_create_tables():
    await create_tables()
    print("Tables created (or already exist).")

@app.on_event("startup")
async def startup():
    await create_tables()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head><title>Test Page</title></head>
        <body style="font-family: sans-serif; padding: 20px;">
            <h1>Работает (Local)</h1>
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
        print(f"DB Error: {e}")
        return {"db_status": False, "error": str(e)}


if __name__ == "__main__":
    asyncio.run(run_create_tables())
    uvicorn.run(app, host="0.0.0.0", port=8000)
