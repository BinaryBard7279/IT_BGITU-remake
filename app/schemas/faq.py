from pydantic import BaseModel, ConfigDict, Field

class FaqBase(BaseModel):
    question: str = Field(..., min_length=1, max_length=255)
    answer: str = Field(..., min_length=1)

class Faq(FaqBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., gt=0)