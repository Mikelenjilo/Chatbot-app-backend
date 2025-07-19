from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserResponse(UserBase):
    """Schema for user data in API responses."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models

class LoginRequest(BaseModel):
    """Schema for login credentials."""
    username: str
    password: str


class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str


class TokenData(BaseModel):
    """Schema for token payload data."""
    username: Optional[str] = None


class RegisterResponse(BaseModel):
    """Schema for registration response with user data and token."""
    user: UserResponse
    access_token: str