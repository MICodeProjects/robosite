"""Test the Lesson Component Controller."""
import pytest
from flask import url_for
from tests.sample_lesson_component_data import SAMPLE_COMPONENTS

def test_component_view(auth_client, init_controllers):
    """Test viewing a lesson component."""
    response = auth_client.get('/components/1')
    assert response.status_code == 200
    
    # Check if component content is displayed
    component = next(c for c in SAMPLE_COMPONENTS if c['id'] == 1)
    assert bytes(component['title'].encode()) in response.data
    assert bytes(component['content'].encode()) in response.data

def test_create_component(auth_client, init_controllers):
    """Test component creation."""
    # Create a new component
    response = auth_client.post('/components/create', data={
        'lesson_id': '1',
        'title': 'New Component',
        'content': 'Test content',
        'type': 'text'
    })
    assert response.status_code == 302
    assert 'lessons' in response.location
    
    # Verify component was created
    response = auth_client.get('/lessons/1')
    assert b'New Component' in response.data

def test_update_component(auth_client, init_controllers):
    """Test component update."""
    # Update an existing component
    response = auth_client.post('/components/update', data={
        'component_id': '1',
        'lesson_id': '1',
        'title': 'Updated Component',
        'content': 'Updated content',
        'type': 'text'
    })
    assert response.status_code == 302
    assert 'lessons' in response.location
    
    # Verify component was updated
    response = auth_client.get('/components/1')
    assert b'Updated Component' in response.data
    assert b'Updated content' in response.data

def test_delete_component(auth_client, init_controllers):
    """Test component deletion."""
    # Delete a component
    response = auth_client.post('/components/delete', data={
        'component_id': '1',
        'lesson_id': '1'
    })
    assert response.status_code == 302
    assert 'lessons' in response.location
    
    # Verify component was deleted
    response = auth_client.get('/lessons/1')
    component = next(c for c in SAMPLE_COMPONENTS if c['id'] == 1)
    assert bytes(component['title'].encode()) not in response.data

def test_unauthorized_component_operations(client, init_controllers):
    """Test unauthorized component operations."""
    operations = [
        ('/components/create', {'lesson_id': '1', 'title': 'test', 'content': 'test', 'type': 'text'}),
        ('/components/update', {'component_id': '1', 'lesson_id': '1', 'title': 'test', 'content': 'test', 'type': 'text'}),
        ('/components/delete', {'component_id': '1', 'lesson_id': '1'})
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

def test_invalid_component_operations(auth_client, init_controllers):
    """Test invalid component operations."""
    # Try to view non-existent component
    response = auth_client.get('/components/999')
    assert response.status_code == 302
    
    # Try to update non-existent component
    response = auth_client.post('/components/update', data={
        'component_id': '999',
        'lesson_id': '1',
        'title': 'test',
        'content': 'test',
        'type': 'text'
    })
    assert response.status_code == 302
    
    # Try to delete non-existent component
    response = auth_client.post('/components/delete', data={
        'component_id': '999',
        'lesson_id': '1'
    })
    assert response.status_code == 302

def test_component_access_levels(client, init_controllers):
    """Test component access level restrictions."""
    # Test with no authentication
    response = client.get('/components/1')
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
    response = client.get('/components/1')
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
    response = client.get('/components/1')
    assert response.status_code == 200
