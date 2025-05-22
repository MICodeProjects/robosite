from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

# Import models
from models.user_model import User_Model
from models.team_model import Team_Model
from models.unit_model import Unit_Model
from models.lesson_model import Lesson_Model
from models.lesson_component_model import lesson_component_Model

# Import controllers
from controllers.User_Controller import User_Controller
from controllers.Team_Controller import Team_Controller
from controllers.unit_Controller import Unit_Controller
from controllers.lesson_Controller import Lesson_Controller
from controllers.lesson_component_Controller import lesson_component_Controller

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Set up static folder
app.static_folder = 'static'

# Initialize model instances
user_model = User_Model()
team_model = Team_Model()
unit_model = Unit_Model()
lesson_model = Lesson_Model()
lesson_component_model = lesson_component_Model()

# Initialize controller instances
user_controller = User_Controller(user_model)
team_controller = Team_Controller(team_model, user_model)
unit_controller = Unit_Controller(unit_model, lesson_model)
lesson_controller = Lesson_Controller(lesson_model, lesson_component_model)
lesson_component_controller = lesson_component_Controller(lesson_component_model)

# Initialize database files
def init_databases():
    """Initialize all database files"""
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    user_model.initialize_DB(DB_name='data/users.json')
    team_model.initialize_DB(DB_name='data/teams.json')
    unit_model.initialize_DB(DB_name='data/units.json')
    lesson_model.initialize_DB(DB_name='data/lessons.json')
    lesson_component_model.initialize_DB(DB_name='data/lesson_components.json')
    
    print("All databases initialized successfully!")

# Route Handlers
@app.route('/')
def index():
    """Home page."""
    current_user = user_controller.get_current_user()
    session['user'] = current_user
    return render_template('index.html')

# Routes using add_url_rule for cleaner organization

# Team routes
app.add_url_rule('/teams', 'teams.view', view_func=team_controller.view)
app.add_url_rule('/teams/create', 'teams.create', view_func=team_controller.create_team, methods=['POST'])
app.add_url_rule('/teams/update', 'teams.update', view_func=team_controller.update_team, methods=['POST'])
app.add_url_rule('/teams/add_user', 'teams.add_user', view_func=team_controller.add_user_to_team, methods=['POST'])
app.add_url_rule('/teams/remove_user', 'teams.remove_user', view_func=team_controller.remove_user_from_team, methods=['POST'])

# User routes
app.add_url_rule('/users/update', 'users.update', view_func=user_controller.update_user, methods=['POST'])
app.add_url_rule('/users/delete', 'users.delete', view_func=user_controller.delete_user, methods=['POST'])

# Unit routes
app.add_url_rule('/units', 'units.view', view_func=unit_controller.view)
app.add_url_rule('/units/create', 'units.create', view_func=unit_controller.create, methods=['POST'])
app.add_url_rule('/units/update', 'units.update', view_func=unit_controller.update, methods=['POST'])
app.add_url_rule('/units/delete', 'units.delete', view_func=unit_controller.delete, methods=['POST'])

# Lesson routes
app.add_url_rule('/lessons/<int:lesson_id>', 'lessons.view', view_func=lesson_controller.view)
app.add_url_rule('/lessons/create', 'lessons.create', view_func=lesson_controller.create, methods=['POST'])
app.add_url_rule('/lessons/update', 'lessons.update', view_func=lesson_controller.update, methods=['POST'])
app.add_url_rule('/lessons/delete', 'lessons.delete', view_func=lesson_controller.delete, methods=['POST'])

# replacewithsmthhhelse routes
app.add_url_rule('/lesson_components/<int:lesson_component_id>', 'lesson_components.view', view_func=lesson_component_controller.view)
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
        'teams.create', 'teams.update', 'teams.add_user', 'teams.remove_user',
        'users.update', 'users.delete',
        'units.create', 'units.update', 'units.delete',
        'lessons.create', 'lessons.update', 'lessons.delete',
        'lesson_components.create', 'lesson_components.update', 'lesson_components.delete'
    ]
    if request.endpoint in admin_routes and current_user['access'] < 3:
        flash('You must be a team captain or teacher to perform this action', 'error')
        return redirect(url_for('index'))
    
    return None

if __name__ == '__main__':
    # Initialize databases
    init_databases()
    
    # Start the Flask development server
    app.run(debug=True)