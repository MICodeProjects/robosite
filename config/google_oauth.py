"""Google OAuth Configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

# OAuth 2.0 credentials
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET') #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
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_REDIRECT_URI = "http://localhost:5000/callback"

# OAuth scopes
OAUTH_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]
