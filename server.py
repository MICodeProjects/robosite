from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.database import Base
from config.keys import Keys

# Set environment variable to allow OAuth over HTTP for localhost development
# This is ONLY for development purposes - production should always use HTTPS
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Import models
from models.user_model import UserModel
from models.team_model import TeamModel
from models.unit_model import UnitModel
from models.lesson_model import LessonModel
from models.lesson_component_model import LessonComponentModel

# Import controllers
from controllers.User_Controller import UserController
from controllers.Team_Controller import TeamController
from controllers.unit_Controller import UnitController
from controllers.lesson_Controller import LessonController
from controllers.lesson_component_Controller import LessonComponentController
from controllers.auth_controller import AuthController

from controllers.session_controller import SessionController

# Add missing OAuth dependencies to requirements
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = Keys.SECRET_KEY
app.permanent_session_lifetime = timedelta(days=7)

# Set up static folder
app.static_folder = 'static'

# Database setup
DB_PATH = os.path.join('data', 'robosite.db')
DB_URL = f'sqlite:///{DB_PATH}'

# Initialize models with database URL
user_model = UserModel()
team_model = TeamModel()
unit_model = UnitModel()
lesson_model = LessonModel()
lesson_component_model = LessonComponentModel()

# Initialize controller instances
user_controller = UserController(user_model)
auth_controller = AuthController(user_model)
team_controller = TeamController(team_model, user_model)
unit_controller = UnitController(unit_model, lesson_model, user_model)
lesson_controller = LessonController(lesson_model, lesson_component_model, user_model, unit_model)
lesson_component_controller = LessonComponentController(lesson_component_model, user_model, lesson_model, unit_model)
session_controller = SessionController(user_model)

# Make sessions permanent and set session lifetime
app.permanent_session_lifetime = timedelta(days=7)  # or however long you want

def init_database():
    """Initialize the SQLite database"""
    os.makedirs('data', exist_ok=True)
    db_path = os.path.abspath(os.path.join('data', 'robosite.db'))
    db_url = f'sqlite:///{db_path}'

    # Create a single engine and create tables once
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)

    # Initialize all models with the same engine
    user_model.initialize_DB(DB_name=db_url)
    team_model.initialize_DB(DB_name=db_url)
    unit_model.initialize_DB(DB_name=db_url)
    lesson_model.initialize_DB(DB_name=db_url)
    lesson_component_model.initialize_DB(DB_name=db_url)
    
    # Create default teams if they don't exist
    # default_teams = ["phoenixes", "pigeons", "teachers"]
    # team_ids = {}
    # for team_name in default_teams:
    #     team_exists = team_model.exists(team=team_name)
    #     if team_exists==False:
    #         team_result = team_model.create(team_name)
    #         if team_result["status"] == "success":
    #             team_ids[team_name] = team_result["data"]["id"]
    #             print(f"Team '{team_name}' created successfully!")
    #         else:
    #             print(f"Error creating team '{team_name}': {team_result['data']}")
    #     else:
    #         team_result = team_model.get(team=team_name)
    #         if team_result["status"] == "success":
    #             team_ids[team_name] = team_result["data"]["id"]
    #         else:
    #             print(f"Error getting team '{team_name}': {team_result['data']}")
    team_ids = {"phoenixes":1, "pigeons":2, "teachers":3}
    for team_name in team_ids.keys():
        team_result = team_model.create(team_name)
        if team_result["status"] == "success":
            team_ids[team_name] = team_result["data"]["id"]
            print(f"Team '{team_name}' created successfully!")
        else:
            print(f"Error creating team '{team_name}': {team_result['data']}")
              # Create admin user if not exists
    admin_info = {
        'google_id': '111675821664854451432', # IMPORTANT: Replace with YOUR actual Google ID shown in flash message after login
        'name': 'Maya Admin',
        'email': 'maya23inal@gmail.com',
        'team_id': 3,  # teachers team
        'access': 3    # admin access
    }
    user_model.create(admin_info)
    
    print(f"Database initialized successfully at {db_path}")
    
# Context processor to inject current year into templates
@app.context_processor
def inject_year():
    """Inject the current year into all templates."""
    return {'year': datetime.now().year}

# inject current user from auth into all templates
@app.context_processor
def inject_user():
    """Make current user available to all templates."""
    return {'user': auth_controller.get_current_user()}




# Route Handlers
@app.route('/')
def index():
    """Home page"""
    return session_controller.index()

@app.route('/auth/google')
def login():
    """Start Google OAuth flow"""
    return auth_controller.login()

@app.route('/auth/google/callback')
def callback():
    """Handle Google OAuth callback"""
    return auth_controller.callback()

@app.route('/logout')
def logout():
    """Logout"""
    return auth_controller.logout()

@app.route('/profile')
def profile():
    """Logout"""
    return render_template("profile.html")


@app.route('/settings')
def settings():
    """Logout"""
    return render_template("settings.html")

# Routes using add_url_rule for cleaner organization

# Team routes
app.add_url_rule('/teams', 'teams.view', view_func=team_controller.view)
app.add_url_rule('/teams/create', 'teams.create', view_func=team_controller.create, methods=['POST'])
app.add_url_rule('/teams/update', 'teams.update', view_func=team_controller.update, methods=['POST'])

# User routes
app.add_url_rule('/users/update', 'users.update', view_func=user_controller.update, methods=['POST'])
app.add_url_rule('/users/delete', 'users.delete', view_func=user_controller.delete, methods=['POST'])

# Unit routes
app.add_url_rule('/units', 'units.view', view_func=unit_controller.view)
app.add_url_rule('/units/create', 'units.create', view_func=unit_controller.create, methods=['POST'])
app.add_url_rule('/units/update', 'units.update', view_func=unit_controller.update, methods=['POST'])
app.add_url_rule('/units/delete', 'units.delete', view_func=unit_controller.delete, methods=['POST'])

# Lesson routes
app.add_url_rule('/lessons/<int:unit_id>/<int:lesson_id>', 'lessons.view', view_func=lesson_controller.view)
app.add_url_rule('/lessons/create', 'lessons.create', view_func=lesson_controller.create, methods=['POST'])
app.add_url_rule('/lessons/update', 'lessons.update', view_func=lesson_controller.update, methods=['POST'])
app.add_url_rule('/lessons/delete', 'lessons.delete', view_func=lesson_controller.delete, methods=['POST'])

# lesson component routes
app.add_url_rule('/lessons/<int:unit_id>/<int:lesson_id>/<int:lesson_component_id>', 
                 'lesson_components.view', 
                 view_func=lesson_component_controller.view)
app.add_url_rule('/lesson_components/create', 'lesson_components.create', view_func=lesson_component_controller.create, methods=['POST'])
app.add_url_rule('/lesson_components/update', 'lesson_components.update', view_func=lesson_component_controller.update, methods=['POST'])
app.add_url_rule('/lesson_components/delete', 'lesson_components.delete', view_func=lesson_component_controller.delete, methods=['POST'])

# Access Control Middleware
@app.before_request
def check_access():
    """Check if user has required access level for protected routes"""
    user = auth_controller.get_current_user()
    
    # Public routes
    public_routes = ['index', 'google_login', 'callback']
    if request.endpoint in public_routes:
        return None
    
    # Member routes (level 2+)
    member_routes = ['units.view', 'teams.view', 'lessons.view', 'lesson_components.view']
    if request.endpoint in member_routes and user['access'] < 2:
        flash('You must be a team member to access this page')
        return redirect(url_for('index'))
    
    # Admin routes (level 3)
    admin_routes = [
        'teams.create', 'teams.update', 
        'users.update', 'users.delete',
        'units.create', 'units.update', 'units.delete',
        'lessons.create', 'lessons.update', 'lessons.delete',
        'lesson_components.create', 'lesson_components.update', 'lesson_components.delete'
    ]
    if request.endpoint in admin_routes and user['access'] < 3:
        flash('You must be a team captain or teacher to perform this action', 'error')
        return redirect(url_for('index'))
    
    return None

@app.before_request
def make_session_permanent():
    session.permanent = True

if __name__ == '__main__':
    # Initialize databases
    init_database()
    
    # Start the Flask development server
    app.run(debug=True)