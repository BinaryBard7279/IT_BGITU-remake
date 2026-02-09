from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List

class DirectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class DirectionCreate(DirectionBase):
    pass

class DirectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class Direction(DirectionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class DisciplineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=225)
    start_term: int = Field(..., ge=1, le=12)
    end_term: int = Field(..., ge=1, le=12)
    group: str = Field(default="Общие", min_length=1, max_length=100)
    direction_id: int = Field(..., gt=0)

class DisciplineCreate(DisciplineBase):
    pass

class DisciplineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    start_term: Optional[int] = Field(None, ge=1, le=12)
    end_term: Optional[int] = Field(None, ge=1, le=12)
    direction_id: Optional[int] = Field(None, gt=0)

class Discipline(DisciplineBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., gt=0)


class Direction_Disciplines(Direction):
    disciplines: List[Discipline] = []