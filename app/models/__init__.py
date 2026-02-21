from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.user import User
from app.models.speciality import Speciality
from app.models.feature import Feature
from app.models.plan import Direction, Discipline
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.achievement import Achievement

__all__ = [
    "Base",
    "User",
    "Speciality",
    "Feature",
    "Direction",
    "Discipline",
    "Teacher",
    "Subject",
    "Achievement",
]
