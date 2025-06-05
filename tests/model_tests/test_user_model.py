import pytest
import sqlalchemy
import os
import sys
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, User, Team
from models import user_model
from test_data.sample_user_data import SAMPLE_USERS
from test_data.sample_team_data import SAMPLE_TEAMS

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
    return session  # Remove yield as we want setup_user_data to manage cleanup

@pytest.fixture(scope="function")
def user(engine, session):  # Add session dependency
    """Create a fresh User_Model instance for each test"""
    test_user = user_model.User_Model()
    test_user.initialize_DB(TEST_DB)
    test_user.Session = sessionmaker(bind=engine)  # Use the same engine
    return test_user

@pytest.fixture(scope="function", autouse=True)
def setup_user_data(engine, session, user):  # Add engine and user dependencies
    """Setup test data before each test"""
    try:
        # Clear existing data
        session.query(User).delete()
        session.query(Team).delete()
        session.commit()
        
        # Create teams first
        for team_data in SAMPLE_TEAMS:
            team = Team(
                id=team_data["id"],
                name=team_data["name"].lower()  # Ensure lowercase names
            )
            session.add(team)
        session.commit()
        
        # Create users
        for user_data in SAMPLE_USERS:
            new_user = User(
                email=user_data["email"],
                team_id=user_data["team_id"],
                access=user_data["access"]
            )
            session.add(new_user)
        session.commit()
        
        # Verify data was created
        teams = session.query(Team).all()
        users = session.query(User).all()
        print(f"Created {len(teams)} teams and {len(users)} users")  # Debug output
        
        yield
        
        # Cleanup after test
        session.query(User).delete()
        session.query(Team).delete()
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
        
def test_user_creation(user, setup_user_data, session):
    """Test creating a new user"""
    # First ensure the test team exists
    if setup_user_data:  # Use the fixture data
        result = user.create({
            "email": "newuser@robotics.com",
            "team_id": 1,  # phoenixes team
            "access": 2
        })
        assert result["status"] == "success", f"Creation failed. Got response: {result}"
        assert result["data"]["email"] == "newuser@robotics.com", f"Wrong email in response. Got: {result['data']}"
        
        # Verify in database
        db_user = session.query(User).filter_by(email="newuser@robotics.com").first()
        assert db_user is not None, "User was not created in database"
        assert db_user.email == "newuser@robotics.com", f"Wrong email in DB. Got: {db_user.email}"
        assert db_user.team_id == 1, f"Wrong team_id in DB. Got: {db_user.team_id}"
        assert db_user.access == 2, f"Wrong access level in DB. Got: {db_user.access}"

def test_user_get_by_email(user, setup_user_data, session):
    """Test retrieving a user by email"""
    result = user.get("captain@robotics.com")
    assert result["status"] == "success", f"Get failed. Got response: {result["data"]}"
    assert result["data"]["email"] == "captain@robotics.com", f"Wrong email in response. Got: {result['data']}"
    assert result["data"]["team_id"] == 1, f"Wrong team_id in response. Got: {result['data']}"  # phoenixes team
    assert result["data"]["access"] == 3, f"Wrong access level in response. Got: {result['data']}"
    
    # Verify in database
    db_user = session.query(User).filter_by(email="captain@robotics.com").first()
    assert db_user is not None, "User not found in database"
    assert db_user.email == "captain@robotics.com", f"Wrong email in DB. Got: {db_user.email}"
    assert db_user.team_id == 1, f"Wrong team_id in DB. Got: {db_user.team_id}"
    assert db_user.access == 3, f"Wrong access level in DB. Got: {db_user.access}"

def test_user_update(user, setup_user_data):
    """Test updating user information"""    # First verify initial state
    session = user.Session()
    try:
        initial_user = session.query(User).filter_by(email="member1@robotics.com").first()        
        assert initial_user.team_id == 1, f"Initial team_id should be 1 but got: {initial_user.team_id}"  # phoenixes team
        
        # Perform update
        result = user.update({
            "email": "member1@robotics.com",
            "team_id": 2  # pigeons team
        })
        
        assert result["status"] == "success", f"Update failed. Got response: {result}"
        assert result["data"]["team_id"] == 2, f"Update response has wrong team_id. Expected 2, got: {result['data']}"
        
        # Verify updated state in database
        session.refresh(initial_user)
        assert initial_user.team_id == 2, f"Database team_id not updated. Expected 2, got: {initial_user.team_id}"
    finally:
        session.close()

def test_user_delete(user, setup_user_data):
    """Test deleting a user"""
    # First verify user exists
    session = user.Session()
    try:
        initial_user = session.query(User).filter_by(email="guest@robotics.com").first()
        assert initial_user is not None, "Test user not found in database before deletion"
        
        # Perform deletion
        result = user.remove("guest@robotics.com")
        assert result["status"] == "success", f"Deletion failed. Got response: {result}"
        
        # Verify deletion in database
        session.expire_all()
        deleted_user = session.query(User).filter_by(email="guest@robotics.com").first()
        assert deleted_user is None, "User still exists in database after deletion"
    finally:
        session.close()

def test_get_all_users(user, setup_user_data):
    """Test retrieving all users"""
    result = user.get_all()
    
    assert result["status"] == "success", f"Get all users failed. Got response: {result}"
    
    # Verify against database
    session = user.Session()
    try:
        db_users = session.query(User).all()
        assert len(result["data"]) == len(db_users), f"Wrong number of users. Expected {len(db_users)}, got {len(result['data'])}"
        
        # Verify team relationships are intact
        for db_user in db_users:
            if db_user.team !=None:
                assert isinstance(db_user.team, Team), f"Wrong team type for user: {db_user.email}"
    finally:
        session.close()

def test_invalid_user_email(user, setup_user_data):
    """Test getting a nonexistent user"""
    result = user.get("nonexistent@robotics.com")
    
    assert result["status"] == "error", f"Expected error status but got: {result}"
    assert "not found" in result["data"], f"Expected 'not found' message but got: {result['data']}"
    
    # Verify in database
    session = user.Session()
    try:
        db_user = session.query(User).filter_by(email="nonexistent@robotics.com").first()
        assert db_user is None, "User should not exist in database"
    finally:

        session.close()

def test_invalid_team_creation(user, setup_user_data):
    """Test creating a user with invalid team"""
    result = user.create({
        "email": "test@robotics.com",
        "team_id": 999,  # Invalid team ID
        "access": 2
    })
    
    assert result["status"] == "error", f"Expected error status but got: {result}"
    assert "team" in result["data"].lower(), f"Expected error about team but got: {result['data']}"
    
    # Verify user was not created in database
    session = user.Session()
    try:
        db_user = session.query(User).filter_by(email="test@robotics.com").first()
        assert db_user is None, "User should not have been created with invalid team"
    finally:
        session.close()

def test_invalid_access_level(user, setup_user_data):
    """Test creating a user with invalid access level"""
    result = user.create({
        "email": "test@robotics.com",
        "team_id": 1,  # phoenixes team
        "access": 5
    })
    
    assert result["status"] == "error", f"Expected error status but got: {result}"
    assert "Access must be one of" in result["data"], f"Expected access level error but got: {result['data']}"

def test_duplicate_email(user, setup_user_data):
    """Test creating a user with an email that already exists"""
    # First check if email exists
    exists_result = user.exists("captain@robotics.com")
    assert exists_result["status"] == "success"
    assert exists_result["data"] == True
    
    # Try to create user with existing email
    result = user.create({
        "email": "captain@robotics.com",  # This email already exists in sample data
        "team_id": 1,  # phoenixes team
        "access": 2
    })
    
    assert result["status"] == "error"
    assert "already exists" in result["data"].lower()
    
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
        # First verify we have users in team 1 (phoenixes)
        phoenix_users = session.query(User).filter_by(team_id=1).all()
        assert len(phoenix_users) > 0, "No users found in phoenixes team before deletion"
        
        # Delete the phoenixes team
        team = session.query(Team).filter_by(id=1).first()
        session.delete(team)
        session.commit()
        
        # Verify the users are properly handled (should be None or updated based on your cascade rules)
        affected_users = session.query(User).filter_by(team_id=1).all()
        assert len(affected_users) == 0, f"Expected no users with team_id=1 after team deletion, found {len(affected_users)}"
    finally:
        session.close()

def test_access_level_validation(user, setup_user_data):
    """Test that invalid access levels are rejected"""
    result = user.create({
        "email": "invalid@robotics.com",
        "team_id": 1,  # phoenixes team
        "access": 5  # Invalid access level
    })
    
    assert result["status"] == "error"
    assert "access" in result["data"].lower()
    
    # Verify user was not created
    session = user.Session()
    try:
        db_user = session.query(User).filter_by(email="invalid@robotics.com").first()
        assert db_user is None
    finally:
        session.close()