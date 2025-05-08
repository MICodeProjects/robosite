from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
# DB_names
robosite_db_location = "/models/robosite_db.db"

# Initialize models
from models.user_model import User_Model
from models.team_model import Team_Model
from models.unit_model import Unit_Model
from models.lesson_model import Lesson_Model
from models.lesson_component_model import Lesson_Component_Model

def init_databases():
    """Initialize all database files"""
    User_Model.initialize_DB(DB_name='data/users.json')
    Team_Model.initialize_DB(DB_name='data/teams.json')
    Unit_Model.initialize_DB(DB_name='data/units.json')
    Lesson_Model.initialize_DB(DB_name='data/lessons.json')
    Lesson_Component_Model.initialize_DB(DB_name='data/lesson_components.json')
    
    print("All databases initialized successfully!")

# Middleware to check user access level
def get_current_user():
    """Get the current user from the session."""
    if 'user_email' in session:
        return User_Model.get(session['user_email'])
    return {'email': None, 'team': 'none', 'access': 1}  # Default guest user


if __name__ == '__main__':
    init_databases()
    app.run(debug=True)