import os
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.achievement import Achievement
from app.models.faq import Faq
from app.models.feature import Feature
from app.models.plan import Direction
from app.models.setting import Setting
from app.models.speciality import Speciality
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.timeline import TimelineStep
from app.models.life_event import LifeEvent

# [PERF] Импорт нашего таймера
from app.performance import PerfTimer
from app.schemas.achievement import Achievement as AchievementSchema
from app.schemas.faq import Faq as FaqSchema
from app.schemas.feature import Feature as FeatureSchema
from app.schemas.setting import Setting as SettingSchema
from app.schemas.speciality import Speciality as SpecialitySchema
from app.schemas.subject import Subject as SubjectSchema
from app.schemas.teacher import Teacher as TeacherSchema
from app.schemas.timeline import TimelineStep as TimelineStepSchema
from app.schemas.life_event import LifeEvent as LifeEventSchema

router = APIRouter(tags=["Landing"])

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
        # Логируем реальную ошибку в консоль/логгер сервера
        print(f"Healthcheck DB Error: {e}")
        # Пользователю отдаем безопасное сообщение
        return {"db_status": False, "error": "Database connection failed"}


@router.get("/achievements", response_model=List[AchievementSchema])
async def get_all_achievements(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Achievement).order_by(Achievement.id))
    return result.scalars().all()

@router.get("/faqs", response_model=List[FaqSchema])
async def get_all_faqs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Faq).order_by(Faq.id))
    return result.scalars().all()

@router.get("/features", response_model=List[FeatureSchema])
async def get_all_features(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Feature).order_by(Feature.id))
    return result.scalars().all()


@router.get("/directions-with-disciplines")
async def get_all_directions_with_disciplines(db: AsyncSession = Depends(get_db)):
    # SQL-запрос замеряется автоматически через события SQLAlchemy
    result = await db.execute(select(Direction).options(selectinload(Direction.disciplines)).order_by(Direction.id))
    directions = result.scalars().all()

    # [PERF] Замеряем время упаковки данных в JSON (чистый CPU time)
    with PerfTimer("Упаковка JSON Roadmap"):
        response_data = [{
            "id": d.id,
            "name": d.name,
            "disciplines": [{
                "id": disc.id,
                "name": disc.name,
                "start_term": disc.start_term,
                "end_term": disc.end_term,
                "group": disc.group,
                "direction_id": disc.direction_id
            } for disc in d.disciplines]
        } for d in directions]

    return response_data


@router.get("/speciality", response_model=List[SpecialitySchema])
async def get_all_speciality(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Speciality).order_by(Speciality.id))
    return result.scalars().all()

@router.get("/subjects", response_model=List[SubjectSchema])
async def get_all_subjects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subject).order_by(Subject.id))
    return result.scalars().all()

@router.get("/teachers", response_model=List[TeacherSchema])
async def get_all_teachers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Teacher).order_by(Teacher.fio))
    return result.scalars().all()

@router.get("/settings", response_model=List[SettingSchema])
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Setting))
    return result.scalars().all()

@router.get("/timeline", response_model=List[TimelineStepSchema])
async def get_timeline(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TimelineStep).order_by(TimelineStep.order))
    return result.scalars().all()


@router.get("/life-events", response_model=List[LifeEventSchema])
async def get_life_events(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LifeEvent).order_by(LifeEvent.order, LifeEvent.id.desc()))
    return result.scalars().all()
