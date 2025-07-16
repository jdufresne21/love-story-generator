"""
Configuration settings for the Love Story Generator
"""

import os
from dotenv import load_dotenv

class Config:
    """Configuration class for managing API keys and settings"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # OpenAI API configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Model configuration
        self.model_name = "gpt-4-turbo-preview"  # GPT-4 Turbo for better quality and cost efficiency
        self.max_tokens = 2000  # Increased for longer, more detailed stories
        self.temperature = 0.7  # Slightly lower for more consistent quality while maintaining creativity
        
        # Tally configuration (for future integration)
        self.tally_api_url = os.getenv('TALLY_API_URL', '')
        self.tally_api_key = os.getenv('TALLY_API_KEY', '')
        
    def validate_config(self):
        """Validate that required configuration is present"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        if not self.openai_api_key.startswith('sk-'):
            raise ValueError("Invalid OpenAI API key format")
        
        return True
