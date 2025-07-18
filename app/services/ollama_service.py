"""
Ollama service for local AI chatbot interactions.
Completely free alternative to OpenAI.
"""

import httpx
from typing import List, Dict
from app.enums import SenderType

class OllamaService:
    """
    Service class for handling chatbot interactions with Ollama (local AI).
    """
    
    def __init__(self, model: str = "deepseek-r1"):
        """Initialize the Ollama service."""
        self.base_url = "http://localhost:11434"
        self.model = model
    
    def generate_response(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Generate a response using Ollama local AI.
        
        Args:
            message: The user's message
            chat_history: List of previous messages in the chat
            
        Returns:
            The chatbot's response
        """
        try:
            # Prepare the context
            context = self._prepare_context(message, chat_history)
            
            # Call Ollama API
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": context,
                    "stream": False
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Sorry, I couldn't generate a response.")
            else:
                print(f"Ollama API error: {response.status_code}")
                return "I'm having trouble connecting to the AI service."
                
        except httpx.ConnectError:
            return "🔴 Ollama is not running. Please start Ollama first: 'ollama serve'"
        except Exception as e:
            print(f"Error generating response: {type(e).__name__}: {e}")
            return "I apologize, but I'm having trouble generating a response right now."
    
    def _prepare_context(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Prepare the context for Ollama.
        
        Args:
            message: Current user message
            chat_history: Previous chat messages
            
        Returns:
            Formatted context string
        """
        context = "You are a helpful and friendly AI assistant. Provide clear, concise, and helpful responses.\n\n"
        
        # Add chat history if available
        if chat_history:
            for msg in chat_history[-5:]:  # Keep last 5 messages for context
                role = "Human" if msg["sender"] == SenderType.USER else "Assistant"
                context += f"{role}: {msg['content']}\n"
        
        # Add current message
        context += f"Human: {message}\nAssistant:"
        
        return context
    
    def generate_chat_title(self, first_message: str) -> str:
        """
        Generate a title for a chat based on the first message.
        
        Args:
            first_message: The first message in the chat
            
        Returns:
            A suggested title for the chat
        """
        try:
            prompt = f"Generate a short title (3-5 words) for this conversation: {first_message}\nTitle:"
            
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                title = result.get("response", "").strip()
                return title if title else f"Chat about {first_message[:30]}..."
            else:
                return f"Chat about {first_message[:30]}..."
                
        except Exception as e:
            print(f"Error generating chat title: {type(e).__name__}: {e}")
            return f"Chat about {first_message[:30]}..."

    def check_connection(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            return response.status_code == 200
        except:
            return False

# Create a global instance
ollama_service = OllamaService(model="deepseek-r1") 