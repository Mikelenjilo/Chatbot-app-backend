from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.core.enums import SenderType


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
    chat_id: Optional[int] = None


class ChatMessageResponse(BaseModel):
    """Schema for chat message API responses."""
    user_message: MessageResponse
    bot_message: MessageResponse
    chat_id: int
