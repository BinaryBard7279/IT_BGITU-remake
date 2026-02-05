from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from .feature import Feature

class SpecialityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=225)
    qualification: str = Field(..., min_length=1, max_length=225)
    term: int = Field(..., ge=1, le=10)
    direction: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    
class SpecialityCreate(SpecialityBase):
    pass

class SpecialityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=225)
    qualification: Optional[str] = Field(None, min_length=1, max_length=225)
    term: Optional[int] = Field(None, ge=1, le=10)
    direction: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)

class Speciality(SpecialityBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., gt=0)

class Speciality_Features(Speciality):
    features: List[Feature] = []