from flask import redirect, session, url_for, request, flash
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from config.keys import Keys
from models.user_model import UserModel
from models.team_model import TeamModel

from controllers.base_controller import BaseController


class AuthController(BaseController):
    def __init__(self, user_model: UserModel, team_model:TeamModel):
        self.user_model = user_model
        self.team_model = team_model
        # Use configuration from Keys instead of client_secrets.json file
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

    def login(self):
        """Start Google OAuth flow"""
        authorization_url, state = self.flow.authorization_url()
        session['state'] = state
        return redirect(authorization_url)

    def callback(self):
        """Handle Google OAuth callback"""
        try:
            self.flow.fetch_token(authorization_response=request.url)
            credentials = self.flow.credentials
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()

            print("new user info: ", user_info)
            
            # Display Google ID for debugging (temporary)
            from flask import flash
            flash(f"Welcome to Robosite, {user_info['name']}", 'info')
            
            # does user exist? if so, get team_id
            exists_result=self.user_model.exists(email=user_info['email'])
            print("exists_result: ", exists_result)
            if exists_result["status"] == "success" and exists_result["data"]==True:
                team_id_result=self.user_model.get(email=user_info['email'])
                print("team_idresult = ", team_id_result)
                team_id=team_id_result["data"]["team_id"]
                access=team_id_result["data"]["access"]

            # default to pigeons team if no team id
            else:
                team_id=2 
                access=2

            # Create/update user in database
            user_data = {
                'google_id': user_info['id'],
                'name': user_info['name'],
                'email': user_info['email'],
                'team_id':team_id,
                'access': access  # Default to member access
            }
            result = self.user_model.create(user_data)
            if result['status'] == 'success':
                session['user'] = result['data']
                # adding team_name to session['user']
                session['user']['team_name']=self.team_model.get(id=team_id)['data']['name']
                

                
                return redirect(url_for('index'))
            else:
                return redirect(url_for('index', error="Login failed"))
                
        except Exception as e:
            return redirect(url_for('index', error=str(e)))


    def logout(self):
        """Clear session and logout user"""
        session.clear()
        return redirect(url_for('index'))
