from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user

from app.models.user import User
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

from app.security import verify_password, get_password_hash
from app.jwt_manager import jwt_manager

router = APIRouter(prefix="/amdin/cms", tags=["CMS Panel"])


# Subject
@router.post("/subject")
async def subject_create(
    subject_data: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Создание нового предмета.
    """
    result = await db.execute(select(Subject).where(Subject.name == subject_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой предмет уже существует"
        )
    
    subject = Subject(**subject_data.model_dump())
    try:
        db.add(subject)
        await db.commit()
        await db.refresh(subject)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании предмета"
        )
    
    return subject

@router.put("/subject/{subject_id}")
async def subject_update(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Обновить предмет.
    """
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Предмет не найден"
        )
    
    update_data = subject_data.model_dump(exclude_unset=True)
    
    if "name" in update_data:
        result = await db.execute(
            select(Subject).where(
                Subject.name == update_data["name"],
                Subject.id != subject_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Предмет с таким названием уже существует"
            )
    
    for field, value in update_data.items():
        setattr(subject, field, value)
    
    try:
        await db.commit()
        await db.refresh(subject)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при обновлении предмета"
        )
    
    return subject

@router.delete("/subject/{subject_id}")
async def subject_delete(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Удаление предмета.
    """
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Предмет не найден"
        )
    
    try:
        await db.delete(subject)
        await db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при удалении"
        )
    
    return subject

# Teachers (Движуха с фото, static и docker)
# @router.post("/teacher")
# async def teacher_create(
#     teacher_data: TeacherCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user_id: int = Depends(get_current_user)
# ):
#     """
#     Создание нового преподавателя.
#     """
#     result = await db.execute(select(Teacher).where(Teacher.fio == teacher_data.fio))
#     if result.scalar_one_or_none():
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Преподаватель с таким ФИО уже существует"
#         )
    
#     teacher = (Teacher(**teacher_data.model_dump()))

#     try:
#         db.add(teacher)
#         await db.commit()
#         await db.refresh(teacher)
#     except IntegrityError:
#         await db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Ошибка при создании преподавателя"
#         )
    
#     return teacher
    
# @router.put("/teacher/{teacher_id}")
# async def teacher_update(
#     teacher_id: int,
#     teacher_data: TeacherUpdate,
#     db: AsyncSession = Depends(get_db),
#     current_user_id: int = Depends(get_current_user)
# ):
#     """
#     Обновление данных о преподавателе.
#     """
#     result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
#     teacher = result.scalar_one_or_none()

#     if not teacher:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Преподаватель не найден"
#         )
    
#     update_data = teacher_data.model_dump(exclude_unset=True)
    
#     if "fio" in update_data:
#         result = await db.execute(
#             select(Teacher).where(
#                 Teacher.fio == update_data["fio"],
#                 Teacher.id != teacher_id
#             )
#         )
#         if result.scalar_one_or_none():
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Преподаватель уже существует"
#             )
    
#     for field, value in update_data.items():
#         setattr(teacher, field, value)
    
#     try:
#         await db.commit()
#         await db.refresh(teacher)
#     except IntegrityError:
#         await db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Ошибка при обновлении данных"
#         )
    
#     return teacher

# @router.delete("/teacher/{teacher_id}")
# async def teacher_delete(
#     teacher_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user_id: int = Depends(get_current_user)
# ):
#     """
#     Удаление преподавателя.
#     """
#     result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
#     teacher = result.scalar_one_or_none()

#     if not teacher:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Преподаватель не найден"
#         )
    
#     try:
#         await db.delete(teacher)
#         await db.commit()
#     except IntegrityError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Ошибка при удалении"
#         )
    
#     return teacher