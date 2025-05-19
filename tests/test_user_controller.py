"""Test the User Controller."""
import pytest
from flask import url_for
from tests.sample_user_data import SAMPLE_USERS

def test_user_update(auth_client, init_controllers):
    """Test updating user information."""
    # Update a user's team and access level
    response = auth_client.post('/users/update', data={
        'email': 'member1@robotics.com',
        'team': 'pigeons',
        'access': '3'
    })
    assert response.status_code == 302
    assert 'teams' in response.location
    
    # Verify user was updated
    response = auth_client.get('/teams')
    assert b'member1@robotics.com' in response.data
    assert b'pigeons' in response.data
    assert b'Captain' in response.data

def test_user_delete(auth_client, init_controllers):
    """Test deleting a user."""
    # Delete a user
    response = auth_client.post('/users/delete', data={
        'email': 'member1@robotics.com'
    })
    assert response.status_code == 302
    assert 'teams' in response.location
    
    # Verify user was deleted
    response = auth_client.get('/teams')
    assert b'member1@robotics.com' not in response.data

def test_unauthorized_user_operations(client, init_controllers):
    """Test unauthorized user operations."""
    operations = [
        ('/users/update', {'email': 'test@test.com', 'team': 'test', 'access': '2'}),
        ('/users/delete', {'email': 'test@test.com'})
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

def test_invalid_user_operations(auth_client, init_controllers):
    """Test invalid user operations."""
    # Try to update non-existent user
    response = auth_client.post('/users/update', data={
        'email': 'nonexistent@robotics.com',
        'team': 'phoenixes',
        'access': '2'
    })
    assert response.status_code == 302
    assert 'teams' in response.location
    
    # Try to delete non-existent user
    response = auth_client.post('/users/delete', data={
        'email': 'nonexistent@robotics.com'
    })
    assert response.status_code == 302
    assert 'teams' in response.location

def test_current_user_session(auth_client, init_controllers):
    """Test current user session management."""
    response = auth_client.get('/teams')
    assert response.status_code == 200
    
    with auth_client.session_transaction() as session:
        assert session['user_email'] == 'captain@robotics.com'
        assert session['user']['access'] == 3
        assert session['user']['team'] == 'phoenixes'

def test_user_access_levels(client, init_controllers):
    """Test user access level restrictions."""
    access_levels = [
        ('guest@robotics.com', 1),
        ('member1@robotics.com', 2),
        ('captain@robotics.com', 3)
    ]
    
    protected_routes = [
        '/teams',
        '/units',
        '/lessons/1'
    ]
    
    admin_routes = [
        ('/users/update', 'POST'),
        ('/users/delete', 'POST')
    ]
    
    for email, access in access_levels:
        with client.session_transaction() as session:
            session['user_email'] = email
            session['user'] = {
                'email': email,
                'team': 'phoenixes' if access > 1 else 'none',
                'access': access
            }
        
        # Test protected routes
        for route in protected_routes:
            response = client.get(route)
            if access >= 2:
                assert response.status_code in [200, 302]  # 302 for valid redirects
            else:
                assert response.status_code == 302
                assert 'index' in response.location
        
        # Test admin routes
        for route, method in admin_routes:
            if method == 'POST':
                response = client.post(route, data={})
            else:
                response = client.get(route)
            
            if access >= 3:
                assert response.status_code == 302
                assert 'teams' in response.location
            else:
                assert response.status_code == 302
                assert 'index' in response.location
