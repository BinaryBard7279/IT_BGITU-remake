from pydantic import BaseModel, ConfigDict, Field


class LifeEventBase(BaseModel):
    title: str = Field(..., min_length=1)
    tag: str = Field(..., min_length=1)
    image_url: str = Field(..., min_length=1)
    is_main: bool = Field(default=False)
    order: int = Field(default=0)


class LifeEvent(LifeEventBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., gt=0)
