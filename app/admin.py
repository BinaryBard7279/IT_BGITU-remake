import os
import uuid
import aiofiles
from pathlib import Path
from typing import Any

from fastapi import Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from wtforms import PasswordField, TextAreaField, StringField, FileField

from app.database import engine, AsyncSessionLocal # ОПТИМИЗАЦИЯ: Импорт менеджера сессий
from app.models import User, Speciality, Feature, Direction, Discipline, Teacher, Subject, Achievement
from app.security import verify_password, get_password_hash

# --- AUTHENTICATION ---
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form.get("username"), form.get("password")

        # ОПТИМИЗАЦИЯ: Изолируем сессию для предотвращения утечки пула соединений БД
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

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


# --- BASE VIEW (DRY ОПТИМИЗАЦИЯ) ---
class BaseAdminView(ModelView):
    """
    Базовый класс для всех моделей админки. 
    Централизует настройки пагинации и другие общие параметры.
    """
    page_size = 50


# --- VIEWS ---
class UserAdmin(BaseAdminView, model=User):
    name = "Администратор"
    name_plural = "Администраторы"
    icon = "fa-solid fa-user-shield"
    
    column_list = [User.id, User.name, User.email]
    column_labels = {User.id: "ID", User.name: "Имя", User.email: "Email", User.hashed_password: "Хэш пароля"}
    column_details_exclude_list = [User.hashed_password]
    form_columns = [User.name, User.email, User.hashed_password]
    
    form_overrides = {"hashed_password": PasswordField}
    form_args = {"hashed_password": {"label": "Пароль (оставьте пустым, если не меняете)"}}

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        password = data.get("hashed_password")
        if password:
            data["hashed_password"] = get_password_hash(password)
        elif not is_created and "hashed_password" in data:
            del data["hashed_password"]

class SpecialityAdmin(BaseAdminView, model=Speciality):
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

class FeatureAdmin(BaseAdminView, model=Feature):
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
    form_args = {"svg_code": {"label": "Класс иконки FontAwesome (например: fa-solid fa-code)"}}

class TeacherAdmin(BaseAdminView, model=Teacher):
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

    form_overrides = {
        "subjects": TextAreaField,
        "image_url": FileField
    }

    form_args = {
        "image_url": {"label": "Фотография", "render_kw": {"accept": "image/*"}},
        "subjects": {"label": "Предметы (вводите через запятую)", "render_kw": {"class": "form-control", "rows": 3}}
    }

    column_formatters = {
        Teacher.image_url: lambda m, a: f'<img src="{m.image_url}" width="50" style="border-radius: 5px; object-fit: cover;">' if m.image_url else "Нет фото"
    }

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        input_file = data.get("image_url")
        if input_file and hasattr(input_file, "filename") and input_file.filename:
            extension = input_file.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{extension}"
            save_directory = Path("app/uploads")
            save_directory.mkdir(parents=True, exist_ok=True)
            save_path = save_directory / unique_filename
            
            # ОПТИМИЗАЦИЯ: Асинхронное сохранение файла, чтобы не блокировать Event Loop
            async with aiofiles.open(save_path, "wb") as buffer:
                while content := await input_file.read(1024 * 1024):
                    await buffer.write(content)
                    
            data["image_url"] = f"/media/{unique_filename}"
        else:
            if is_created:
                data["image_url"] = ""
            elif "image_url" in data:
                del data["image_url"]

        subjects_input = data.get("subjects")
        if isinstance(subjects_input, str):
            clean_text = subjects_input.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
            data["subjects"] = [s.strip() for s in clean_text.split(",") if s.strip()]

class DisciplineInline(BaseAdminView, model=Discipline):
    column_list = [Discipline.name, Discipline.group, Discipline.start_term, Discipline.end_term]
    form_columns = [Discipline.name, Discipline.group, Discipline.start_term, Discipline.end_term]
    column_labels = {
        Discipline.name: "Дисциплина",
        Discipline.group: "Группа (Общие/Спец)",
        Discipline.start_term: "С семестра",
        Discipline.end_term: "По семестр"
    }

class DisciplineAdmin(BaseAdminView, model=Discipline):
    name = "Дисциплина"
    name_plural = "Все дисциплины"
    icon = "fa-solid fa-book"

    column_list = [Discipline.id, Discipline.name, Discipline.group, Discipline.direction, Discipline.start_term]
    column_labels = {
        Discipline.id: "ID",
        Discipline.name: "Название",
        Discipline.group: "Группа",
        Discipline.direction: "Направление",
        Discipline.start_term: "Начало (сем.)",
        Discipline.end_term: "Конец (сем.)"
    }
    form_columns = [Discipline.name, Discipline.direction, Discipline.group, Discipline.start_term, Discipline.end_term]
    column_searchable_list = [Discipline.name, Discipline.group]
    column_sortable_list = [Discipline.name, Discipline.start_term, Discipline.direction_id]

class DirectionAdmin(BaseAdminView, model=Direction):
    name = "Направление (План)"
    name_plural = "Направления (План)"
    icon = "fa-solid fa-route"

    column_list = [Direction.id, Direction.name]
    column_labels = {Direction.id: "ID", Direction.name: "Название направления"}
    inline_models = [DisciplineInline]

class SubjectAdmin(BaseAdminView, model=Subject):
    name = "Технология (Стек)"
    name_plural = "Технологии (Стек)"
    icon = "fa-solid fa-layer-group"
    
    column_list = [Subject.name, Subject.svg_code]
    column_labels = {Subject.name: "Название", Subject.description: "Описание", Subject.svg_code: "Иконка"}
    form_args = {"svg_code": {"label": "Класс иконки FontAwesome (например: fa-brands fa-python)"}}

class AchievementAdmin(BaseAdminView, model=Achievement):
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
    )
    
    admin.add_view(UserAdmin)
    admin.add_view(SpecialityAdmin)
    admin.add_view(DirectionAdmin) 
    admin.add_view(DisciplineAdmin)
    admin.add_view(TeacherAdmin)
    admin.add_view(FeatureAdmin)
    admin.add_view(SubjectAdmin)
    admin.add_view(AchievementAdmin)