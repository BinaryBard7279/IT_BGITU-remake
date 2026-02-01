from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.user import User
from app.models.speciality import Speciality
from app.models.feature import Feature
from app.models.plan import Track, Direction, Discipline
from app.models.teacher import Teacher
from app.models.subject import Subject

__all__ = [
    "Base",
    "User",
    "Speciality",
    "Feature",
    "Track",
    "Direction",
    "Discipline",
    "Teacher",
    "Subject",
]
