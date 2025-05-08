import pytest
import os
import json
from models.team_model import Team
from .sample_team_data import SAMPLE_TEAMS

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
    team = Team("dragons", 6, ["new.member@robotics.com"])
    team.save()
    
    with open("data/teams.json", "r") as f:
        teams = json.load(f)
    
    assert any(t["name"] == "dragons" for t in teams)

def test_team_get_by_name(setup_team_data):
    """Test retrieving a team by name"""
    team = Team.get_by_name("phoenixes")
    assert team.name == "phoenixes"
    assert team.id == 1
    assert len(team.members) == 2

def test_team_update_members(setup_team_data):
    """Test updating team members"""
    team = Team.get_by_name("pigeons")
    team.members.append("new.student@robotics.com")
    team.save()
    
    updated_team = Team.get_by_name("pigeons")
    assert "new.student@robotics.com" in updated_team.members
    assert len(updated_team.members) == 2

def test_team_delete(setup_team_data):
    """Test deleting a team"""
    team = Team.get_by_name("hawks")
    team.delete()
    
    with open("data/teams.json", "r") as f:
        teams = json.load(f)
    
    assert not any(t["name"] == "hawks" for t in teams)

def test_get_all_teams(setup_team_data):
    """Test retrieving all teams"""
    teams = Team.get_all()
    assert len(teams) == len(SAMPLE_TEAMS)

def test_invalid_team_name(setup_team_data):
    """Test getting a nonexistent team"""
    with pytest.raises(Exception):
        Team.get_by_name("nonexistent_team")

def test_remove_team_member(setup_team_data):
    """Test removing a member from a team"""
    team = Team.get_by_name("phoenixes")
    team.remove_member("member1@robotics.com")
    team.save()
    
    updated_team = Team.get_by_name("phoenixes")
    assert "member1@robotics.com" not in updated_team.members