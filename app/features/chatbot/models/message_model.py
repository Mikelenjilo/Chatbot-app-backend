from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.enums import SenderType


class Message(Base):
    """
    Message model - represents individual messages in a chat.
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    content = Column(Text, nullable=False)  # The actual message content
    sender = Column(SqlEnum(SenderType), nullable=False)  # Indicates if message is from user or AI
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    chat = relationship("Chat", back_populates="messages") 