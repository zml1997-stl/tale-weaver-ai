import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the application."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Gemini API settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = "gemini-1.5-flash"  # Using Gemini-2.0-Flash as specified
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    
    # Story genres
    STORY_GENRES = [
        'Fantasy',
        'Science Fiction',
        'Mystery',
        'Adventure',
        'Horror',
        'Romance',
        'Historical Fiction',
        'Comedy'
    ]
    
    # Maximum story parts
    MAX_STORY_PARTS = 10