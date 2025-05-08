import pytest
import os
import json
from .models.user_model import User_Model
from .sample_user_data import SAMPLE_USERS

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
    user = User_Model("newuser@robotics.com", "newteam", 2)
    user.save()
    
    with open("data/users.json", "r") as f:
        users = json.load(f)
    
    assert any(u["email"] == "newuser@robotics.com" for u in users)

def test_user_get_by_email(setup_user_data):
    """Test retrieving a user by email"""
    user = User_Model.get_by_email("captain@robotics.com")
    assert user.email == "captain@robotics.com"
    assert user.team == "phoenixes"
    assert user.access == 3

def test_user_update(setup_user_data):
    """Test updating user information"""
    user = User_Model.get_by_email("member1@robotics.com")
    user.team = "eagles"
    user.save()
    
    updated_user = User_Model.get_by_email("member1@robotics.com")
    assert updated_user.team == "eagles"

def test_user_delete(setup_user_data):
    """Test deleting a user"""
    user = User_Model.get_by_email("guest@robotics.com")
    user.delete()
    
    with open("data/users.json", "r") as f:
        users = json.load(f)
    
    assert not any(u["email"] == "guest@robotics.com" for u in users)

def test_get_all_users(setup_user_data):
    """Test retrieving all users"""
    users = User_Model.get_all()
    assert len(users) == len(SAMPLE_USERS)

def test_invalid_user_email(setup_user_data):
    """Test getting a nonexistent user"""
    with pytest.raises(Exception):
        User_Model.get_by_email("nonexistent@robotics.com")