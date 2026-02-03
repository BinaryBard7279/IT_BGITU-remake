from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class SubjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=225)
    description: str = Field(..., min_length=1)

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=225)
    description: Optional[str] = Field(None, min_length=1)

class Subject(SubjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., gt=0)