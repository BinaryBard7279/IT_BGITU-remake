from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.achievement import Achievement  # noqa: E402
from app.models.faq import Faq  # noqa: E402
from app.models.feature import Feature  # noqa: E402
from app.models.life_event import LifeEvent  # noqa: E402
from app.models.plan import Direction, Discipline  # noqa: E402
from app.models.setting import Setting  # noqa: E402
from app.models.speciality import Speciality  # noqa: E402
from app.models.subject import Subject  # noqa: E402
from app.models.teacher import Teacher  # noqa: E402
from app.models.timeline import TimelineStep  # noqa: E402
from app.models.user import User  # noqa: E402

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
    "Faq",
    "Setting",
    "TimelineStep",
    "LifeEvent",
]
