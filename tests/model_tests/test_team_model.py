import pytest
import os
import sys
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, Team, User
from models import team_model
from test_data.sample_team_data import SAMPLE_TEAMS
from test_data.sample_user_data import SAMPLE_USERS

# Use SQLite in-memory database for testing
TEST_DB = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def engine():
    """Create a fresh database engine for each test"""
    engine = create_engine(TEST_DB)
    Base.metadata.create_all(engine)  # Create all tables
    return engine

@pytest.fixture(scope="function")
def session(engine):
    """Create a new session for each test"""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture(scope="function")
def team(engine):
    """Create a fresh Team_Model instance for each test"""
    test_team = team_model.Team_Model()
    test_team.initialize_DB(TEST_DB)
    return test_team

@pytest.fixture
def setup_team_data(session):
    """Setup test data before each test"""
    try:
        # Clean up any existing data
        session.query(User).delete()
        session.query(Team).delete()
        session.commit()
        
        # Create sample teams
        created_teams = {}
        for team_data in SAMPLE_TEAMS:
            team = Team(
                name=team_data["name"]
            )
            session.add(team)
            session.flush()  # This will set the team.id
            created_teams[team_data["id"]] = team

        # Create users and associate them with teams
        for user_data in SAMPLE_USERS:
            if user_data.get("team_id"):
                team = created_teams.get(user_data["team_id"])
                if team:
                    user = User(
                        email=user_data["email"],
                        access=user_data["access"],
                        team=team
                    )
                    session.add(user)

        session.commit()
        yield
    finally:
        # Clean up after each test
        session.query(User).delete()
        session.query(Team).delete()
        session.commit()

def test_team_creation(team, setup_team_data):
    """Test creating a new team"""
    result = team.create("dragons")
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "dragons"
    assert result["data"]["members"] == []

def test_team_get_by_name(team, setup_team_data):
    """Test retrieving a team by name"""
    result = team.get_team(team="phoenixes")
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "phoenixes"
    assert len(result["data"]["members"]) > 0

def test_team_get_all(team, setup_team_data):
    """Test retrieving all teams"""
    result = team.get_all_teams()
    
    assert result["status"] == "success"
    assert len(result["data"]) == len(SAMPLE_TEAMS)

def test_add_user_to_team(team, setup_team_data):
    """Test adding a user to a team"""
    # First create a team
    new_team = team.create("Test Team")
    team_name = new_team["data"]["name"]
    
    result = team.add_user("test@example.com", team_name)
    
    assert result["status"] == "success"
    
    # Verify user was added
    team_result = team.get_team(team=team_name)
    assert any(member["email"] == "test@example.com" for member in team_result["data"]["members"])

def test_remove_user_from_team(team, setup_team_data):
    """Test removing a user from a team"""
    user_email = next(user["email"] for user in SAMPLE_USERS if user.get("team_id"))
    team_name = next(team["name"] for team in SAMPLE_TEAMS if team["id"] == next(user["team_id"] for user in SAMPLE_USERS if user["email"] == user_email))
    
    result = team.remove_user(user_email, team_name)
    
    assert result["status"] == "success"
    
    # Verify user was removed
    team_result = team.get_team(team=team_name)
    assert not any(member["email"] == user_email for member in team_result["data"]["members"])

def test_invalid_team_name(team, setup_team_data):
    """Test getting a nonexistent team"""
    result = team.get_team(team="nonexistent")
    
    assert result["status"] == "error"
    assert "not found" in result["data"]

def test_duplicate_team_name(team, setup_team_data):
    """Test creating a team with duplicate name"""
    # First create a team
    team.create("Test Team")
    
    # Try to create another team with same name
    result = team.create("Test Team")
    
    assert result["status"] == "error"
    assert "exists" in result["data"].lower()