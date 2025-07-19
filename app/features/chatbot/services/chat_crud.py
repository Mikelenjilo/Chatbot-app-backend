from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.features.chatbot.models.chat_model import Chat
from app.features.chatbot.models.message_model import Message
from app.core.enums import SenderType


# Chat CRUD operations
def get_chat(db: Session, chat_id: int) -> Optional[Chat]:
    """Get a chat by ID."""
    return db.query(Chat).filter(Chat.id == chat_id).first()


def get_user_chats(db: Session, user_id: int, limit: int = 50) -> List[Chat]:
    """Get all chats for a user."""
    return (
        db.query(Chat)
        .filter(Chat.user_id == user_id)
        .order_by(Chat.updated_at.desc())
        .limit(limit)
        .all()
    )


def create_chat(db: Session, user_id: int, title: str = None) -> Chat:
    """Create a new chat."""
    db_chat = Chat(
        user_id=user_id,
        title=title
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


def update_chat_title(db: Session, chat_id: int, title: str) -> Optional[Chat]:
    """Update a chat's title."""
    chat = get_chat(db, chat_id)
    if chat:
        chat.title = title
        chat.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(chat)
    return chat


def delete_chat(db: Session, chat_id: int) -> bool:
    """Delete a chat and all its messages."""
    chat = get_chat(db, chat_id)
    if chat:
        db.delete(chat)
        db.commit()
        return True
    return False


# Message CRUD operations
def get_chat_messages(db: Session, chat_id: int) -> List[Message]:
    """Get all messages in a chat."""
    return (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.sent_at.asc())
        .all()
    )


def create_message(db: Session, chat_id: int, content: str, sender: SenderType) -> Message:
    """Create a new message in a chat."""
    db_message = Message(
        chat_id=chat_id,
        content=content,
        sender=sender
    )
    db.add(db_message)
    
    # Update chat's updated_at timestamp
    chat = get_chat(db, chat_id)
    if chat:
        chat.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_message)
    return db_message


def get_chat_history_for_ai(db: Session, chat_id: int, limit: int = 10) -> List[dict]:
    """
    Get chat history formatted for AI service.
    Returns the last 'limit' messages in the chat.
    """
    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.sent_at.desc())
        .limit(limit)
        .all()
    )
    
    # Reverse to get chronological order and format for AI
    return [
        {
            "content": msg.content,
            "sender": msg.sender
        }
        for msg in reversed(messages)
    ] 