# app/schemas/feature.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class FeatureBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=225)
    description: str = Field(..., min_length=1)
    svg_code: Optional[str] = None

class FeatureUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=225)
    description: Optional[str] = Field(None, min_length=1)
    svg_code: Optional[str] = None

class FeatureCreate(FeatureBase):
    pass

class Feature(FeatureBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., gt=0)