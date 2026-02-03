# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Token(BaseModel):
    access_token: str = Field(..., min_length=1)
    token_type: str = Field(default="bearer")

class TokenData(BaseModel):
    user_id: int = Field(..., gt=0)
    email: EmailStr = Field(...)

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=225)