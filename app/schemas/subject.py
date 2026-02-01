from pydantic import BaseModel, ConfigDict
from typing import Optional

class SubjectBase(BaseModel):
    name: str
    description: str

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Subject(SubjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: int