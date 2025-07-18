"""
CRUD (Create, Read, Update, Delete) operations for database models.
These functions handle all database interactions.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
import hashlib
import secrets
from app.models.user_model import User
from app.models.chat_model import Chat
from app.models.message_model import Message
from app import schemas
from app.enums import SenderType


# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def hash_password(password: str) -> str:
    """Hash a password with salt."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, password_hash = hashed_password.split(":")
        return hashlib.sha256((plain_password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False


def create_user(db: Session, user: schemas.UserCreate) -> User:
    """Create a new user."""
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


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