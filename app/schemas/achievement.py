from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class AchievementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=225)
    theme: str = Field(..., min_length=1, max_length=225)
    description: str =  Field(..., min_length=1)

class AchievementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=225)
    theme: Optional[str] = Field(None, min_length=1, max_length=225)
    description: Optional[str] = Field(None, min_length=1)

class AchievementCreate(AchievementBase):
    pass

class Achievement(AchievementBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., gt=0)