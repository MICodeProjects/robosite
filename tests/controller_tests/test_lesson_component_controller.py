"""Test the lesson component Controller."""
import pytest
import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from flask import url_for
from tests.test_data.sample_lesson_component_data import SAMPLE_LESSON_COMPONENTS

def test_lesson_component_view(auth_client, init_controllers):
    """Test viewing a lesson component."""
    response = auth_client.get('/lessons/1/1/1')  # unit_id=1, lesson_id=1, lesson_component_id=1
    assert response.status_code == 200
      # Check if lesson_component content is displayed
    lesson_component = next(c for c in SAMPLE_LESSON_COMPONENTS if c['id'] == 1)
    assert bytes(lesson_component['name'].encode()) in response.data
    assert bytes(lesson_component['content'].encode()) in response.data
    # Check if lesson_component type is displayed
    if 'type' in lesson_component:
        assert bytes(str(lesson_component['type']).encode()) in response.data

def test_create_lesson_component(auth_client, init_controllers):
    """Test lesson_component creation."""
    # Create a new lesson_component
    response = auth_client.post('/lesson_components/create', data={
        'lesson_id': '1',
        'name': 'New lesson_component',
        'content': 'Test content',
        'type': 'text'
    })
    assert response.status_code == 302
    assert 'lessons' in response.location

    # Verify lesson_component was created in DB
    lesson_component_model = init_controllers['lesson_component_controller'].lesson_component_model
    db_components = lesson_component_model.get_all()
    assert any(c.get('name') == 'New lesson_component' for c in db_components['data'])

def test_update_lesson_component(auth_client, init_controllers):
    """Test lesson_component update."""
    # Update an existing lesson_component
    response = auth_client.post('/lesson_components/update', data={
        'lesson_component_id': '1',
        'lesson_id': '1',
        'name': 'Updated lesson_component',
        'content': 'Updated content',
        'type': 'text'
    })
    assert response.status_code == 302
    assert 'lessons' in response.location

    # Verify lesson_component was updated in DB
    lesson_component_model = init_controllers['lesson_component_controller'].lesson_component_model
    db_component = lesson_component_model.get(id=1)
    assert db_component['status'] == 'success'
    assert db_component['data'].get('name', db_component['data'].get('name')) == 'Updated lesson_component'

def test_delete_lesson_component(auth_client, init_controllers):
    """Test lesson_component deletion."""
    # Delete a lesson_component
    response = auth_client.post('/lesson_components/delete', data={
        'lesson_component_id': '1',
        'lesson_id': '1'
    })
    assert response.status_code == 302
    assert 'lessons' in response.location

    # Verify lesson_component was deleted in DB
    lesson_component_model = init_controllers['lesson_component_controller'].lesson_component_model
    db_component = lesson_component_model.get(id=1)
    assert db_component['status'] == 'error'
    assert 'not found' in db_component['data']

def test_unauthorized_lesson_component_operations(client, init_controllers):
    """Test unauthorized lesson_component operations."""
    operations = [
        ('/lesson_components/create', {'lesson_id': '1', 'name': 'test', 'content': 'test', 'type': 'text'}),
        ('/lesson_components/update', {'lesson_component_id': '1', 'lesson_id': '1', 'name': 'test', 'content': 'test', 'type': 'text'}),
        ('/lesson_components/delete', {'lesson_component_id': '1', 'lesson_id': '1'})
    ]
    
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

def test_invalid_lesson_component_operations(auth_client, init_controllers):
    """Test invalid lesson_component operations."""
    # Try to view non-existent lesson_component
    response = auth_client.get('/lessons/1/1/999')
    assert response.status_code == 302
    
    # Try to update non-existent lesson_component
    response = auth_client.post('/lesson_components/update', data={
        'lesson_component_id': '999',
        'lesson_id': '1',
        'name': 'test',
        'content': 'test',
        'type': 'text'
    })
    assert response.status_code == 302
    
    # Try to delete non-existent lesson_component
    response = auth_client.post('/lesson_components/delete', data={
        'lesson_component_id': '999',
        'lesson_id': '1'
    })
    assert response.status_code == 302

def test_lesson_component_access_levels(client, init_controllers):
    """Test lesson_component access level restrictions."""
    # Test with no authentication
    response = client.get('/lesson_components/1')
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
    response = client.get('/lesson_components/1')
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
    response = client.get('/lesson_components/1')
    assert response.status_code == 200
