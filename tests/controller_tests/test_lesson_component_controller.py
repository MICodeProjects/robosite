"""Test the replacewithsmthhhelse Controller."""
import pytest
import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from flask import url_for
from tests.test_data.sample_lesson_component_data import SAMPLE_lesson_componentS

def test_lesson_component_view(auth_client, init_controllers):
    """Test viewing a replacewithsmthhhelse."""
    response = auth_client.get('/lesson_components/1')
    assert response.status_code == 200
    
    # Check if lesson_component content is displayed
    lesson_component = next(c for c in SAMPLE_lesson_componentS if c['id'] == 1)
    assert bytes(lesson_component['title'].encode()) in response.data
    assert bytes(lesson_component['content'].encode()) in response.data

def test_create_lesson_component(auth_client, init_controllers):
    """Test lesson_component creation."""
    # Create a new lesson_component
    response = auth_client.post('/lesson_components/create', data={
        'lesson_id': '1',
        'title': 'New lesson_component',
        'content': 'Test content',
        'type': 'text'
    })
    assert response.status_code == 302
    assert 'lessons' in response.location
    
    # Verify lesson_component was created
    response = auth_client.get('/lessons/1')
    assert b'New lesson_component' in response.data

def test_update_lesson_component(auth_client, init_controllers):
    """Test lesson_component update."""
    # Update an existing lesson_component
    response = auth_client.post('/lesson_components/update', data={
        'lesson_component_id': '1',
        'lesson_id': '1',
        'title': 'Updated lesson_component',
        'content': 'Updated content',
        'type': 'text'
    })
    assert response.status_code == 302
    assert 'lessons' in response.location
    
    # Verify lesson_component was updated
    response = auth_client.get('/lesson_components/1')
    assert b'Updated lesson_component' in response.data
    assert b'Updated content' in response.data

def test_delete_lesson_component(auth_client, init_controllers):
    """Test lesson_component deletion."""
    # Delete a lesson_component
    response = auth_client.post('/lesson_components/delete', data={
        'lesson_component_id': '1',
        'lesson_id': '1'
    })
    assert response.status_code == 302
    assert 'lessons' in response.location
    
    # Verify lesson_component was deleted
    response = auth_client.get('/lessons/1')
    lesson_component = next(c for c in SAMPLE_lesson_componentS if c['id'] == 1)
    assert bytes(lesson_component['title'].encode()) not in response.data

def test_unauthorized_lesson_component_operations(client, init_controllers):
    """Test unauthorized lesson_component operations."""
    operations = [
        ('/lesson_components/create', {'lesson_id': '1', 'title': 'test', 'content': 'test', 'type': 'text'}),
        ('/lesson_components/update', {'lesson_component_id': '1', 'lesson_id': '1', 'title': 'test', 'content': 'test', 'type': 'text'}),
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
    response = auth_client.get('/lesson_components/999')
    assert response.status_code == 302
    
    # Try to update non-existent lesson_component
    response = auth_client.post('/lesson_components/update', data={
        'lesson_component_id': '999',
        'lesson_id': '1',
        'title': 'test',
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
