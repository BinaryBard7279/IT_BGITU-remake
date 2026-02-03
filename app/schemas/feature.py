from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class FeatureBase(BaseModel):
    subtitle: str = Field(..., min_length=1, max_length=225)
    description: str =  Field(..., min_length=1)
    speciality_id: int =  Field(..., gt=0)

class FeatureUpdate(BaseModel):
    subtitle: Optional[str] = Field(None, min_length=1,  max_length=225)
    description: Optional[str] = Field(None, min_length=1)
    speciality_id: Optional[int] = Field(None, gt=0)

class FeatureCreate(FeatureBase):
    pass

class FeatureRead(FeatureBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., gt=0)