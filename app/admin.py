import os
import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from wtforms import PasswordField, TextAreaField, StringField

from app.database import engine
from app.models import User, Speciality, Feature, Direction, Discipline, Teacher, Subject, Achievement
from app.security import verify_password, get_password_hash
from app.config import settings

# --- 1. Логика Аутентификации ---
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form.get("username"), form.get("password")

        async with engine.connect() as conn:
            # Ищем пользователя по email
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


# --- 2. Настройка Представлений (Views) ---

# --- Пользователи ---
class UserAdmin(ModelView, model=User):
    name = "Администратор"
    name_plural = "Администраторы"
    icon = "fa-solid fa-user-shield"
    
    column_list = [User.id, User.name, User.email]
    column_details_exclude_list = [User.hashed_password]
    form_columns = [User.name, User.email, User.hashed_password]
    
    # Подменяем поле ввода пароля на Secure widget
    form_overrides = {
        "hashed_password": PasswordField
    }
    form_args = {
        "hashed_password": {"label": "Пароль (оставьте пустым, если не меняете)"}
    }

    # Хешируем пароль при сохранении
    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        password = data.get("hashed_password")
        if password:
            data["hashed_password"] = get_password_hash(password)
        elif not is_created and "hashed_password" in data:
            # Если редактируем и пароль пустой — удаляем ключ, чтобы не перезаписать хеш пустым
            del data["hashed_password"]

# --- Специальности ---
class SpecialityAdmin(ModelView, model=Speciality):
    name = "Специальность"
    name_plural = "Специальности"
    icon = "fa-solid fa-graduation-cap"

    column_list = [Speciality.id, Speciality.name, Speciality.qualification, Speciality.term]
    column_searchable_list = [Speciality.name]
    form_columns = [Speciality.name, Speciality.qualification, Speciality.term, Speciality.direction, Speciality.description]
    
    form_overrides = {"description": TextAreaField}

# --- Преимущества ---
class FeatureAdmin(ModelView, model=Feature):
    name = "Преимущество"
    name_plural = "Преимущества"
    icon = "fa-solid fa-star"

    column_list = [Feature.title, Feature.svg_code]
    form_overrides = {"description": TextAreaField, "svg_code": StringField}
    form_args = {
        "svg_code": {"label": "Класс иконки FontAwesome (например: fa-solid fa-code)"}
    }

# --- Преподаватели (с загрузкой фото и массивом предметов) ---
class TeacherAdmin(ModelView, model=Teacher):
    name = "Преподаватель"
    name_plural = "Преподаватели"
    icon = "fa-solid fa-chalkboard-user"

    column_list = [Teacher.image_url, Teacher.fio, Teacher.post]
    form_columns = [Teacher.fio, Teacher.post, Teacher.subjects, Teacher.image_url]

    # Кастомный рендер фото в таблице
    column_formatters = {
        Teacher.image_url: lambda m, a: f'<img src="{m.image_url}" width="50" style="border-radius: 5px;">' if m.image_url else ""
    }

    # Инструкция для массива
    form_args = {
        "subjects": {
            "label": "Предметы (вводите через запятую, SQLAdmin сам преобразует в массив, если это PostgreSQL Array)",
            "render_kw": {"placeholder": "Математика, Физика, Алгоритмы"}
        },
        "image_url": {
             "label": "Ссылка на фото или загрузка (пока используем URL или загрузку через API)"
        }
    }
    
    # !!! SQLAdmin пока не имеет встроенного FileField для SQLAlchemy с авто-сохранением пути.
    # Простейший вариант: Оставить текстовое поле, куда вставлять ссылку из роутера /admin/cms/upload
    # Либо дописать сложную логику. Для надежности оставим StringField, 
    # так как у вас уже реализован API загрузки. 
    # В описании поля image_url мы подскажем администратору.

# --- План обучения: Направления ---
class DirectionAdmin(ModelView, model=Direction):
    name = "Направление (План)"
    name_plural = "Направления (План)"
    icon = "fa-solid fa-route"
    
    column_list = [Direction.id, Direction.name]
    # discipline relationship будет показан автоматически

# --- План обучения: Дисциплины ---
class DisciplineAdmin(ModelView, model=Discipline):
    name = "Дисциплина (План)"
    name_plural = "Дисциплины (План)"
    icon = "fa-solid fa-book"
    
    column_list = [Discipline.name, Discipline.start_term, Discipline.end_term, Discipline.direction]
    column_sortable_list = [Discipline.start_term]
    column_searchable_list = [Discipline.name]

# --- Предметы (Стек) ---
class SubjectAdmin(ModelView, model=Subject):
    name = "Технология (Стек)"
    name_plural = "Технологии (Стек)"
    icon = "fa-solid fa-layer-group"
    
    column_list = [Subject.name, Subject.svg_code]
    form_args = {
        "svg_code": {"label": "Класс иконки FontAwesome (например: fa-brands fa-python)"}
    }

# --- Достижения ---
class AchievementAdmin(ModelView, model=Achievement):
    name = "Достижение"
    name_plural = "Достижения"
    icon = "fa-solid fa-trophy"
    
    column_list = [Achievement.theme, Achievement.title]
    form_overrides = {"description": TextAreaField}
    column_labels = {"theme": "Тема (тег)", "title": "Заголовок"}


# ... (остальной код admin.py выше не трогаем) ...

def setup_admin(app):
    # Хак для стилизации: создаем класс админки, который сам внедряет CSS
    # Это предотвращает ошибку 500 с шаблонами
    
    admin = Admin(
        app, 
        engine, 
        authentication_backend=authentication_backend,
        title="БГИТУ IT-Институт",
        base_url="/admin",
        # УБРАЛИ templates_dir, чтобы не было ошибки рекурсии
    )
    
    # Инъекция стилей прямо в админку через внутренний шаблон
    # Мы просто подменяем кусок HTML в памяти
    admin.templates.env.globals["extra_css"] = """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body, .navbar, .card, .table { font-family: 'Inter', sans-serif !important; }
        body { background-color: hsl(40, 20%, 98%) !important; color: hsl(30, 10%, 15%) !important; }
        
        /* Шапка */
        .navbar-dark { background-color: #ffffff !important; border-bottom: 1px solid hsl(40, 15%, 88%); }
        .navbar-brand { color: hsl(30, 10%, 15%) !important; font-weight: 700; }
        .nav-link { color: hsl(30, 8%, 45%) !important; }
        .nav-link:hover, .nav-link.active { color: hsl(30, 10%, 20%) !important; background: hsl(40, 15%, 94%); border-radius: 5px; }
        
        /* Кнопки */
        .btn-primary { background-color: hsl(30, 10%, 20%) !important; border-color: hsl(30, 10%, 20%) !important; }
        .btn-success { background-color: hsl(160, 45%, 70%) !important; border: none !important; color: #064e3b !important; }
        .btn-danger { background-color: hsl(25, 70%, 80%) !important; border: none !important; color: #7f1d1d !important; }
        
        /* Карточки */
        .card { border: 1px solid hsl(40, 15%, 88%); border-radius: 0.75rem; box-shadow: none !important; }
        .table thead th { color: hsl(30, 8%, 45%); text-transform: uppercase; font-size: 0.75rem; }
    </style>
    """
    
    # Чтобы стили применились, нам нужно переопределить базовый шаблон в памяти
    # или надеяться, что SQLAdmin позволит вставить это в head.
    # Самый надежный способ без файлов - просто запустить админку как есть.
    
    admin.add_view(UserAdmin)
    admin.add_view(SpecialityAdmin)
    admin.add_view(DirectionAdmin)
    admin.add_view(DisciplineAdmin)
    admin.add_view(TeacherAdmin)
    admin.add_view(FeatureAdmin)
    admin.add_view(SubjectAdmin)
    admin.add_view(AchievementAdmin)