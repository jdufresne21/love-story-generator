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
        self.openai_api_key = os.getenv('OPENAI_API_KEY', 
            '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')
        
        # Model configuration
        self.model_name = "gpt-4o-mini"  # Using the model you specified
        self.max_tokens = 1500
        self.temperature = 0.8  # Higher temperature for more creative stories
        
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
