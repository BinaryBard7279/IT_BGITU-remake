from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# Track
class TrackBase(BaseModel):
    name: str

class TrackCreate(TrackBase):
    pass

class TrackUpdate(BaseModel):
    name: Optional[str] = None

class Track(TrackBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# Direction
class DirectionBase(BaseModel):
    name: str
    track_id: int

class DirectionCreate(DirectionBase):
    pass

class DirectionUpdate(BaseModel):
    name: Optional[str] = None
    track_id: Optional[int] = None

class Direction(DirectionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# Discipline
class DisciplineBase(BaseModel):
    name: str
    start_term: int
    end_term: int
    direction_id: int

class DisciplineCreate(DisciplineBase):
    pass

class DisciplineUpdate(BaseModel):
    name: Optional[str] = None
    start_term: Optional[int] = None
    end_term: Optional[int] = None
    direction_id: Optional[int] = None

# шаблон для ответов API
class Discipline(DisciplineBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# для вывода вложенных данных
class Direction_Disciplines(Direction): # наследуем
    disciplines: List[Discipline] = []  # добавляем

class Track_Directions(Track):
    directions: List[Direction_Disciplines] = []