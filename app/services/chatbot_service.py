"""
Chatbot service for handling OpenAI API interactions.
This service manages the communication with OpenAI's API.
"""

from openai import OpenAI
from typing import List, Dict, Any
from app.config import settings
from app.enums import SenderType

class ChatbotService:
    """
    Service class for handling chatbot interactions with OpenAI.
    """
    
    def __init__(self):
        """Initialize the chatbot service with OpenAI client."""
        if not settings.openai_api_key:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
            )
        
        # Initialize OpenAI client with new syntax
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def generate_response(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Generate a response from the chatbot using OpenAI's API.
        
        Args:
            message: The user's message
            chat_history: List of previous messages in the chat
            
        Returns:
            The chatbot's response
        """
        try:
            # Prepare the chat context
            messages = self._prepare_messages(message, chat_history)
            
            # Call OpenAI API with new syntax
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract the response content
            bot_response = response.choices[0].message.content.strip()
            return bot_response
            
        except Exception as e:
            # Better error logging for debugging
            print(f"Error generating response: {type(e).__name__}: {e}")
            if "authentication" in str(e).lower() or "api_key" in str(e).lower():
                print("🔑 Check your OpenAI API key configuration!")
            elif "quota" in str(e).lower() or "billing" in str(e).lower():
                print("💳 Check your OpenAI account billing/quota!")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    def _prepare_messages(self, message: str, chat_history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """
        Prepare the messages list for OpenAI API.
        
        Args:
            message: Current user message
            chat_history: Previous chat messages
            
        Returns:
            Formatted messages for OpenAI API
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful and friendly AI assistant. "
                          "Provide clear, concise, and helpful responses to user questions."
            }
        ]
        
        # Add chat history if available
        if chat_history:
            for msg in chat_history[-10:]:  # Keep last 10 messages for context
                role = "user" if msg["sender"] == SenderType.USER else "assistant"
                messages.append({
                    "role": role,
                    "content": msg["content"]
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        return messages
    
    def generate_chat_title(self, first_message: str) -> str:
        """
        Generate a title for a chat based on the first message.

        Args:
            first_message: The first message in the chat
            
        Returns:
            A suggested title for the chat
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a short, descriptive title (3-5 words) for a chat that starts with the following message. Only return the title, nothing else."
                    },
                    {
                        "role": "user",
                        "content": first_message
                    }
                ],
                max_tokens=20,
                temperature=0.5
            )
            
            title = response.choices[0].message.content.strip()
            return title
            
        except Exception as e:
            # Log the error and fallback to a generic title
            print(f"Error generating chat title: {type(e).__name__}: {e}")
            return f"Chat about {first_message[:30]}..."


# Create a global instance
chatbot_service = ChatbotService() 