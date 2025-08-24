from pydantic import BaseModel, EmailStr
from typing import Optional
from .user import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    session_id: str
    user: UserResponse


class SessionResponse(BaseModel):
    session_id: str
    user_id: int
    created_at: str
    last_accessed: str
