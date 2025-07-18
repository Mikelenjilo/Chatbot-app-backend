"""
Startup script for the AI Chatbot FastAPI application.
Run this file to start the server.
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🤖 Starting AI Chatbot Server...")
    print("📝 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Alternative docs at: http://localhost:8000/redoc")
    print("⭐ Server running at: http://localhost:8000")
    print("\n" + "="*50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    ) 