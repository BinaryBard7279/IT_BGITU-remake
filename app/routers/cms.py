from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from sqlalchemy.orm import joinedload
from sqlalchemy import func
import shutil
import uuid
from pathlib import Path

from app.database import get_db
from app.dependencies import get_current_user

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

router = APIRouter(prefix="/admin/cms", tags=["CMS Panel"])

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user)
):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Только изображения (jpg, png, webp)"
            )

    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    save_directory = Path("app/uploads")
    save_directory.mkdir(parents=True, exist_ok=True)

    save_path = save_directory / unique_filename

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сохранения файла"
        )

    return {"url": f"/media/{unique_filename}"}

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

@router.post("/feature")
async def feature_create(
    feature_data: FeatureCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Создание нового преимущества.
    """
    result = await db.execute(select(Feature).where(Feature.title == feature_data.title))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такое объект уже существует"
        )
    
    feature = Feature(**feature_data.model_dump())
    try:
        db.add(feature)
        await db.commit()
        await db.refresh(feature)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании объекта"
        )
    
    return feature

@router.put("/feature/{feature_id}")
async def feature_update(
    feature_id: int,
    feature_data: FeatureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Обновить преимущество
    """
    result = await db.execute(select(Feature).where(Feature.id == feature_id))
    feature = result.scalar_one_or_none()

    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Обект не найден"
        )
    
    update_data = feature_data.model_dump(exclude_unset=True)
    
    if "title" in update_data:
        result = await db.execute(
            select(Feature).where(
                Feature.title == update_data["title"],
                Feature.id != feature_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Объект с таким названием уже существует"
            )
    
    for field, value in update_data.items():
        setattr(feature, field, value)
    
    try:
        await db.commit()
        await db.refresh(feature)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при обновлении объекта"
        )
    
    return feature
    
@router.delete("/feature/{feature_id}")
async def feature_delete(
    feature_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id:int = Depends(get_current_user)
):
    """
    Удаление преимущества
    """
    result = await db.execute(select(Feature).where(Feature.id == feature_id))
    feature = result.scalar_one_or_none()

    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Объект не найден"
        )
    
    try:
        await db.delete(feature)
        await db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при удалении объекта"
        )
    
    return feature

@router.post("/speciality")
async def speciality_create(
    speciality_data: SpecialityCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Создание новой специальности
    """
    result = await db.execute(select(Speciality).where(Speciality.name == speciality_data.name))

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Спесиальность с таким названием уже существует"
        )
    
    speciality = Speciality(**speciality_data.model_dump())
    try:
        db.add(speciality)
        await db.commit()
        await db.refresh(speciality)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании специальности"
        )
    
    return speciality

@router.put("/speciality/{speciality_id}")
async def speciality_update(
    speciality_id: int,
    speciality_data: SpecialityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Редактирование специальности
    """
    result = await db.execute(select(Speciality).where(Speciality.id == speciality_id))
    speciality = result.scalar_one_or_none()

    if not speciality:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Специальность не найдена"
        )
    
    update_data = speciality_data.model_dump(exclude_unset=True)
    
    if "name" in update_data:
        result = await db.execute(
            select(Speciality).where(
                Speciality.name == update_data["name"],
                Speciality.id != speciality_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Специальность с таким названием уже существует"
            )
    
    for field, value in update_data.items():
        setattr(speciality, field, value)
    
    try:
        await db.commit()
        await db.refresh(speciality)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при обновлении специальности"
        )
    
    return speciality

@router.delete("/speciality/{speciality_id}")
async def speciality_delete(
    speciality_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Удаление специальности
    """
    result = await db.execute(select(Speciality).where(Speciality.id == speciality_id))
    speciality = result.scalar_one_or_none()

    if not speciality:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Специальность не найдена"
        )
    
    try:
        await db.delete(speciality)
        await db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при удалении специальности"
        )
    
    return speciality

@router.post("/achievements")
async def achive_create(
    achive_data: AchievementCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Создание нового достижения
    """
    result = await db.execute(select(Achievement).where(Achievement.title == achive_data.title))

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Достижение с таким заголовком уже существует"
        )
    achive = Achievement(**achive_data.model_dump())

    try:
        db.add(achive)
        await db.commit()
        await db.refresh(achive)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Проблема с созданием достижения"
        )
    
    return achive

@router.put("/achievements/{achive_id}")
async def achive_update(
    achive_id: int,
    achive_data: AchievementUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Обновление достижения
    """
    result = await db.execute(select(Achievement).where(Achievement.id == achive_id))
    achive = result.scalar_one_or_none()
    
    if not achive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Достижение не найдено"
        )
    
    update_data = achive_data.model_dump(exclude_unset=True)
    
    if "title" in update_data:
        result = await db.execute(
            select(Achievement).where(
                Achievement.title == update_data["title"],
                Achievement.id != achive_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Достижение с таким названием уже существует"
            )
    
    for field, value in update_data.items():
        setattr(achive, field, value)
    
    try:
        await db.commit()
        await db.refresh(achive)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при обновлении достижения"
        )
    
    return achive

@router.delete("/achievements/{achive_id}")
async def achive_delete(
    achive_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Удаление достижения
    """
    result = await db.execute(select(Achievement).where(Achievement.id == achive_id))
    achive = result.scalar_one_or_none()

    if not achive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Достижение не найдено"
        )
    
    try:
        await db.delete(achive)
        await db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при удалении достижения"
        )
    
    return achive

@router.post("/directions")
async def direction_create(
    direction_data: DirectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Создание нового направления
    """
    result = await db.execute(
        select(Direction).where(Direction.name == direction_data.name)
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Направление с таким названием уже существует"
        )
    
    direction = Direction(**direction_data.model_dump())

    try:
        db.add(direction)
        await db.commit()
        await db.refresh(direction)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании направления"
        )
    
    return direction


@router.put("/directions/{direction_id}")
async def direction_update(
    direction_id: int,
    direction_data: DirectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Обновление направления
    """
    result = await db.execute(
        select(Direction).where(Direction.id == direction_id)
    )
    direction = result.scalar_one_or_none()
    
    if not direction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Направление не найдено"
        )
    
    update_data = direction_data.model_dump(exclude_unset=True)
    
    if "name" in update_data:
        result = await db.execute(
            select(Direction).where(
                Direction.name == update_data["name"],
                Direction.id != direction_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Направление с таким названием уже существует"
            )
    
    for field, value in update_data.items():
        setattr(direction, field, value)
    
    try:
        await db.commit()
        await db.refresh(direction)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при обновлении направления"
        )
    
    return direction

@router.delete("/directions/{direction_id}")
async def direction_delete(
    direction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Удаление направления (с каскадным удалением дисциплин)
    """
    result = await db.execute(
        select(Direction).where(Direction.id == direction_id)
    )
    direction = result.scalar_one_or_none()

    if not direction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Направление не найдено"
        )
    result = await db.execute(
        select(func.count(Discipline.id)).where(Discipline.direction_id == direction_id)
    )
    discipline_count = result.scalar()
    
    try:
        await db.delete(direction)
        await db.commit()
        return {
            "message": "Направление успешно удалено",
            "deleted_disciplines_count": discipline_count
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при удалении направления: {str(e)}"
        )


@router.post("/disciplines")
async def discipline_create(
    discipline_data: DisciplineCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Создание новой дисциплины
    """
    result = await db.execute(
        select(Discipline).where(Discipline.name == discipline_data.name)
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дисциплина с таким названием уже существует"
        )

    result = await db.execute(
        select(Direction).where(Direction.id == discipline_data.direction_id)
    )
    direction = result.scalar_one_or_none()
    
    if not direction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Указанное направление не существует"
        )
    
    if discipline_data.start_term > discipline_data.end_term:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начальный семестр не может быть больше конечного"
        )
    
    discipline = Discipline(**discipline_data.model_dump())

    try:
        db.add(discipline)
        await db.commit()
        await db.refresh(discipline)
        await db.refresh(direction)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании дисциплины"
        )
    
    return discipline

@router.put("/disciplines/{discipline_id}")
async def discipline_update(
    discipline_id: int,
    discipline_data: DisciplineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Обновление дисциплины
    """
    result = await db.execute(
        select(Discipline).where(Discipline.id == discipline_id)
    )
    discipline = result.scalar_one_or_none()
    
    if not discipline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Дисциплина не найдена"
        )
    
    update_data = discipline_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        result = await db.execute(
            select(Discipline).where(
                Discipline.name == update_data["name"],
                Discipline.id != discipline_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дисциплина с таким названием уже существует"
            )

    if "direction_id" in update_data:
        result = await db.execute(
            select(Direction).where(Direction.id == update_data["direction_id"])
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Указанное направление не существует"
            )
        
    start_term = update_data.get("start_term", discipline.start_term)
    end_term = update_data.get("end_term", discipline.end_term)
    
    if start_term > end_term:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начальный семестр не может быть больше конечного"
        )
    
    for field, value in update_data.items():
        setattr(discipline, field, value)
    
    try:
        await db.commit()
        await db.refresh(discipline)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при обновлении дисциплины"
        )
    
    return discipline


@router.delete("/disciplines/{discipline_id}")
async def discipline_delete(
    discipline_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Удаление дисциплины
    """
    result = await db.execute(
        select(Discipline).where(Discipline.id == discipline_id)
    )
    discipline = result.scalar_one_or_none()

    if not discipline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Дисциплина не найдена"
        )
    
    try:
        await db.delete(discipline)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при удалении дисциплины: {str(e)}"
        )
    
    return discipline




@router.post("/teacher")
async def teacher_create(
    teacher_data: TeacherCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Создание нового преподавателя.
    """
    result = await db.execute(select(Teacher).where(Teacher.fio == teacher_data.fio))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Преподаватель с таким ФИО уже существует"
        )
    
    teacher = (Teacher(**teacher_data.model_dump()))

    try:
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании преподавателя"
        )
    
    return teacher
    
@router.put("/teacher/{teacher_id}")
async def teacher_update(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Обновление данных о преподавателе.
    """
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )
    
    update_data = teacher_data.model_dump(exclude_unset=True)
    
    if "fio" in update_data:
        result = await db.execute(
            select(Teacher).where(
                Teacher.fio == update_data["fio"],
                Teacher.id != teacher_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Преподаватель уже существует"
            )
    
    for field, value in update_data.items():
        setattr(teacher, field, value)
    
    try:
        await db.commit()
        await db.refresh(teacher)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при обновлении данных"
        )
    
    return teacher

@router.delete("/teacher/{teacher_id}")
async def teacher_delete(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Удаление преподавателя.
    """
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )
    
    try:
        await db.delete(teacher)
        await db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при удалении"
        )
    
    return teacher