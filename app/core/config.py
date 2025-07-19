"""
Configuration settings for the chatbot application.
This file manages all environment variables and app settings.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    You can create a .env file in your project root to set these values:
    OPENAI_API_KEY=your_openai_api_key_here
    SECRET_KEY=your_secret_key_here
    """
    
    # Database settings
    database_url: str = "sqlite:///./chatbot.db"
    
    # AI Service Selection (ollama)
    ai_service: str = "ollama" 
    
    # Security settings
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App settings
    app_name: str = "AI Chatbot"
    app_version: str = "1.0.0"
    debug: bool = True
    
    class Config:
        env_file = ".env"


# Create a global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings 