from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List

class TeacherBase(BaseModel):
    fio: str = Field(..., min_length=1, max_length=100)
    post: str = Field(..., min_length=1, max_length=100)
    subjects: List[str] = Field(..., min_items=1, max_items=100)
    image_url: str = Field(...)

class TeacherCreate(TeacherBase):
    pass

class TeacherUpdate(BaseModel):
    fio: Optional[str] = Field(None, min_length=5, max_length=100)
    post: Optional[str] = Field(None, min_length=3, max_length=100)
    subjects: Optional[List[str]] = Field(None, min_items=1, max_items=100)
    image_url: Optional[str] = Field(None)

class Teacher(TeacherBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., gt=0)