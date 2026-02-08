import os
from typing import Any

from fastapi import Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from wtforms import PasswordField, TextAreaField, StringField

from app.database import engine
from app.models import User, Speciality, Feature, Direction, Discipline, Teacher, Subject, Achievement
from app.security import verify_password, get_password_hash

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
    column_labels = {User.id: "ID", User.name: "Имя", User.email: "Email", User.hashed_password: "Хэш пароля"}
    column_details_exclude_list = [User.hashed_password]
    form_columns = [User.name, User.email, User.hashed_password]
    
    form_overrides = {
        "hashed_password": PasswordField
    }
    form_args = {
        "hashed_password": {"label": "Пароль (оставьте пустым, если не меняете)"}
    }

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        password = data.get("hashed_password")
        if password:
            data["hashed_password"] = get_password_hash(password)
        elif not is_created and "hashed_password" in data:
            del data["hashed_password"]

class SpecialityAdmin(ModelView, model=Speciality):
    name = "Специальность"
    name_plural = "Специальности"
    icon = "fa-solid fa-graduation-cap"

    column_list = [Speciality.name, Speciality.qualification, Speciality.term]
    column_labels = {
        Speciality.name: "Название", 
        Speciality.qualification: "Квалификация", 
        Speciality.term: "Срок обучения",
        Speciality.direction: "Направление (текст)",
        Speciality.description: "Описание"
    }
    form_columns = [Speciality.name, Speciality.qualification, Speciality.term, Speciality.direction, Speciality.description]
    form_overrides = {"description": TextAreaField}

class FeatureAdmin(ModelView, model=Feature):
    name = "Преимущество"
    name_plural = "Преимущества"
    icon = "fa-solid fa-star"

    column_list = [Feature.title, Feature.svg_code]
    column_labels = {
        Feature.title: "Заголовок", 
        Feature.description: "Описание", 
        Feature.svg_code: "Иконка (код/класс)"
    }
    form_overrides = {"description": TextAreaField, "svg_code": StringField}
    form_args = {
        "svg_code": {"label": "Класс иконки FontAwesome (например: fa-solid fa-code)"}
    }

class TeacherAdmin(ModelView, model=Teacher):
    name = "Преподаватель"
    name_plural = "Преподаватели"
    icon = "fa-solid fa-chalkboard-user"

    column_list = [Teacher.image_url, Teacher.fio, Teacher.post]
    column_labels = {
        Teacher.image_url: "Фото",
        Teacher.fio: "ФИО",
        Teacher.post: "Должность",
        Teacher.subjects: "Предметы"
    }
    form_columns = [Teacher.fio, Teacher.post, Teacher.subjects, Teacher.image_url]

    column_formatters = {
        Teacher.image_url: lambda m, a: f'<img src="{m.image_url}" width="50" style="border-radius: 5px;">' if m.image_url else ""
    }

    form_overrides = {
        "subjects": TextAreaField
    }
    form_args = {
        "subjects": {
            "label": "Предметы (вводите через запятую)",
            "render_kw": {
                "class": "form-control",
                "rows": 3,
                "style": "width: 100%; min-width: 100%;" 
            }
        },
        "image_url": {"label": "Ссылка на фото"}
    }

# --- ИСПРАВЛЕННЫЙ БЛОК ПЛАНА (Direction + Discipline) ---

class DisciplineInline(ModelView, model=Discipline):
    # Колонки, которые видны в таблице
    column_list = [Discipline.name, Discipline.group, Discipline.start_term, Discipline.end_term]
    
    # Поля, доступные для редактирования. 
    # ВАЖНО: Исключаем direction, чтобы он не просил выбрать родителя вручную
    form_excluded_columns = [Discipline.direction]
    
    form_columns = [
        Discipline.name, 
        Discipline.group, 
        Discipline.start_term, 
        Discipline.end_term
    ]
    
    column_labels = {
        Discipline.name: "Дисциплина",
        Discipline.group: "Группа (Общие/Спец)",
        Discipline.start_term: "С семестра",
        Discipline.end_term: "По семестр"
    }

class DirectionAdmin(ModelView, model=Direction):
    name = "Направление (План)"
    name_plural = "Направления (План)"
    icon = "fa-solid fa-route"
    
    column_list = [Direction.id, Direction.name]
    column_labels = {Direction.id: "ID", Direction.name: "Название направления"}
    
    # ВАЖНО: Я УДАЛИЛ form_columns = [Direction.name]. 
    # Если оставить эту строку, SQLAdmin покажет ТОЛЬКО имя и скроет Inline таблицу.
    
    # Подключаем Inline модель
    inline_models = [DisciplineInline]

# --------------------------------------------------------

class SubjectAdmin(ModelView, model=Subject):
    name = "Технология (Стек)"
    name_plural = "Технологии (Стек)"
    icon = "fa-solid fa-layer-group"
    
    column_list = [Subject.name, Subject.svg_code]
    column_labels = {Subject.name: "Название", Subject.description: "Описание", Subject.svg_code: "Иконка"}
    form_args = {
        "svg_code": {"label": "Класс иконки FontAwesome (например: fa-brands fa-python)"}
    }

class AchievementAdmin(ModelView, model=Achievement):
    name = "Достижение"
    name_plural = "Достижения"
    icon = "fa-solid fa-trophy"
    
    column_list = [Achievement.theme, Achievement.title]
    column_labels = {Achievement.theme: "Тема (тег)", Achievement.title: "Заголовок", Achievement.description: "Описание"}
    form_overrides = {"description": TextAreaField}


# --- SETUP ---

def setup_admin(app):
    admin = Admin(
        app, 
        engine, 
        authentication_backend=authentication_backend,
        title="БГИТУ IT-Институт",
        base_url="/admin",
        logo_url=None,
        templates_dir="app/templates"
    )
    
    admin.add_view(UserAdmin)
    admin.add_view(SpecialityAdmin)
    admin.add_view(DirectionAdmin) 
    admin.add_view(TeacherAdmin)
    admin.add_view(FeatureAdmin)
    admin.add_view(SubjectAdmin)
    admin.add_view(AchievementAdmin)