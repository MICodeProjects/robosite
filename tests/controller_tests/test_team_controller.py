"""Test the Team Controller."""
import pytest
import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from flask import url_for
from tests.test_data.sample_team_data import SAMPLE_TEAMS
from tests.test_data.sample_user_data import SAMPLE_USERS

def test_team_view(auth_client, init_controllers):
    """Test viewing the teams page."""
    response = auth_client.get('/teams')
    assert response.status_code == 200
    
    # Check if all teams are displayed
    for team in SAMPLE_TEAMS:
        assert bytes(team['name'].encode()) in response.data
    
    # Check if team statistics are included
    assert b'completed_assignments' in response.data
    assert b'pending_assignments' in response.data
    assert b'completion_rate' in response.data

def test_create_team(auth_client, init_controllers):
    """Test team creation."""
    # Try to create a new team
    response = auth_client.post('/teams/create', data={
        'team_name': 'dragons'
    })
    assert response.status_code == 302
    assert 'teams' in response.location
    
    # Verify team was created
    response = auth_client.get('/teams')
    assert b'dragons' in response.data

def test_update_team(auth_client, init_controllers):
    """Test team update."""
    # Update an existing team
    response = auth_client.post('/teams/update', data={
        'team_id': '1',
        'team_name': 'super_phoenixes'
    })
    assert response.status_code == 302
    assert 'teams' in response.location
    
    # Verify team was updated
    response = auth_client.get('/teams')
    assert b'super_phoenixes' in response.data

def test_team_stats(auth_client, init_controllers):
    """Test team statistics calculation."""
    response = auth_client.get('/teams')
    assert response.status_code == 200
    
    # Check if all teams have statistics
    for team in SAMPLE_TEAMS:
        assert bytes(f'{team["name"]}' in response.data)
        assert b'completed_assignments' in response.data
        assert b'pending_assignments' in response.data
        assert b'completion_rate' in response.data

def test_unauthorized_team_operations(client, init_controllers):
    """Test unauthorized team operations."""
    operations = [
        ('/teams/create', {'team_name': 'test'}),
        ('/teams/update', {'team_id': '1', 'team_name': 'test'}),
    
    ]
    
    # Test with no authentication
    for route, data in operations:
        response = client.post(route, data=data)
        assert response.status_code == 302
        assert 'login' in response.location
    
    # Test with insufficient access level
    with client.session_transaction() as session:
        session['user_email'] = 'member1@robotics.com'
        session['user'] = {
            'email': 'member1@robotics.com',
            'team': 'phoenixes',
            'access': 2
        }
    
    for route, data in operations:
        response = client.post(route, data=data)
        assert response.status_code == 302
        assert 'index' in response.location
