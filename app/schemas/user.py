from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    name = str    
    email = EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
