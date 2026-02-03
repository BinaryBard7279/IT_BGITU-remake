from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head><title>IT BGITU</title></head>
        <body style="font-family: sans-serif; padding: 20px;">
            <h1>IT БГИТУ - Работает</h1>
            <p>Новая структура проекта (v2)</p>
            <div id="status">Проверка связи с БД...</div>
            <script>
                fetch('/api/health')
                    .then(r => r.json())
                    .then(data => {
                        const el = document.getElementById('status');
                        if (data.db_status) {
                            el.innerText = '✅ База данных активна. Тест: ' + data.math_result;
                            el.style.color = 'green';
                        } else {
                            el.innerText = '❌ Ошибка БД: ' + data.error;
                            el.style.color = 'red';
                        }
                    })
                    .catch(e => document.getElementById('status').innerText = 'API Error');
            </script>
        </body>
    </html>
    """

@router.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 100 + 55"))
        value = result.scalar()
        return {"db_status": True, "math_result": value}
    except Exception as e:
        print(f"DB Error: {e}")
        return {"db_status": False, "error": str(e)}

