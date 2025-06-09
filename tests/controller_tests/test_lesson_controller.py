"""Test the Lesson Controller."""
import pytest
import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from flask import url_for
from tests.test_data.sample_lesson_data import SAMPLE_LESSONS
from tests.test_data.sample_lesson_component_data import SAMPLE_LESSON_COMPONENTS

def test_lesson_view(auth_client, init_controllers):
    """Test viewing a lesson."""
    # Test viewing a specific lesson
    response = auth_client.get('/lessons/1')
    assert response.status_code == 200
    
    # Check if lesson content is displayed
    lesson = next(l for l in SAMPLE_LESSONS if l['id'] == 1)
    assert bytes(lesson['name'].encode()) in response.data
    assert bytes(lesson['description'].encode()) in response.data
      # Check if lesson component are displayed
    lesson_components = [c for c in SAMPLE_LESSON_COMPONENTS if c['lesson_id'] == 1]
    for lesson_component in lesson_components:
        assert bytes(lesson_component['name'].encode()) in response.data

def test_create_lesson(auth_client, init_controllers):
    """Test lesson creation."""
    # Create a new lesson
    new_lesson = {
        'unit_id': '1',
        'name': 'New Lesson',
        'description': 'Test description',
        'order': '3'
    }
    response = auth_client.post('/lessons/create', data=new_lesson)
    assert response.status_code == 302
    assert response.location == '/'
    
    # Verify lesson was created in DB
    lesson_model = init_controllers['lesson_controller'].lesson_model
    db_lessons = lesson_model.get_all()
    assert any(l.get('name') == 'New Lesson' or l.get('name') == 'New Lesson' for l in db_lessons['data'])

def test_update_lesson(auth_client, init_controllers):
    """Test lesson update."""
    # Update an existing lesson
    response = auth_client.post('/lessons/update', data={
        'lesson_id': '1',
        'unit_id': '1',
        'name': 'Updated Lesson',
        'description': 'Updated description',
        'order': '1'
    })
    assert response.status_code == 302
    assert 'units' in response.location
    
    # Verify lesson was updated in DB
    lesson_model = init_controllers['lesson_controller'].lesson_model
    db_lesson = lesson_model.get(id=1)
    assert db_lesson['status'] == 'success'
    assert db_lesson['data'].get('name', db_lesson['data'].get('name')) == 'Updated Lesson'

def test_delete_lesson(auth_client, init_controllers):
    """Test lesson deletion."""
    # Delete a lesson
    response = auth_client.post('/lessons/delete', data={
        'lesson_id': '1'
    })
    assert response.status_code == 302
    assert 'units' in response.location
    
    # Verify lesson was deleted in DB
    lesson_model = init_controllers['lesson_controller'].lesson_model
    db_lesson = lesson_model.get(id=1)
    assert db_lesson['status'] == 'error'
    assert 'not found' in db_lesson['data']

def test_unauthorized_lesson_operations(client, init_controllers):
    """Test unauthorized lesson operations."""
    operations = [
        ('/lessons/create', {'unit_id': '1', 'name': 'test', 'description': 'test', 'order': '1'}),
        ('/lessons/update', {'lesson_id': '1', 'unit_id': '1', 'name': 'test', 'description': 'test', 'order': '1'}),
        ('/lessons/delete', {'lesson_id': '1'})
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

def test_invalid_lesson_operations(auth_client, init_controllers):
    """Test invalid lesson operations."""
    # Try to view non-existent lesson
    response = auth_client.get('/lessons/999')
    assert response.status_code == 302
    assert 'units' in response.location
    
    # Try to update non-existent lesson
    response = auth_client.post('/lessons/update', data={
        'lesson_id': '999',
        'unit_id': '1',
        'name': 'test',
        'description': 'test',
        'order': '1'
    })
    assert response.status_code == 302
    assert 'units' in response.location

def test_lesson_component_list(auth_client, init_controllers):
    """Test lesson component listing."""
    response = auth_client.get('/lessons/1')
    assert response.status_code == 200
      # Check if all lesson_components for lesson 1 are listed
    lesson_components = [c for c in SAMPLE_LESSON_COMPONENTS if c['lesson_id'] == 1]
    for lesson_component in lesson_components:
        assert bytes(lesson_component['name'].encode()) in response.data
        # Check if lesson_component type is indicated
        assert bytes(lesson_component['type'].encode()) in response.data

def test_lesson_navigation(auth_client, init_controllers):
    """Test lesson navigation structure."""
    response = auth_client.get('/lessons/1')
    assert response.status_code == 200
    
    # Check if navigation elements exist
    assert b'lesson-sidebar' in response.data
    assert b'lesson-content' in response.data
      # Check if lesson components are in order
    lesson_components = [c for c in SAMPLE_LESSON_COMPONENTS if c['lesson_id'] == 1]
    sorted_lesson_components = sorted(lesson_components, key=lambda x: x['order'])
    content = response.data.decode('utf-8')
    last_pos = 0
    for lesson_component in sorted_lesson_components:
        pos = content.find(lesson_component['name'])
        assert pos > last_pos
        last_pos = pos

def test_lesson_access_levels(client, init_controllers):
    """Test lesson access level restrictions."""
    # Test with no authentication
    response = client.get('/lessons/1')
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
    response = client.get('/lessons/1')
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
    response = client.get('/lessons/1')
    assert response.status_code == 200
