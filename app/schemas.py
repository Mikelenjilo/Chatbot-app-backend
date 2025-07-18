"""
Pydantic schemas for data validation and API request/response models.
These define the structure of data that comes in and goes out of our API.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.enums import SenderType


# User schemas
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


# Message schemas
class MessageBase(BaseModel):
    """Base message schema."""
    content: str
    sender: SenderType


class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    content: str
    sender: SenderType


class MessageResponse(MessageBase):
    """Schema for message data in API responses."""
    id: int
    chat_id: int
    sent_at: datetime
    
    class Config:
        from_attributes = True


# Chat schemas
class ChatBase(BaseModel):
    """Base chat schema."""
    title: Optional[str] = None


class ChatCreate(ChatBase):
    """Schema for creating a new chat."""
    pass


class ChatResponse(ChatBase):
    """Schema for chat data in API responses."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for incoming chat messages."""
    message: str
    chat_id: Optional[int] = None  # If None, creates a new chat


class ChatResponse(BaseModel):
    """Schema for chat API responses."""
    user_message: MessageResponse
    bot_message: MessageResponse
    chat_id: int


# Authentication schemas
class LoginRequest(BaseModel):
    """Schema for login credentials."""
    username: str
    password: str


class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token payload data."""
    username: Optional[str] = None


class RegisterResponse(BaseModel):
    """Schema for registration response with user data and token."""
    user: UserResponse
    access_token: str