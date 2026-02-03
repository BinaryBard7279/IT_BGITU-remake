# app/schemas/__init__.py
from .feature import (FeatureBase, FeatureCreate, FeatureUpdate, Feature)

from .plan import (TrackBase, TrackCreate, TrackUpdate, Track, DirectionBase, DirectionCreate, DirectionUpdate, Direction, DisciplineBase, DisciplineCreate, DisciplineUpdate, Discipline, Direction_Disciplines, Track_Directions)
from .speciality import (SpecialityBase, SpecialityCreate, SpecialityUpdate, Speciality, Speciality_Features)
from .subject import (SubjectBase, SubjectCreate, SubjectUpdate, Subject)
from .teacher import (TeacherBase, TeacherCreate, TeacherUpdate, Teacher)
from .user import (UserBase, User)
from .auth import (Token, TokenData, LoginRequest)

from .health_check import HealthCheck

__all__ = [
    # Feature
    'FeatureBase', 'FeatureCreate', 'FeatureUpdate', 'Feature',
    
    # Plan
    'TrackBase', 'TrackCreate', 'TrackUpdate', 'Track',
    'DirectionBase', 'DirectionCreate', 'DirectionUpdate', 'Direction',
    'DisciplineBase', 'DisciplineCreate', 'DisciplineUpdate', 'Discipline',
    'Direction_Disciplines', 'Track_Directions',
    
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

    # Health Check
    'HealthCheck',
]