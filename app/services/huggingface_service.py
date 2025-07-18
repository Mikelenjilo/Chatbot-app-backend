"""
Hugging Face service for AI chatbot interactions.
Free alternative to OpenAI using Hugging Face Inference API.
"""

import httpx
import json
from typing import List, Dict, Any
from app.config import settings
from app.enums import SenderType

class HuggingFaceService:
    """
    Service class for handling chatbot interactions with Hugging Face.
    """
    
    def __init__(self):
        """Initialize the Hugging Face service."""
        self.base_url = "https://api-inference.huggingface.co/models"
        # Free models available:
        self.model = "microsoft/DialoGPT-large"  # Good for conversations
        # Alternatives: "facebook/blenderbot-400M-distill", "microsoft/DialoGPT-medium"
        
        # HF token is optional for public models, but recommended for better rate limits
        self.headers = {}
        if hasattr(settings, 'huggingface_token') and settings.huggingface_token:
            self.headers["Authorization"] = f"Bearer {settings.huggingface_token}"
    
    def generate_response(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Generate a response using Hugging Face Inference API.
        
        Args:
            message: The user's message
            chat_history: List of previous messages in the chat
            
        Returns:
            The chatbot's response
        """
        try:
            # Prepare the input
            inputs = self._prepare_input(message, chat_history)
            
            # Call Hugging Face API
            response = httpx.post(
                f"{self.base_url}/{self.model}",
                headers=self.headers,
                json={"inputs": inputs},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    # Extract only the new response (after the input)
                    if inputs in generated_text:
                        bot_response = generated_text.replace(inputs, "").strip()
                    else:
                        bot_response = generated_text.strip()
                    
                    return bot_response if bot_response else "I'm not sure how to respond to that."
                else:
                    return "Sorry, I couldn't generate a response."
                    
            elif response.status_code == 503:
                return "The AI model is currently loading. Please try again in a moment."
            else:
                print(f"HuggingFace API error: {response.status_code}")
                return "I'm having trouble connecting to the AI service."
                
        except Exception as e:
            print(f"Error generating response: {type(e).__name__}: {e}")
            return "I apologize, but I'm having trouble generating a response right now."
    
    def _prepare_input(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Prepare the input for Hugging Face model.
        
        Args:
            message: Current user message
            chat_history: Previous chat messages
            
        Returns:
            Formatted input string
        """
        context = ""
        
        # Add recent chat history
        if chat_history:
            for msg in chat_history[-3:]:  # Keep last 3 messages for context
                if msg["sender"] == SenderType.USER:
                    context += f"Human: {msg['content']}\n"
                else:
                    context += f"Bot: {msg['content']}\n"
        
        # Add current message
        context += f"Human: {message}\nBot:"
        
        return context
    
    def generate_chat_title(self, first_message: str) -> str:
        """
        Generate a title for a chat based on the first message.
        
        Args:
            first_message: The first message in the chat
            
        Returns:
            A suggested title for the chat
        """
        # For simplicity, use first few words of the message
        words = first_message.split()[:4]
        return " ".join(words) + ("..." if len(first_message.split()) > 4 else "")

# Create a global instance
huggingface_service = HuggingFaceService() 