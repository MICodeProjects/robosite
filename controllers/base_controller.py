from flask import redirect, session, url_for, flash, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
from config.keys import Keys
from models.user_model import UserModel

class BaseController:
    def __init__(self, user_model:UserModel):
        self.user_model = user_model
        self.flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": Keys.GOOGLE_CLIENT_ID,
                    "client_secret": Keys.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [Keys.GOOGLE_REDIRECT_URI]
                }
            },
            scopes=Keys.GOOGLE_SCOPES,
            redirect_uri=Keys.GOOGLE_REDIRECT_URI
        )

    def get_current_user(self):
        """Get current user from session"""
        if 'user' in session:
            # Optionally refresh from database if needed
            user = self.user_model.get(email=session['user']['email'])
            if user['status'] == 'success':
                session['user'] = user['data']
                return user['data']
            session.pop('user', None)
        return {'email': None, 'team_id': None, 'access': 1}  # Default guest user

    def require_access_level(self, required_level):
        """Check if current user has required access level"""
        current_user = self.get_current_user()
        return current_user['access'] >= required_level

    def flash_error(self, message):
        """Flash error message"""
        flash(message, 'error')

    def flash_success(self, message):
        """Flash success message"""
        flash(message, 'success')