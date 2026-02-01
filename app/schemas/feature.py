from pydantic import BaseModel, ConfigDict
from typing import Optional

class FeatureBase(BaseModel):
    subtitle: str
    description: str
    speciality_id: int

class FeatureUpdate(BaseModel):
    subtitle: Optional[str] = None
    description: Optional[str] = None
    speciality_id: Optional[int] = None

class Feature(FeatureBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    speciality_id: int