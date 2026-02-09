import os
import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from wtforms import PasswordField, TextAreaField, StringField, FileField

from app.database import engine
from app.models import User, Speciality, Feature, Direction, Discipline, Teacher, Subject, Achievement
from app.security import verify_password, get_password_hash

# --- CONFIG & UTILS ---

# Путь для сохранения картинок (согласован с твоим Docker volume)
UPLOAD_DIR = Path("app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_file_from_form(file_storage) -> str | None:
    """
    Сохраняет файл, пришедший из формы WTForms/SQLAdmin.
    Возвращает веб-путь (/media/filename.ext) или None.
    """
    if not file_storage or not hasattr(file_storage, "filename"):
        return None
    
    filename = file_storage.filename
    if not filename:
        return None

    # Генерируем уникальное имя, чтобы не затереть старые файлы
    extension = filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{extension}"
    file_path = UPLOAD_DIR / unique_name
    
    # Сохраняем на диск
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file_storage.file, f)
        return f"/media/{unique_name}"
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

# --- AUTHENTICATION ---

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form.get("username"), form.get("password")

        async with engine.connect() as conn:
            stmt = select(User).where(User.email == email)
            result = await conn.execute(stmt)
            user = result.fetchone()

        if user and verify_password(password, user.hashed_password):
            request.session.update({"token": str(user.id)})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "token" in request.session

authentication_backend = AdminAuth(secret_key=os.getenv("SECRET_KEY", "supersecret"))

# --- VIEWS ---

class UserAdmin(ModelView, model=User):
    name = "Администратор"
    name_plural = "Администраторы"
    icon = "fa-solid fa-user-shield"
    
    column_list = [User.id, User.name, User.email]
    form_columns = [User.name, User.email, User.hashed_password]
    
    form_overrides = { "hashed_password": PasswordField }
    form_args = { "hashed_password": {"label": "Пароль (оставьте пустым, если не меняете)"} }

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        password = data.get("hashed_password")
        if password:
            data["hashed_password"] = get_password_hash(password)
        elif not is_created and "hashed_password" in data:
            del data["hashed_password"]

class TeacherAdmin(ModelView, model=Teacher):
    name = "Преподаватель"
    name_plural = "Преподаватели"
    icon = "fa-solid fa-chalkboard-user"

    column_list = [Teacher.image_url, Teacher.fio, Teacher.post]
    form_columns = [Teacher.fio, Teacher.post, Teacher.subjects, Teacher.image_url]

    column_labels = {
        Teacher.image_url: "Фото",
        Teacher.fio: "ФИО",
        Teacher.post: "Должность",
        Teacher.subjects: "Предметы"
    }

    # Говорим админке, что это поле для файла
    form_overrides = { "image_url": FileField }
    
    form_args = {
        "subjects": {
            "label": "Предметы (вводите через запятую)",
            "render_kw": {"placeholder": "Java, Python, Базы данных"} 
        }
    }

    # Красивый вывод картинки в таблице
    column_formatters = {
        Teacher.image_url: lambda m, a: f'<img src="{m.image_url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;">' if m.image_url else "—"
    }

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        # 1. ЛОГИКА СОХРАНЕНИЯ ФОТО
        file_obj = data.get("image_url")
        saved_path = save_file_from_form(file_obj)
        
        if saved_path:
            data["image_url"] = saved_path
        else:
            # Если файл не выбран при редактировании, удаляем ключ, чтобы не стереть текущий путь в БД
            if not is_created and "image_url" in data:
                del data["image_url"]

        # 2. ЛОГИКА СПИСКА ПРЕДМЕТОВ (String -> Array)
        # Превращаем строку "Математика, Физика" в список ["Математика", "Физика"]
        subjects_raw = data.get("subjects")
        if isinstance(subjects_raw, str):
            clean_list = [s.strip() for s in subjects_raw.split(",") if s.strip()]
            data["subjects"] = clean_list

class SpecialityAdmin(ModelView, model=Speciality):
    name = "Специальность"
    name_plural = "Специальности"
    icon = "fa-solid fa-graduation-cap"
    column_list = [Speciality.name, Speciality.qualification]
    form_overrides = {"description": TextAreaField}

class FeatureAdmin(ModelView, model=Feature):
    name = "Преимущество"
    name_plural = "Преимущества"
    icon = "fa-solid fa-star"
    column_list = [Feature.title, Feature.svg_code]
    form_overrides = {"description": TextAreaField}

class SubjectAdmin(ModelView, model=Subject):
    name = "Технология (Стек)"
    name_plural = "Технологии (Стек)"
    icon = "fa-solid fa-layer-group"
    column_list = [Subject.name, Subject.svg_code]
    form_args = {
        "svg_code": {"label": "Класс иконки FontAwesome (например: fa-brands fa-python)"}
    }

class AchievementAdmin(ModelView, model=Achievement):
    name = "Достижение"
    name_plural = "Достижения"
    icon = "fa-solid fa-trophy"
    column_list = [Achievement.theme, Achievement.title]
    form_overrides = {"description": TextAreaField}

# --- PLAN (Directions + Disciplines) ---

class DisciplineAdmin(ModelView, model=Discipline):
    name = "Дисциплина"
    name_plural = "Дисциплины"
    icon = "fa-solid fa-book"
    
    column_list = [Discipline.name, Discipline.direction, Discipline.start_term, Discipline.group]
    column_sortable_list = [Discipline.start_term, Discipline.direction_id]
    column_searchable_list = [Discipline.name]
    
    form_columns = [
        Discipline.name, 
        Discipline.direction, 
        Discipline.group, 
        Discipline.start_term, 
        Discipline.end_term
    ]

class DirectionAdmin(ModelView, model=Direction):
    name = "Направление"
    name_plural = "Направления"
    icon = "fa-solid fa-route"
    column_list = [Direction.name]
    
    # Inline models временно отключены для стабильности работы AsyncIO
    # inline_models = [DisciplineInline] 

# --- SETUP ---

def setup_admin(app):
    admin = Admin(
        app, 
        engine, 
        authentication_backend=authentication_backend,
        title="БГИТУ IT-Институт",
        base_url="/admin",
        templates_dir="app/templates"
    )
    
    admin.add_view(UserAdmin)
    admin.add_view(SpecialityAdmin)
    admin.add_view(DirectionAdmin)
    admin.add_view(DisciplineAdmin)
    admin.add_view(TeacherAdmin)
    admin.add_view(FeatureAdmin)
    admin.add_view(SubjectAdmin)
    admin.add_view(AchievementAdmin)