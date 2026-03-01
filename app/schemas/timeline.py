from pydantic import BaseModel, ConfigDict, Field


class TimelineStepBase(BaseModel):
    order: int = Field(..., ge=0)
    term: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=225)
    description: str = Field(..., min_length=1)
    color_class: str = Field(..., min_length=1, max_length=50)

class TimelineStep(TimelineStepBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., gt=0)
