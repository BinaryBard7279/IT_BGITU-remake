# app/routers/public.py
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from sqlalchemy.orm import selectinload

from app.models.speciality import Speciality
from app.models.feature import Feature
from app.models.plan import Direction
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.achievement import Achievement

router = APIRouter(tags=["Landing"])
# Указываем FastAPI, где лежат наши HTML-шаблоны
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def render_landing(request: Request):
    """Отдача главной HTML-страницы сайта"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/api/initial-state")
async def get_initial_state(db: AsyncSession = Depends(get_db)):
    """
    Агрегирующий эндпоинт. Заменяет 6 отдельных запросов к БД.
    """
@router.get("/api/initial-state")
async def get_initial_state(db: AsyncSession = Depends(get_db)):
    """
    Агрегирующий эндпоинт. Заменяет 6 отдельных запросов к БД.
    """
    # В SQLAlchemy async сессиях нельзя делать конкурентные вызовы gather на одной сессии.
    # Поэтому выполняем последовательно, но за ОДИН HTTP-запрос.
    
    spec_res = await db.execute(select(Speciality).order_by(Speciality.id))
    subj_res = await db.execute(select(Subject).order_by(Subject.id))
    feat_res = await db.execute(select(Feature).order_by(Feature.id))
    teach_res = await db.execute(select(Teacher).order_by(Teacher.fio))
    achiv_res = await db.execute(select(Achievement).order_by(Achievement.id))
    
    # N+1 оптимизация уже внедрена тобой через selectinload!
    dir_res = await db.execute(select(Direction).options(selectinload(Direction.disciplines)).order_by(Direction.id))

    directions = dir_res.scalars().all()
    dir_data = [{
        "id": d.id,
        "name": d.name,
        "disciplines": [
            {"id": c.id, "name": c.name, "start_term": c.start_term, "end_term": c.end_term, "group": c.group} 
            for c in d.disciplines
        ]
    } for d in directions]

    return {
        "specialities": spec_res.scalars().all(),
        "subjects": subj_res.scalars().all(),
        "features": feat_res.scalars().all(),
        "teachers": teach_res.scalars().all(),
        "achievements": achiv_res.scalars().all(),
        "directions": dir_data
    }