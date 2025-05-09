import pytest
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import user_model
from tests.sample_user_data import SAMPLE_USERS


User = user_model.User_Model()

@pytest.fixture
def setup_user_data():
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

def test_user_creation(setup_user_data):
    """Test creating a new user"""
    result = User.create({
        "email": "newuser@robotics.com",
        "team": "phoenixes",
        "access": 2
    })
    
    assert result["status"] == "success"
    assert result["data"]["email"] == "newuser@robotics.com"
    
    with open("data/users.json", "r") as f:
        users = json.load(f)
    
    assert any(u["email"] == "newuser@robotics.com" for u in users)

def test_user_get_by_email(setup_user_data):
    """Test retrieving a user by email"""
    result = User.get("captain@robotics.com")
    
    assert result["status"] == "success"
    assert result["data"]["email"] == "captain@robotics.com"
    assert result["data"]["team"] == "phoenixes"
    assert result["data"]["access"] == 3

def test_user_update(setup_user_data):
    """Test updating user information"""
    result = User.update({
        "email": "member1@robotics.com",
        "team": "eagles"
    })
    
    assert result["status"] == "success"
    assert result["data"]["team"] == "eagles"

def test_user_delete(setup_user_data):
    """Test deleting a user"""
    result = User.remove("guest@robotics.com")
    
    assert result["status"] == "success"
    
    with open("data/users.json", "r") as f:
        users = json.load(f)
    
    assert not any(u["email"] == "guest@robotics.com" for u in users)

def test_get_all_users(setup_user_data):
    """Test retrieving all users"""
    result = User.get_all()
    
    assert result["status"] == "success"
    assert len(result["data"]) == len(SAMPLE_USERS)

def test_invalid_user_email(setup_user_data):
    """Test getting a nonexistent user"""
    result = User.get("nonexistent@robotics.com")
    
    assert result["status"] == "error"
    assert "not found" in result["data"]

def test_invalid_team_creation(setup_user_data):
    """Test creating a user with invalid team"""
    result = User.create({
        "email": "test@robotics.com",
        "team": "invalid_team",
        "access": 2
    })
    
    assert result["status"] == "error"
    assert "Team must be one of" in result["data"]

def test_invalid_access_level(setup_user_data):
    """Test creating a user with invalid access level"""
    result = User.create({
        "email": "test@robotics.com",
        "team": "phoenixes",
        "access": 5
    })
    
    assert result["status"] == "error"
    assert "Access must be one of" in result["data"]