"""Configuration for OAuth keys and other sensitive data"""
import os
from dotenv import load_dotenv

load_dotenv()

class Keys:
    """Keys configuration class"""
    # Google OAuth 2.0 credentials
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = "http://localhost:5000/auth/google/callback"
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    
    # Session configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # OAuth scopes
    GOOGLE_SCOPES = [
        'openid',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
