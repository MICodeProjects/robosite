from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.database import Base

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
from controllers.session_Controller import SessionController

app = Flask(__name__)
app.secret_key = "your-very-secret-key"  # Use a constant key!

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
team_controller = TeamController(team_model, user_model)
unit_controller = UnitController(unit_model, lesson_model, user_model)
lesson_controller = LessonController(lesson_model, lesson_component_model, user_model, unit_model)
lesson_component_controller = LessonComponentController(lesson_component_model, user_model, lesson_model, unit_model)
session_controller = SessionController(user_model, team_model)

# Make sessions permanent and set session lifetime
app.permanent_session_lifetime = timedelta(days=7)  # or however long you want

def init_database():
    """Initialize the SQLite database"""
    os.makedirs('data', exist_ok=True)
    db_path = os.path.abspath(os.path.join('data', 'robosite.db'))
    db_url = f'sqlite:///{db_path}'
     # Initialize all models with the same databaseAdd commentMore actions
    user_model.initialize_DB(DB_name=db_url)
    team_model.initialize_DB(DB_name=db_url)
    unit_model.initialize_DB(DB_name=db_url)
    lesson_model.initialize_DB(DB_name=db_url)
    lesson_component_model.initialize_DB(DB_name=db_url)
    
    # Create default teams if they don't exist
    default_teams = ["phoenixes", "pigeons", "teachers"]
    team_ids = {}
    for team_name in default_teams:
        team_exists = team_model.exists(team=team_name)
        if team_exists==False:
            team_result = team_model.create(team_name)
            if team_result["status"] == "success":
                team_ids[team_name] = team_result["data"]["id"]
                print(f"Team '{team_name}' created successfully!")
            else:
                print(f"Error creating team '{team_name}': {team_result['data']}")
        else:
            team_data = team_model.get_team(team=team_name)["data"]
            team_ids[team_name] = team_data["id"]
            
    # Create admin user if not exists
    if not user_model.exists(email='admin@robotics.com')["data"]:
        # Ensure team ID 1 exists
        admin_team_id = team_ids.get("phoenixes", 1)  # Default to 1 if "phoenixes" doesn't exist
        user_model.create({
            'email': 'admin@robotics.com',
            'access': 3,
            'team_id': admin_team_id
        })
        print("Admin user created successfully!")
    
    print(f"Database initialized successfully at {db_path}")
    
# Context processor to inject current year into templates
@app.context_processor
def inject_year():
    """Inject the current year into all templates."""
    return {'year': datetime.now().year}



# Route Handlers
@app.route('/')
def index():
    """Home page."""
    return session_controller.index()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    return session_controller.login()



@app.route('/profile')
def profile():
    """Profile page."""
    return session_controller.profile()

@app.route('/settings')
def settings():
    """Settings page."""
    return session_controller.settings()

@app.route('/logout')
def logout():
    """Logout page."""
    return session_controller.logout()

@app.route('/register', methods=['GET', 'POST'])
def register():
    return session_controller.register()

# If you want 'teams_manage' or 'statistics', define them:
# @app.route('/teams/manage')
# def teams_manage():
#     ...

# @app.route('/statistics')
# def statistics():
#     ...

# Routes using add_url_rule for cleaner organization

# Team routes
app.add_url_rule('/teams', 'teams.view', view_func=team_controller.view)
app.add_url_rule('/teams/create', 'teams.create', view_func=team_controller.create_team, methods=['POST'])
app.add_url_rule('/teams/update', 'teams.update', view_func=team_controller.update_team, methods=['POST'])

# User routes
app.add_url_rule('/users/update', 'users.update', view_func=user_controller.update_user, methods=['POST'])
app.add_url_rule('/users/delete', 'users.delete', view_func=user_controller.delete_user, methods=['POST'])

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
    """Check if user has required access level for protected routes."""
    current_user = user_controller.get_current_user()
    
    # Public routes - allow all access levels
    public_routes = ['index', 'login', 'register']
    if request.endpoint in public_routes:
        return None
        
    # Routes requiring access level 2 or higher
    member_routes = ['units.view', 'teams.view', 'lessons.view', 'lesson_components.view', 'todo.view']
    if request.endpoint in member_routes and current_user['access'] < 2:
        flash('You must be a team member to access this page', 'error')
        return redirect(url_for('index'))
        
    # Routes requiring access level 3
    admin_routes = [
        'teams.create', 'teams.update', 
        'users.update', 'users.delete',
        'units.create', 'units.update', 'units.delete',
        'lessons.create', 'lessons.update', 'lessons.delete',
        'lesson_components.create', 'lesson_components.update', 'lesson_components.delete'
    ]
    if request.endpoint in admin_routes and current_user['access'] < 3:
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