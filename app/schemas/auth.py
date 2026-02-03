from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Token(BaseModel):
    access_token: str = Field(..., min_length=1)
    token_type: str = Field(default="bearer")
    expires_in: Optional[int] = Field(None, gt=0)
    refresh_token: Optional[str] = Field(None, min_length=1)

class TokenData(BaseModel):

    user_id: Optional[int] = Field(None, gt=0)
    email: Optional[EmailStr] = Field(None)
    exp: Optional[int] = Field(None, gt=0)

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=225)

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...,min_length=5, max_length=255)
    password: str = Field(..., min_length=4, max_length=100)

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)

class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=225)
    new_password: str = Field(..., min_length=6, max_length=225)