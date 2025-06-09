import pytest
from flask import Flask
import os
import sys
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import sessionmaker
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app as flask_app
from models.user_model import UserModel
from models.team_model import TeamModel
from models.unit_model import UnitModel
from models.lesson_model import LessonModel
from models.lesson_component_model import LessonComponentModel
from models.database import Base, Team, User, Unit, Lesson, LessonComponent
from tests.test_data.sample_team_data import SAMPLE_TEAMS
from tests.test_data.sample_user_data import SAMPLE_USERS
from tests.test_data.sample_unit_data import SAMPLE_UNITS
from tests.test_data.sample_lesson_data import SAMPLE_LESSONS
from tests.test_data.sample_lesson_component_data import SAMPLE_LESSON_COMPONENTS

@pytest.fixture
def app():
    """Create a test Flask application."""
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    flask_app.config['DB_URL'] = 'sqlite:///:memory:'  # Use in-memory DB for testing
    return flask_app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def auth_client(client, init_controllers):
    """Create a test client with an authenticated admin user."""
    user_controller = init_controllers['user_controller']
    user_model = user_controller.user_model
    team_model = init_controllers['team_controller'].team_model    
    team_map = init_controllers['team_map']
    Session = user_model.Session  # Access Session from user_model

    # Get phoenixes team id
    phoenixes_team_id = team_map.get("phoenixes")
    if not phoenixes_team_id:
        # If phoenixes team doesn't exist, create it
        team = Team(name="phoenixes")
        with Session() as session:
            session.add(team)
            session.commit()
            phoenixes_team_id = team.id

    # Ensure admin user exists and is in phoenixes team
    if not user_model.exists(email='admin@robotics.com')["data"]:
        user_controller.create({
            'email': 'admin@robotics.com',
            'access': 3,
            'team_id': phoenixes_team_id
        })
    else:
        # Update admin user's team if needed
        admin_user = user_model.get(email='admin@robotics.com')["data"]
        if admin_user['team_id'] != phoenixes_team_id:
            user_controller.update({
                'email': 'admin@robotics.com',
                'team_id': phoenixes_team_id,
                'access': 3
            })

    with client.session_transaction() as session:
        session['user_email'] = 'admin@robotics.com'
        session['user'] = {
            'email': 'admin@robotics.com',
            'team_id': phoenixes_team_id,
            'access': 3
        }
    return client

@pytest.fixture(scope='function')
def init_controllers(app):
    """Initialize controllers for testing."""
    from controllers.User_Controller import UserController
    from controllers.Team_Controller import TeamController
    from controllers.unit_Controller import UnitController
    from controllers.lesson_Controller import LessonController
    from controllers.lesson_component_Controller import LessonComponentController
    from controllers.session_Controller import SessionController
    
    user_model = UserModel()
    team_model = TeamModel()
    unit_model = UnitModel()
    lesson_model = LessonModel()
    lesson_component_model = LessonComponentModel()
    
    # Initialize database
    db_path = app.config.get('DB_URL', 'sqlite:///:memory:')
    user_model.initialize_DB(DB_name=db_path)
    team_model.initialize_DB(DB_name=db_path)
    unit_model.initialize_DB(DB_name=db_path)
    lesson_model.initialize_DB(DB_name=db_path)
    lesson_component_model.initialize_DB(DB_name=db_path)
    
    # Create a session
    Session = user_model.Session
    
    print("\nCreating sample teams...")
    team_map = {}
    with Session() as session:
        for team_data in SAMPLE_TEAMS:
            team = Team(name=team_data['name'].lower())
            session.add(team)
            session.flush()
            team_map[team.name] = team.id
            print(f"Created team: {team.name} with ID: {team.id}")
        session.commit()
    
    print("\nCreating sample users...")
    with Session() as session:
        for user_data in SAMPLE_USERS:
            team_name = next((t['name'].lower() for t in SAMPLE_TEAMS if t['id'] == user_data['team_id']), None)
            team_id = team_map.get(team_name)
            if team_id is None:
                print(f"Warning: team_id {user_data['team_id']} not found for user {user_data['email']}")
                team_id = team_map.get("phoenixes")
                if team_id is None:
                    print("Creating phoenixes team as fallback...")
                    team = Team(name="phoenixes")
                    session.add(team)
                    session.flush()
                    team_map["phoenixes"] = team.id
                    team_id = team.id
        
            user = User(
                email=user_data['email'],
                team_id=team_id,
                access=user_data['access']
            )
            session.add(user)
            print(f"Created user: {user.email} with team_id: {team_id}")
        session.commit()
    
    print("\nCreating sample units...")
    unit_map = {}
    with Session() as session:
        for unit_data in SAMPLE_UNITS:
            unit = Unit(name=unit_data['name'])
            session.add(unit)
            session.flush()
            unit_map[unit_data['id']] = unit.id
        session.commit()
    
    print("\nCreating sample lessons...")
    lesson_map = {}
    with Session() as session:
        for lesson_data in SAMPLE_LESSONS:
            lesson = Lesson(
                name=lesson_data.get("name") or lesson_data.get("title", ""),
                type=lesson_data.get("type", 1),
                img=lesson_data.get("img", ""),
                unit_id=unit_map.get(lesson_data['unit_id'])
            )
            session.add(lesson)
            session.flush()
            lesson_map[lesson_data.get('id')] = lesson.id
            print(f"Created lesson: {lesson.name} with ID: {lesson.id}")
        session.commit()
    
    # Create sample lesson components
    with Session() as session:
        for component_data in SAMPLE_LESSON_COMPONENTS:
            component = LessonComponent(
                name=component_data['name'],
                type=component_data['type'],
                content=component_data['content'],
                lesson_id=lesson_map.get(component_data['lesson_id'])
            )
            session.add(component)
        session.commit()
    
    print("\nVerifying relationships...")
    with Session() as session:
        teams = session.query(Team).all()
        users = session.query(User).all()
        units = session.query(Unit).all()
        lessons = session.query(Lesson).all()
        components = session.query(LessonComponent).all()
    
        print(f"Database contains:")
        print(f"- {len(teams)} teams")
        print(f"- {len(users)} users")
        print(f"- {len(units)} units")
        print(f"- {len(lessons)} lessons")
        print(f"- {len(components)} lesson components")
    
    user_controller = UserController(user_model)
    team_controller = TeamController(team_model, user_model)
    unit_controller = UnitController(unit_model, lesson_model)
    lesson_controller = LessonController(lesson_model, lesson_component_model)
    lesson_component_controller = LessonComponentController(lesson_component_model)
    session_controller = SessionController(user_model, team_model)
    
    # Pass team_map to auth_client
    controller_dict = {
        'user_controller': user_controller,
        'team_controller': team_controller,
        'unit_controller': unit_controller,
        'lesson_controller': lesson_controller,
        'lesson_component_controller': lesson_component_controller,
        'session_controller': session_controller,
        'team_map': team_map
    }
    return controller_dict