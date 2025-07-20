"""
Main FastAPI application for the AI Chatbot.
This file contains all the API endpoints and brings everything together.
"""

from datetime import timedelta
from typing import List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db, create_tables
from app.features.auth.services.auth_service import create_access_token, get_current_user
from app.core.enums import SenderType
from app.features.auth.models.user_model import User
from app.features.auth.schemas.auth_schemas import UserCreate, RegisterResponse, LoginRequest, Token
from app.features.auth.schemas.auth_schemas import UserResponse
from app.features.auth.services.auth_crud import get_user_by_username, get_user_by_email, create_user, authenticate_user
from app.features.chatbot.services.chat_crud import get_chat, get_user_chats, create_chat, update_chat_title, delete_chat, get_chat_messages, create_message, get_chat_history_for_ai
from app.features.chatbot.schemas.chat_schemas import ChatResponse, ChatRequest, ChatMessageResponse
from app.features.chatbot.services.ollama_service import ollama_service

# Import AI services
from app.features.chatbot.services.ollama_service import ollama_service

import logging

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A FastAPI-based AI chatbot using OpenAI's API"
)
logger = logging.getLogger("uvicorn.error")


# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    create_tables()
    print(f"🚀 {settings.app_name} v{settings.app_version} started!")
    print(f"📊 Database: {settings.database_url}")


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}!",
        "version": settings.app_version,
        "status": "healthy"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    ai_status = "unknown"
    
    # Check AI service status
    ai_status = "connected" if ollama_service.check_connection() else "disconnected"
    
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "ai_service": settings.ai_service,
        "ai_status": ai_status,
        "ollama_running": ollama_service.check_connection()
    }


# Authentication endpoints
@app.post("/auth/register", response_model=RegisterResponse, tags=["Authentication"])
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return access token."""
    # Check if username already exists
    if get_user_by_username(db, username=user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if get_user_by_email(db, email=user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    db_user = create_user(db=db, user=user)
    
    # Generate access token for the new user
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    return RegisterResponse(
        user=db_user,
        access_token=access_token,
    )


@app.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token."""
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token}


# User endpoints
@app.get("/users/me", response_model=UserResponse, tags=["Users"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


# Chat endpoints
@app.post("/chat", response_model=ChatMessageResponse, tags=["Chat"])
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the chatbot and get a response.
    
    If chat_id is provided, adds to existing chat.
    If not provided, creates a new chat.
    """

    try:
        # Get or create chat
        if chat_request.chat_id:

            # Verify chat belongs to current user
            chat = get_chat(db, chat_request.chat_id)
            if not chat or chat.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )
        else:
            # Create new chat
            chat = create_chat(db, current_user.id)
        
        # Get chat history for context
        chat_history = get_chat_history_for_ai(db, chat.id)
        
        # Create user message
        user_message = create_message(
            db, chat.id, chat_request.message, SenderType.USER
        )
        
        # Get the configured AI service
        ai_service = ollama_service
        
        # Generate bot response
        bot_response = ai_service.generate_response(
            chat_request.message, chat_history
        )
        
        # Create bot message
        bot_message = create_message(
            db, chat.id, bot_response, SenderType.AI
        )
        logger.info(f"Bot message: {bot_message}")
        
        # Generate title for new chats
        # if not chat.title and len(chat_history) == 0:
        #     title = ai_service.generate_chat_title(chat_request.message)
        #     update_chat_title(db, chat.id, title)
        
        return ChatMessageResponse(
            user_message=user_message,
            bot_message=bot_message,
            chat_id=chat.id
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message"
        )


# Chat endpoints
@app.get("/chats", response_model=List[ChatResponse], tags=["Chats"])
async def get_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chats for the current user."""
    chats = get_user_chats(db, current_user.id)
    return chats


@app.get("/chats/{chat_id}", response_model=ChatResponse, tags=["Chats"])
async def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat with all messages."""
    chat = get_chat(db, chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return chat


@app.delete("/chats/{chat_id}", tags=["Chats"])
async def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat."""
    chat = get_chat(db, chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    success = delete_chat(db, chat_id)
    if success:
        return {"message": "Chat deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat"
        )


@app.put("/chats/{chat_id}/title", response_model=ChatResponse, tags=["Chats"])
async def update_chat_title(
    chat_id: int,
    title: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a chat's title."""
    chat = get_chat(db, chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    updated_chat = update_chat_title(db, chat_id, title)
    return updated_chat


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 