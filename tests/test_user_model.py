import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, User, Team
from models import user_model
from tests.test_data.sample_user_data import SAMPLE_USERS
from tests.test_data.sample_team_data import SAMPLE_TEAMS

TEST_DB = "test_data/test_database.db"

@pytest.fixture
def user():
    """Create a fresh User_Model instance for each test using a test database"""
    test_user = user_model.User_Model()
    test_user.initialize_DB(TEST_DB)
    return test_user

@pytest.fixture
def setup_user_data(user):
    """Setup test data before each test"""
    session = user.Session()
    
    try:
        # First create teams (required for foreign key relationships)
        for team_data in SAMPLE_TEAMS:
            team = Team(name=team_data["name"])
            session.add(team)
        session.commit()

        # Then create users
        for user_data in SAMPLE_USERS:
            new_user = User(
                email=user_data["email"],
                team_name=user_data["team"],
                access=user_data["access"]
            )
            session.add(new_user)
        session.commit()
    
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

    yield
    
    # Cleanup after tests
    if os.path.exists(os.path.join(user.data_dir, TEST_DB)):
        os.remove(os.path.join(user.data_dir, TEST_DB))

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup fixture that runs automatically after all tests"""
    yield
    test_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', TEST_DB)
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_user_creation(user, setup_user_data):
    """Test creating a new user"""
    result = user.create({
        "email": "newuser@robotics.com",
        "team": "phoenixes",
        "access": 2
    })
    
    assert result["status"] == "success"
    assert result["data"]["email"] == "newuser@robotics.com"
    
    # Verify in database
    session = user.Session()
    try:
        db_user = session.query(User).filter_by(email="newuser@robotics.com").first()
        assert db_user is not None
        assert db_user.email == "newuser@robotics.com"
        assert db_user.team_name == "phoenixes"
        assert db_user.access == 2
    finally:
        session.close()

def test_user_get_by_email(user, setup_user_data):
    """Test retrieving a user by email"""
    result = user.get("captain@robotics.com")
    
    assert result["status"] == "success"
    assert result["data"]["email"] == "captain@robotics.com"
    assert result["data"]["team"] == "phoenixes"
    assert result["data"]["access"] == 3
    
    # Verify in database
    session = user.Session()
    try:
        db_user = session.query(User).filter_by(email="captain@robotics.com").first()
        assert db_user is not None
        assert db_user.email == "captain@robotics.com"
        assert db_user.team_name == "phoenixes"
        assert db_user.access == 3
    finally:
        session.close()

def test_user_update(user, setup_user_data):
    """Test updating user information"""
    # First verify initial state
    session = user.Session()
    try:
        initial_user = session.query(User).filter_by(email="member1@robotics.com").first()
        assert initial_user.team_name == "phoenixes"
        
        # Perform update
        result = user.update({
            "email": "member1@robotics.com",
            "team": "pigeons"
        })
        
        assert result["status"] == "success"
        assert result["data"]["team"] == "pigeons"
        
        # Verify updated state in database
        session.refresh(initial_user)
        assert initial_user.team_name == "pigeons"
    finally:
        session.close()

def test_user_delete(user, setup_user_data):
    """Test deleting a user"""
    # First verify user exists
    session = user.Session()
    try:
        initial_user = session.query(User).filter_by(email="guest@robotics.com").first()
        assert initial_user is not None
        
        # Perform deletion
        result = user.remove("guest@robotics.com")
        assert result["status"] == "success"
        
        # Verify deletion in database
        session.expire_all()
        deleted_user = session.query(User).filter_by(email="guest@robotics.com").first()
        assert deleted_user is None
    finally:
        session.close()

def test_get_all_users(user, setup_user_data):
    """Test retrieving all users"""
    result = user.get_all()
    
    assert result["status"] == "success"
    
    # Verify against database
    session = user.Session()
    try:
        db_users = session.query(User).all()
        assert len(result["data"]) == len(db_users)
        
        # Verify team relationships are intact
        for db_user in db_users:
            assert db_user.team is not None
            assert isinstance(db_user.team, Team)
    finally:
        session.close()

def test_invalid_user_email(user, setup_user_data):
    """Test getting a nonexistent user"""
    result = user.get("nonexistent@robotics.com")
    
    assert result["status"] == "error"
    assert "not found" in result["data"]
    
    # Verify in database
    session = user.Session()
    try:
        db_user = session.query(User).filter_by(email="nonexistent@robotics.com").first()
        assert db_user is None
    finally:
        session.close()

def test_invalid_team_creation(user, setup_user_data):
    """Test creating a user with invalid team"""
    result = user.create({
        "email": "test@robotics.com",
        "team": "invalid_team",
        "access": 2
    })
    
    assert result["status"] == "error"
    assert "team" in result["data"].lower()
    
    # Verify user was not created in database
    session = user.Session()
    try:
        db_user = session.query(User).filter_by(email="test@robotics.com").first()
        assert db_user is None
    finally:
        session.close()

def test_invalid_access_level(user, setup_user_data):
    """Test creating a user with invalid access level"""
    result = user.create({
        "email": "test@robotics.com",
        "team": "phoenixes",
        "access": 5
    })
    
    assert result["status"] == "error"
    assert "Access must be one of" in result["data"]

def test_duplicate_email(user, setup_user_data):
    """Test creating a user with an email that already exists"""
    result = user.create({
        "email": "captain@robotics.com",  # This email already exists in sample data
        "team": "phoenixes",
        "access": 2
    })
    
    assert result["status"] == "error"
    assert "email already exists" in result["data"].lower()
    
    # Verify no duplicate was created
    session = user.Session()
    try:
        count = session.query(User).filter_by(email="captain@robotics.com").count()
        assert count == 1  # Only one user should exist with this email
    finally:
        session.close()

def test_team_deletion_cascade(user, setup_user_data):
    """Test that updating a team properly updates all associated users"""
    session = user.Session()
    try:
        # First verify we have users in the phoenixes team
        phoenix_users = session.query(User).filter_by(team_name="phoenixes").all()
        assert len(phoenix_users) > 0
        
        # Delete the phoenixes team
        team = session.query(Team).filter_by(name="phoenixes").first()
        session.delete(team)
        session.commit()
        
        # Verify the users are properly handled (should be None or updated based on your cascade rules)
        affected_users = session.query(User).filter_by(team_name="phoenixes").all()
        assert len(affected_users) == 0
    finally:
        session.close()

def test_access_level_validation(user, setup_user_data):
    """Test that invalid access levels are rejected"""
    result = user.create({
        "email": "invalid@robotics.com",
        "team": "phoenixes",
        "access": 5  # Invalid access level
    })
    
    assert result["status"] == "error"
    assert "access level" in result["data"].lower()
    
    # Verify user was not created
    session = user.Session()
    try:
        db_user = session.query(User).filter_by(email="invalid@robotics.com").first()
        assert db_user is None
    finally:
        session.close()