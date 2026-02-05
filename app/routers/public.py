from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
import os

from app.models.speciality import Speciality
from app.models.feature import Feature
from app.models.plan import Direction, Discipline
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.achievement import Achievement

from app.schemas.speciality import (
    SpecialityCreate, 
    SpecialityUpdate, 
    Speciality as SpecialitySchema,
    Speciality_Features
)
from app.schemas.feature import (
    FeatureBase, 
    FeatureCreate, 
    FeatureUpdate, 
    Feature as FeatureSchema
)
from app.schemas.plan import (
    DirectionBase, DirectionCreate, DirectionUpdate, Direction as DirectionSchema,
    DisciplineBase, DisciplineCreate, DisciplineUpdate, Discipline as DisciplineSchema,
    Direction_Disciplines
)
from app.schemas.teacher import (
    TeacherBase,
    TeacherCreate,
    TeacherUpdate,
    Teacher as TeacherSchema
)
from app.schemas.subject import (
    SubjectBase, 
    SubjectCreate, 
    SubjectUpdate, 
    Subject as SubjectSchema
)
from app.schemas.achievement import (
    AchievementBase,
    Achievement as AchievementSchema,
    AchievementCreate,
    AchievementUpdate
)

router = APIRouter()

@router.get("/") 
async def read_root():

    file_path = os.path.join("app", "templates", "index.html")
    return FileResponse(file_path)

@router.get("/robots.txt", include_in_schema=False)
async def robots():
    return FileResponse(os.path.join("app", "static", "robots.txt"))

@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap():
    return FileResponse(os.path.join("app", "static", "sitemap.xml"))

@router.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 100 + 55"))
        value = result.scalar()
        return {"db_status": True, "math_result": value}
    except Exception as e:
        print(f"DB Error: {e}")
        return {"db_status": False, "error": str(e)}
    
# Гет запросы для подвязки к фронту