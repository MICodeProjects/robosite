import pytest
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import user_model
from tests.sample_user_data import SAMPLE_USERS

@pytest.fixture
def user():
    """Create a fresh User_Model instance for each test"""
    user = user_model.User_Model()
    user.initialize_DB("data/users.json")
    return user

@pytest.fixture
def setup_user_data(user):
    """Setup test data before each test"""
    # Remove existing test data file if it exists
    if os.path.exists("data/users.json"):
        os.remove("data/users.json")
    
    # Create fresh users.json with sample data
    with open("data/users.json", "w") as f:
        json.dump(SAMPLE_USERS, f)

    yield
    
    # Cleanup after tests
    if os.path.exists("data/users.json"):
        os.remove("data/users.json")

def test_user_creation(user, setup_user_data):
    """Test creating a new user"""
    result = user.create({
        "email": "newuser@robotics.com",
        "team": "phoenixes",
        "access": 2
    })
    
    assert result["status"] == "success"
    assert result["data"]["email"] == "newuser@robotics.com"
    
    with open("data/users.json", "r") as f:
        users = json.load(f)
    
    assert any(u["email"] == "newuser@robotics.com" for u in users)

def test_user_get_by_email(user, setup_user_data):
    """Test retrieving a user by email"""
    result = user.get("captain@robotics.com")
    
    assert result["status"] == "success"
    assert result["data"]["email"] == "captain@robotics.com"
    assert result["data"]["team"] == "phoenixes"
    assert result["data"]["access"] == 3

def test_user_update(user, setup_user_data):
    """Test updating user information"""
    result = user.update({
        "email": "member1@robotics.com",
        "team": "pigeons"
    })
    
    assert result["status"] == "success"
    assert result["data"]["team"] == "pigeons"

def test_user_delete(user, setup_user_data):
    """Test deleting a user"""
    result = user.remove("guest@robotics.com")
    
    assert result["status"] == "success"
    
    with open("data/users.json", "r") as f:
        users = json.load(f)
    
    assert not any(u["email"] == "guest@robotics.com" for u in users)

def test_get_all_users(user, setup_user_data):
    """Test retrieving all users"""
    result = user.get_all()
    
    assert result["status"] == "success"
    assert len(result["data"]) == len(SAMPLE_USERS)

def test_invalid_user_email(user, setup_user_data):
    """Test getting a nonexistent user"""
    result = user.get("nonexistent@robotics.com")
    
    assert result["status"] == "error"
    assert "not found" in result["data"]

def test_invalid_team_creation(user, setup_user_data):
    """Test creating a user with invalid team"""
    result = user.create({
        "email": "test@robotics.com",
        "team": "invalid_team",
        "access": 2
    })
    
    assert result["status"] == "error"
    assert "Team must be one of" in result["data"]

def test_invalid_access_level(user, setup_user_data):
    """Test creating a user with invalid access level"""
    result = user.create({
        "email": "test@robotics.com",
        "team": "phoenixes",
        "access": 5
    })
    
    assert result["status"] == "error"
    assert "Access must be one of" in result["data"]