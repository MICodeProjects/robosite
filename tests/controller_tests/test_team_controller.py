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

    # Also check DB for all teams
    team_model = init_controllers['team_controller'].team_model
    db_teams = team_model.get_all_teams()
    assert db_teams['status'] == 'success'
    assert len(db_teams['data']) >= len(SAMPLE_TEAMS)

def test_create_team(auth_client, init_controllers):
    """Test team creation."""
    response = auth_client.post('/teams/create', data={
        'team_name': 'dragons'
    })
    assert response.status_code == 302
    assert 'teams' in response.location

    # Verify team was created in DB
    team_model = init_controllers['team_controller'].team_model
    db_team = team_model.get_team(team='dragons')
    assert db_team['status'] == 'success'
    assert db_team['data']['name'] == 'dragons'

def test_update_team(auth_client, init_controllers):
    """Test team update."""
    response = auth_client.post('/teams/update', data={
        'team_id': '1',
        'team_name': 'super_phoenixes'
    })
    assert response.status_code == 302
    assert 'teams' in response.location

    # Verify team was updated in DB
    team_model = init_controllers['team_controller'].team_model
    db_team = team_model.get_team(team='super_phoenixes')
    assert db_team['status'] == 'success'
    assert db_team['data']['name'] == 'super_phoenixes'

def test_unauthorized_team_operations(client, init_controllers):
    """Test unauthorized team operations."""
    operations = [
        ('/teams/create', {'team_name': 'test'}),
        ('/teams/update', {'team_id': '1', 'team_name': 'test'}),
    ]
    team_model = init_controllers['team_controller'].team_model

    # Test with no authentication
    for route, data in operations:
        response = client.post(route, data=data)
        assert response.status_code == 302
        assert 'login' in response.location
        # No DB change should occur
        db_team = team_model.get_team(team=data.get('team_name', 'test'))
        assert db_team['status'] == 'error' or db_team['data'] is None

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
        db_team = team_model.get_team(team=data.get('team_name', 'test'))
        assert db_team['status'] == 'error' or db_team['data'] is None
