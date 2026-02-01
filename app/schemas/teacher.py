from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class TeacherBase(BaseModel):
    image_url: str
    fio: str
    post: str
    subjects: List[str]

class TeacherCreate(TeacherBase):
    pass

class TeacherUpdate(BaseModel):
    image_url: Optional[str] = None
    fio: Optional[str] = None
    post: Optional[str] = None
    subjects: Optional[List[str]] = None

class Teacher(TeacherBase):
    model_config = ConfigDict(from_attributes=True)
    id: int