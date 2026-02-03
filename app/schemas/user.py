from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=225)  
    email: EmailStr = Field(..., max_length=255)
    
class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., gt=0)
