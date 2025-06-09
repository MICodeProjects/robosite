from flask import render_template, request, redirect, url_for, session, flash
import os
import requests  # Add this import
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from config.google_oauth import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OAUTH_SCOPES
from models.user_model import UserModel
from models.team_model import TeamModel



class SessionController:
    def __init__(self, team_model:TeamModel, user_model: UserModel):
        self.user_model = user_model
        self.team_model=team_model
        self.flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=OAUTH_SCOPES,
            redirect_uri="http://localhost:5000/callback"
        )

    def login(self):
        authorization_url, state = self.flow.authorization_url()
        session["state"] = state
        session.permanent = True  # Make session permanent
        return redirect(authorization_url)

    def callback(self):
        self.flow.fetch_token(authorization_response=request.url)
        credentials = self.flow.credentials
        user_info = id_token.verify_oauth2_token(
            credentials.id_token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )

        # Create or update user with default access level 2
        user = {
            'google_id': user_info['sub'],
            'name': user_info['name'],
            'email': user_info['email'],
            'profile_picture': user_info.get('picture'),
            'access': 2  # Default to member access
        }
        
        self.user_model.create_or_update(user)
        session['user'] = user
        session.permanent = True  # Make session permanent
        return redirect(url_for('index'))

    def logout(self):
        session.clear()
        return redirect(url_for('index'))
    def index(self):
        """Home page."""
        current_user = self.get_current_user()
        return render_template('index.html', user=current_user)

    
    def profile(self):
        """Profile page."""
        return render_template('profile.html')

    def settings(self):
        """Settings page."""
        return render_template('settings.html')

    def get_current_user(self):
        """Get the current user from the session."""
        # Always refresh session['user'] from DB if user_email is present
        if 'user_email' in session:
            result = self.user_model.get(session['user_email'])
            if result['status'] == 'success':
                session['user'] = result['data']
                return result['data']
            session.pop('user', None)
            session.pop('user_email', None)
        return {'email': None, 'team_id': None, 'access': 1}  # Default guest user
