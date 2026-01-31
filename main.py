import os
import sys
from dotenv import load_dotenv


load_dotenv(".env.local")
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import uvicorn

# Получаем настройки БД
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"--- CONFIG ---")
print(f"DB HOST: {DB_HOST}")
print(f"DB NAME: {DB_NAME}")
print(f"Connecting URL (hidden pass): postgresql+asyncpg://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
print(f"--------------")

app = FastAPI()
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head><title>Test Page</title></head>
        <body style="font-family: sans-serif; padding: 20px;">
            <h1>Работает</h1>
            <p>Версия с Alembic migrations</p>
            <div id="status">Connecting to DB...</div>
            <script>
                fetch('/api/health')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('status').innerText = 
                            data.db_status ? 
                            'БД работает! 100+55 = ' + data.math_result : 
                            'Error: ' + data.error;
                        document.getElementById('status').style.color = data.db_status ? 'green' : 'red';
                    })
                    .catch(e => {
                        document.getElementById('status').innerText = '❌ API Error';
                        document.getElementById('status').style.color = 'red';
                    });
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
