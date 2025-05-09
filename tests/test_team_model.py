import pytest
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import team_model
from tests.sample_team_data import SAMPLE_TEAMS

Team = team_model.Team_Model()

@pytest.fixture
def setup_team_data():
    """Setup test data before each test"""
    if os.path.exists("data/teams.json"):
        os.remove("data/teams.json")
    
    with open("data/teams.json", "w") as f:
        json.dump(SAMPLE_TEAMS, f)

    yield
    
    if os.path.exists("data/teams.json"):
        os.remove("data/teams.json")

def test_team_creation(setup_team_data):
    """Test creating a new team"""
    result = Team.create("dragons")
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "dragons"
    assert result["data"]["members"] == []
    
    with open("data/teams.json", "r") as f:
        teams = json.load(f)
    
    assert any(t["name"] == "dragons" for t in teams)

def test_team_get_by_name(setup_team_data):
    """Test retrieving a team by name"""
    result = Team.get_team(team="phoenixes")
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "phoenixes"
    assert result["data"]["id"] == 1
    assert len(result["data"]["members"]) == 2

def test_team_update_members(setup_team_data):
    """Test updating team members"""
    result = Team.add_user("new.student@robotics.com", team_name="pigeons")
    
    assert result["status"] == "success"
    assert "new.student@robotics.com" in result["data"]["members"]
    assert len(result["data"]["members"]) == 2

def test_team_delete_member(setup_team_data):
    """Test removing a member from a team"""
    result = Team.remove_user("member1@robotics.com", team_name="phoenixes")
    
    assert result["status"] == "success"
    assert "member1@robotics.com" not in result["data"]["members"]

def test_get_all_teams(setup_team_data):
    """Test retrieving all teams"""
    result = Team.get_all_teams()
    
    assert result["status"] == "success"
    assert len(result["data"]) == len(SAMPLE_TEAMS)

def test_invalid_team_name(setup_team_data):
    """Test getting a nonexistent team"""
    result = Team.get_team(team="nonexistent_team")
    
    assert result["status"] == "error"
    assert "not found" in result["data"]

def test_duplicate_team_creation(setup_team_data):
    """Test creating a team that already exists"""
    result = Team.create("phoenixes")
    
    assert result["status"] == "error"
    assert "already exists" in result["data"]

def test_add_duplicate_member(setup_team_data):
    """Test adding a member that's already in the team"""
    result = Team.add_user("captain@robotics.com", team_name="phoenixes")
    
    assert result["status"] == "error"
    assert "already a member" in result["data"]

def test_remove_nonexistent_member(setup_team_data):
    """Test removing a member that's not in the team"""
    result = Team.remove_user("nonexistent@robotics.com", team_name="phoenixes")
    
    assert result["status"] == "error"
    assert "not a member" in result["data"]