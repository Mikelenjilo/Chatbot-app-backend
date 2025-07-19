from typing import Optional
from sqlalchemy.orm import Session
import secrets
import hashlib

from app.features.auth.models.user_model import User
from app.features.auth.schemas.auth_schemas import UserCreate


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


def create_user(db: Session, user: UserCreate) -> User:
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