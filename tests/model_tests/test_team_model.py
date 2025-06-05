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
    engine = create_engine(TEST_DB, echo=True)  # Add echo=True for debugging
    Base.metadata.drop_all(engine)  # Clear all tables
    Base.metadata.create_all(engine)  # Create fresh tables
    return engine

@pytest.fixture(scope="function")
def session(engine):
    """Create a new session for each test"""
    Session = sessionmaker(bind=engine)
    session = Session()
    return session  # Remove yield as we want setup_team_data to manage cleanup

@pytest.fixture(scope="function")
def team(engine, session):  # Add session dependency
    """Create a fresh Team_Model instance for each test"""
    test_team = team_model.Team_Model()
    test_team.initialize_DB(TEST_DB)
    test_team.Session = sessionmaker(bind=engine)  # Use the same engine
    return test_team

@pytest.fixture(scope="function", autouse=True)
def setup_team_data(engine, session, team):  # Add engine and user dependencies
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
                id=team_data["id"],
                name=team_data["name"].lower()  # Ensure lowercase names
            )
            session.add(team)
            created_teams[team_data["id"]] = team
        session.commit()
        
        # Create users
        for user_data in SAMPLE_USERS:
            if user_data.get("team_id"):
                user = User(
                    email=user_data["email"],
                    team_id=user_data["team_id"],
                    access=user_data["access"]
                )
                session.add(user)
        session.commit()
        
        # Verify data was created
        teams = session.query(Team).all()
        users = session.query(User).all()
        print(f"Created {len(teams)} teams and {len(users)} users")  # Debug output
        
        yield
        
        # Cleanup after test (setup_team_data manages cleanup)
        session.query(User).delete()
        session.query(Team).delete()
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

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