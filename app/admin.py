# app/admin.py
import io
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import Request

# --- НОВЫЕ ИМПОРТЫ ДЛЯ ОПТИМИЗАЦИИ ФОТО ---
from PIL import Image
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from wtforms import FileField, PasswordField, StringField, TextAreaField

from app.database import AsyncSessionLocal, engine
from app.models import (
    Achievement,
    Direction,
    Discipline,
    Faq,
    Feature,
    Setting,
    Speciality,
    Subject,
    Teacher,
    TimelineStep,
    User,
)
from app.security import get_password_hash, verify_password


# --- AUTHENTICATION ---
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form.get("username"), form.get("password")

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

admin_secret_key = os.getenv("SECRET_KEY", "dev-admin-secret-key")
authentication_backend = AdminAuth(secret_key=admin_secret_key)

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
        "image_url": {
            "label": "Фотография",
            "render_kw": {"accept": "image/*"}
        },
        "subjects": {
            "label": "Предметы (вводите через запятую)",
            "render_kw": {"class": "form-control", "rows": 3}
        }
    }

    column_formatters = {
        Teacher.image_url: lambda m, a: f'<img src="{m.image_url}" width="50" style="border-radius: 5px; object-fit: cover;">' if m.image_url else "Нет фото"
    }

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        input_file = data.get("image_url")
        if input_file and hasattr(input_file, "filename") and input_file.filename:
            # --- ЗАЩИТА ОТ ДЕКОМПРЕССИОННЫХ БОМБ И OOM (Limit 5MB) ---
            # Читаем максимум 5МБ + 1 байт для проверки
            max_size = 5 * 1024 * 1024
            image_bytes = await input_file.read(max_size + 1)

            if len(image_bytes) > max_size:
                raise ValueError("Файл слишком большой! Максимальный размер — 5МБ.")

            # --- УДАЛЕНИЕ СТАРОГО ФАЙЛА ПРИ ОБНОВЛЕНИИ ---
            if not is_created and model.image_url:
                # Превращаем URL /media/name.webp в путь app/uploads/name.webp
                old_relative_path = model.image_url.lstrip("/")
                if old_relative_path.startswith("media/"):
                    old_file_path = Path("app/uploads") / old_relative_path.replace("media/", "", 1)
                    if old_file_path.exists():
                        try:
                            old_file_path.unlink()
                        except Exception:
                            pass # Логируем ошибку, если нужно, но не прерываем процесс

            # Открываем изображение через Pillow
            img = Image.open(io.BytesIO(image_bytes))

            # Конвертируем в RGB (убираем альфа-канал, если это PNG, для корректного сжатия)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Пропорциональный ресайз (максимум 720x720 px)
            img.thumbnail((720, 720), Image.Resampling.LANCZOS)

            # Сохраняем в формате WebP
            unique_filename = f"{uuid.uuid4()}.webp"
            save_directory = Path("app/uploads")
            save_directory.mkdir(parents=True, exist_ok=True)
            save_path = save_directory / unique_filename

            # Сохраняем с оптимизацией
            img.save(save_path, format="WEBP", quality=80, method=6)

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

    async def on_model_delete(self, model: Any, request: Request) -> None:
        """Удаляет файл с диска при удалении записи преподавателя"""
        if model.image_url:
            relative_path = model.image_url.lstrip("/")
            if relative_path.startswith("media/"):
                file_path = Path("app/uploads") / relative_path.replace("media/", "", 1)
                if file_path.exists():
                    try:
                        file_path.unlink()
                    except Exception:
                        pass

class DisciplineInline(ModelView, model=Discipline):
    column_list = [Discipline.name, Discipline.group, Discipline.start_term, Discipline.end_term]

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

class DisciplineAdmin(ModelView, model=Discipline):
    name = "Дисциплина"
    name_plural = "Все дисциплины"
    icon = "fa-solid fa-book"

    column_list = [
        Discipline.id,
        Discipline.name,
        Discipline.group,
        Discipline.direction,
        Discipline.start_term
    ]

    column_labels = {
        Discipline.id: "ID",
        Discipline.name: "Название",
        Discipline.group: "Группа",
        Discipline.direction: "Направление",
        Discipline.start_term: "Начало (сем.)",
        Discipline.end_term: "Конец (сем.)"
    }

    form_columns = [
        Discipline.name,
        Discipline.direction,
        Discipline.group,
        Discipline.start_term,
        Discipline.end_term
    ]

    column_searchable_list = [Discipline.name, Discipline.group]
    column_sortable_list = [Discipline.name, Discipline.start_term, Discipline.direction_id]

class DirectionAdmin(ModelView, model=Direction):
    name = "Направление (План)"
    name_plural = "Направления (План)"
    icon = "fa-solid fa-route"

    column_list = [Direction.id, Direction.name]
    column_labels = {Direction.id: "ID", Direction.name: "Название направления"}

    inline_models = [DisciplineInline]

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


class FaqAdmin(ModelView, model=Faq):
    name = "Вопрос-ответ (FAQ)"
    name_plural = "Вопросы-ответы (FAQ)"
    icon = "fa-solid fa-circle-question"

    column_list = [Faq.question]
    column_labels = {Faq.question: "Вопрос", Faq.answer: "Ответ"}
    form_overrides = {"answer": TextAreaField}


class SettingAdmin(ModelView, model=Setting):
    name = "Текст сайта (Настройки)"
    name_plural = "Тексты сайта (Настройки)"
    icon = "fa-solid fa-gear"

    column_list = [Setting.key, Setting.description, Setting.value]
    column_labels = {Setting.key: "Ключ (обязательно на англ, напр: hero_title)", Setting.value: "Значение (Текст)", Setting.description: "Описание для вас"}
    form_overrides = {"value": TextAreaField}
    column_searchable_list = [Setting.key, Setting.description]

class TimelineStepAdmin(ModelView, model=TimelineStep):
    name = "Этап обучения (Timeline)"
    name_plural = "Этапы обучения (Timeline)"
    icon = "fa-solid fa-stream"

    column_list = [TimelineStep.order, TimelineStep.term, TimelineStep.title]
    column_labels = {
        TimelineStep.order: "Порядок (1, 2, 3...)",
        TimelineStep.term: "Семестры",
        TimelineStep.title: "Заголовок",
        TimelineStep.description: "Описание",
        TimelineStep.color_class: "Цвет"
    }
    form_overrides = {"description": TextAreaField}
    form_args = {
        "color_class": {"label": "CSS класс цвета (bg-pastel-sky, bg-pastel-mint, bg-pastel-peach, bg-pastel-lavender)"}
    }
    column_sortable_list = [TimelineStep.order]


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
    admin.add_view(FaqAdmin)
    admin.add_view(TimelineStepAdmin)
    admin.add_view(SettingAdmin)
