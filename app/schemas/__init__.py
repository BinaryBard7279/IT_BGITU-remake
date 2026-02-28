from .achievement import Achievement, AchievementBase
from .feature import Feature, FeatureBase
from .health_check import HealthCheck
from .plan import Direction, Direction_Disciplines, DirectionBase, Discipline, DisciplineBase
from .speciality import Speciality, Speciality_Features, SpecialityBase
from .subject import Subject, SubjectBase
from .teacher import Teacher, TeacherBase
from .user import User, UserBase
from .faq import Faq, FaqBase

__all__ = [
    # Feature
    'FeatureBase', 'Feature',

    # Plan
    'DirectionBase', 'Direction',
    'DisciplineBase', 'Discipline',
    'Direction_Disciplines',

    # Speciality
    'SpecialityBase', 'Speciality',
    'Speciality_Features',

    # Subject
    'SubjectBase', 'Subject',

    # Teacher
    'TeacherBase', 'Teacher',

    # User
    'UserBase', 'User',

    # Achievement
    'AchievementBase', 'Achievement',

    # Faq
    'FaqBase', 'Faq',

    # Health Check
    'HealthCheck',
]
