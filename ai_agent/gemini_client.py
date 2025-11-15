"""
Gemini API Client Wrapper

Handles communication with Google's Gemini API for generating AI responses.
"""

import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Wrapper for Google's Gemini API.
    Handles initialization, API calls, and error handling.
    """

    def __init__(self, api_key=None):
        """
        Initialize Gemini client with API key.
        
        Args:
            api_key: Optional API key. If not provided, uses GEMINI_API_KEY from settings.
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY in your .env file.")
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model (using gemini-pro for text generation)
        try:
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise

    def generate_response(self, prompt, context_history=None, temperature=0.7):
        """
        Generate a response from Gemini API.
        
        Args:
            prompt: The main prompt/instruction for the AI
            context_history: Optional list of previous messages for conversation context.
                           Format: [{"role": "user", "parts": ["message"]}, ...]
            temperature: Controls randomness (0.0-1.0). Lower = more deterministic.
        
        Returns:
            dict: {
                "response": str,  # The generated response text
                "error": str or None  # Error message if failed
            }
        """
        try:
            # Build the full conversation history if provided
            if context_history:
                # Start the chat with the history
                chat = self.model.start_chat(history=context_history)
                response = chat.send_message(prompt, generation_config={
                    "temperature": temperature,
                })
            else:
                # Simple generation without history
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": temperature,
                    }
                )
            
            # Extract text from response
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "response": response_text,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Gemini API error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return {
                "response": None,
                "error": error_msg
            }

    def format_conversation_history(self, messages):
        """
        Format conversation history from ConversationHistory model for Gemini API.
        
        Args:
            messages: QuerySet or list of ConversationHistory objects
        
        Returns:
            list: Formatted history for Gemini API
                Format: [{"role": "user", "parts": ["message"]}, ...]
        """
        history = []
        
        for msg in messages:
            # Gemini API expects "user" or "model" roles (not "assistant")
            role = "user" if msg.role == "user" else "model"
            
            history.append({
                "role": role,
                "parts": [msg.message]
            })
        
        return history

