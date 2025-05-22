import pytest
from flask import Flask
import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app as flask_app
from models.user_model import User_Model
from models.team_model import Team_Model
from models.unit_model import Unit_Model
from models.lesson_model import Lesson_Model
from models.lesson_component_model import lesson_component_Model

from controllers.User_Controller import User_Controller
from controllers.Team_Controller import Team_Controller
from controllers.unit_Controller import Unit_Controller
from controllers.lesson_Controller import Lesson_Controller
from controllers.lesson_component_Controller import lesson_component_Controller

from tests.sample_user_data import SAMPLE_USERS
from tests.sample_team_data import SAMPLE_TEAMS
from tests.sample_unit_data import SAMPLE_UNITS
from tests.sample_lesson_data import SAMPLE_LESSONS
from tests.sample_lesson_component_data import SAMPLE_lesson_componentS

@pytest.fixture(autouse=True)
def setup_test_data():
    """Set up test data before any tests run."""
    test_data_dir = 'tests/test_data'
    os.makedirs(test_data_dir, exist_ok=True)
    
    # Initialize test data files with sample data
    test_data = {
        'users.json': SAMPLE_USERS,
        'teams.json': SAMPLE_TEAMS,
        'units.json': SAMPLE_UNITS,
        'lessons.json': SAMPLE_LESSONS,
        'lesson_components.json': SAMPLE_lesson_componentS
    }
    
    for filename, data in test_data.items():
        filepath = os.path.join(test_data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    yield
    
    # Clean up test data after tests complete
    for filename in test_data.keys():
        filepath = os.path.join(test_data_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

@pytest.fixture
def app():
    """Create a test Flask application."""
    flask_app.config.update({
        "TESTING": True,
    })
    return flask_app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture
def init_models():
    """Initialize model instances with test data files."""
    # Create test data directory if it doesn't exist
    os.makedirs('tests/test_data', exist_ok=True)
    
    # Initialize models with test data files
    user_model = User_Model()
    team_model = Team_Model()
    unit_model = Unit_Model()
    lesson_model = Lesson_Model()
    lesson_component_model = lesson_component_Model()
    
    user_model.initialize_DB(DB_name='tests/test_data/users.json')
    team_model.initialize_DB(DB_name='tests/test_data/teams.json')
    unit_model.initialize_DB(DB_name='tests/test_data/units.json')
    lesson_model.initialize_DB(DB_name='tests/test_data/lessons.json')
    lesson_component_model.initialize_DB(DB_name='tests/test_data/lesson_components.json')
    
    return {
        'user_model': user_model,
        'team_model': team_model,
        'unit_model': unit_model,
        'lesson_model': lesson_model,
        'lesson_component_model': lesson_component_model
    }

@pytest.fixture
def init_controllers(init_models):
    """Initialize controller instances with test models."""
    user_controller = User_Controller(init_models['user_model'])
    team_controller = Team_Controller(init_models['team_model'], init_models['user_model'])
    unit_controller = Unit_Controller(init_models['unit_model'], init_models['lesson_model'])
    lesson_controller = Lesson_Controller(init_models['lesson_model'], init_models['lesson_component_model'])
    lesson_component_controller = lesson_component_Controller(init_models['lesson_component_model'])
    
    return {
        'user_controller': user_controller,
        'team_controller': team_controller,
        'unit_controller': unit_controller,
        'lesson_controller': lesson_controller,
        'lesson_component_controller': lesson_component_controller
    }

@pytest.fixture
def auth_client(client):
    """Create an authenticated client with admin access."""
    with client.session_transaction() as session:
        session['user_email'] = 'captain@robotics.com'
        session['user'] = {
            'email': 'captain@robotics.com',
            'team': 'phoenixes',
            'access': 3
        }
    return client
