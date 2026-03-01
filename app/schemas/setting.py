from pydantic import BaseModel, ConfigDict, Field


class SettingBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)

class Setting(SettingBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., gt=0)
