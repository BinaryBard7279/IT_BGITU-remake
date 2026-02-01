from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from .feature import Feature

class SpecialityBase(BaseModel):
    name: str
    qualification: str
    term: int
    direction: str
    description: str
    image_url: str

class SpecialityCreate(SpecialityBase):
    pass

class SpecialityUpdate(BaseModel):
    name: Optional[str] = None
    qualification: Optional[str] = None
    term: Optional[int] = None
    direction: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class Speciality(SpecialityBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class Speciality_Features(Speciality): # получить специальности и особенности
    features: List[Feature] = []