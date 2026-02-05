from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
import os 

router = APIRouter()

@router.get("/") 
async def read_root():

    file_path = os.path.join("app", "templates", "index.html")
    return FileResponse(file_path)

@router.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 100 + 55"))
        value = result.scalar()
        return {"db_status": True, "math_result": value}
    except Exception as e:
        print(f"DB Error: {e}")
        return {"db_status": False, "error": str(e)}