from .feature import (FeatureBase, FeatureCreate, FeatureUpdate, Feature)

from .plan import (DirectionBase, DirectionCreate, DirectionUpdate, Direction, DisciplineBase, DisciplineCreate, DisciplineUpdate, Discipline, Direction_Disciplines)
from .speciality import (SpecialityBase, SpecialityCreate, SpecialityUpdate, Speciality, Speciality_Features)
from .subject import (SubjectBase, SubjectCreate, SubjectUpdate, Subject)
from .teacher import (TeacherBase, TeacherCreate, TeacherUpdate, Teacher)
from .user import (UserBase, User)
from .auth import (Token, TokenData, LoginRequest)
from .achievement import (AchievementBase, AchievementCreate, AchievementUpdate, Achievement)

from .health_check import HealthCheck

__all__ = [
    # Feature
    'FeatureBase', 'FeatureCreate', 'FeatureUpdate', 'Feature',
    
    # Plan
    'DirectionBase', 'DirectionCreate', 'DirectionUpdate', 'Direction',
    'DisciplineBase', 'DisciplineCreate', 'DisciplineUpdate', 'Discipline',
    'Direction_Disciplines',
    
    # Speciality
    'SpecialityBase', 'SpecialityCreate', 'SpecialityUpdate', 'Speciality',
    'Speciality_Features',
    
    # Subject
    'SubjectBase', 'SubjectCreate', 'SubjectUpdate', 'Subject',
    
    # Teacher
    'TeacherBase', 'TeacherCreate', 'TeacherUpdate', 'Teacher',
    
    # User
    'UserBase', 'User',

    # Auth - только то, что осталось
    'Token', 'TokenData', 'LoginRequest',

    # Achievement
    'AchievementBase', 'AchievementCreate', 'AchievementUpdate', 'Achievement',

    # Health Check
    'HealthCheck',
]