from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List

from app.database import get_db

from app.models.speciality import Speciality
from app.models.feature import Feature
from app.models.plan import Direction
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.achievement import Achievement

from app.schemas.speciality import Speciality as SpecialitySchema
from app.schemas.feature import Feature as FeatureSchema
from app.schemas.teacher import Teacher as TeacherSchema
from app.schemas.subject import Subject as SubjectSchema
from app.schemas.achievement import Achievement as AchievementSchema
from app.schemas.plan import Direction_Disciplines

router = APIRouter(tags=["Landing"])
templates = Jinja2Templates(directory="app/templates")

# Описываем структуру агрегированного ответа для FastAPI
class InitialStateResponse(BaseModel):
    specialities: List[SpecialitySchema]
    subjects: List[SubjectSchema]
    features: List[FeatureSchema]
    teachers: List[TeacherSchema]
    achievements: List[AchievementSchema]
    directions: List[Direction_Disciplines]

@router.get("/")
async def render_landing(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/api/initial-state", response_model=InitialStateResponse)
async def get_initial_state(db: AsyncSession = Depends(get_db)):
    spec_res = await db.execute(select(Speciality).order_by(Speciality.id))
    subj_res = await db.execute(select(Subject).order_by(Subject.id))
    feat_res = await db.execute(select(Feature).order_by(Feature.id))
    teach_res = await db.execute(select(Teacher).order_by(Teacher.fio))
    achiv_res = await db.execute(select(Achievement).order_by(Achievement.id))
    dir_res = await db.execute(select(Direction).options(selectinload(Direction.disciplines)).order_by(Direction.id))

    return {
        "specialities": spec_res.scalars().all(),
        "subjects": subj_res.scalars().all(),
        "features": feat_res.scalars().all(),
        "teachers": teach_res.scalars().all(),
        "achievements": achiv_res.scalars().all(),
        "directions": dir_res.scalars().all()
    }