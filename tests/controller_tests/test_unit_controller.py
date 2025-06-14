"""Test the Unit Controller."""
import pytest
import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from flask import url_for
from tests.test_data.sample_unit_data import SAMPLE_UNITS
from tests.test_data.sample_lesson_data import SAMPLE_LESSONS

def test_units_view(auth_client, init_controllers):
    """Test viewing the units page."""
    response = auth_client.get('/units')
    assert response.status_code == 200
    
    # Check if all units are displayed
    for unit in SAMPLE_UNITS:
        assert bytes(unit['name'].encode()) in response.data
    
    # Check if lessons are displayed under units
    for lesson in SAMPLE_LESSONS:
        assert bytes(lesson['name'].encode()) in response.data

def test_create_unit(auth_client, init_controllers):
    """Test unit creation."""
    response = auth_client.post('/units/create', data={
        'unit_name': 'Advanced Robotics'
    })
    assert response.status_code == 302
    assert 'units' in response.location

    # Verify unit was created in DB
    unit_model = init_controllers['unit_controller'].unit_model
    db_units = unit_model.get_all()
    assert any(u['name'] == 'Advanced Robotics' for u in db_units['data'])

def test_update_unit(auth_client, init_controllers):
    """Test unit update."""
    response = auth_client.post('/units/update', data={
        'unit_id': '1',
        'unit_name': 'Updated Robotics Basics'
    })
    assert response.status_code == 302
    assert 'units' in response.location

    # Verify unit was updated in DB
    unit_model = init_controllers['unit_controller'].unit_model
    db_unit = unit_model.get(id=1)
    assert db_unit['status'] == 'success'
    assert db_unit['data']['name'] == 'Updated Robotics Basics'

def test_delete_unit(auth_client, init_controllers):
    """Test unit deletion."""
    response = auth_client.post('/units/delete', data={
        'unit_id': '1'
    })
    assert response.status_code == 302
    assert 'units' in response.location

    # Verify unit was deleted in DB
    unit_model = init_controllers['unit_controller'].unit_model
    db_unit = unit_model.get(id=1)
    assert db_unit['status'] == 'error'
    assert 'not found' in db_unit['data']

def test_unauthorized_unit_operations(client, init_controllers):
    """Test unauthorized unit operations."""
    operations = [
        ('/units/create', {'unit_name': 'test'}),
        ('/units/update', {'unit_id': '1', 'unit_name': 'test'}),
        ('/units/delete', {'unit_id': '1'})
    ]
    unit_model = init_controllers['unit_controller'].unit_model

    # Test with member access (level 2)
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
        # No DB change should occur for update/delete
        if route == '/units/create':
            db_units = unit_model.get_all()
            assert not any(u['name'] == 'test' for u in db_units['data'])
        elif route == '/units/update':
            db_unit = unit_model.get(id=1)
            assert db_unit['status'] == 'success'
            assert db_unit['data']['name'] != 'test'
        elif route == '/units/delete':
            db_unit = unit_model.get(id=1)
            assert db_unit['status'] == 'success'

def test_invalid_unit_operations(auth_client, init_controllers):
    """Test invalid unit operations."""
    # Try to update non-existent unit
    response = auth_client.post('/units/update', data={
        'unit_id': '999',
        'unit_name': 'Test Unit'
    })
    assert response.status_code == 302
    assert 'units' in response.location
    
    # Try to delete non-existent unit
    response = auth_client.post('/units/delete', data={
        'unit_id': '999'
    })
    assert response.status_code == 302
    assert 'units' in response.location

def test_unit_lesson_hierarchy(auth_client, init_controllers):
    """Test unit and lesson hierarchy display."""
    response = auth_client.get('/units')
    assert response.status_code == 200
    
    # Check if units contain their lessons
    for unit in SAMPLE_UNITS:
        unit_lessons = [l for l in SAMPLE_LESSONS if l['unit_id'] == unit['id']]
        for lesson in unit_lessons:
            assert bytes(lesson['name'].encode()) in response.data

def test_unit_access_levels(client, init_controllers):
    """Test unit access level restrictions."""
    # Test with no authentication
    response = client.get('/units')
    assert response.status_code == 302
    assert 'login' in response.location
    
    # Test with guest access (level 1)
    with client.session_transaction() as session:
        session['user_email'] = 'guest@robotics.com'
        session['user'] = {
            'email': 'guest@robotics.com',
            'team': 'none',
            'access': 1
        }
    response = client.get('/units')
    assert response.status_code == 302
    assert 'index' in response.location
    
    # Test with member access (level 2)
    with client.session_transaction() as session:
        session['user_email'] = 'member1@robotics.com'
        session['user'] = {
            'email': 'member1@robotics.com',
            'team': 'phoenixes',
            'access': 2
        }
    response = client.get('/units')
    assert response.status_code == 200
