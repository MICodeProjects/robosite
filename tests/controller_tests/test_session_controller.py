import pytest
import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from flask import url_for
from tests.test_data.sample_user_data import SAMPLE_USERS

def test_login(client, init_controllers):
    """Test user login."""
    response = client.post('/login', data={
        'email': 'member1@robotics.com',
        'password': 'password'
    }, follow_redirects=True)
    
    assert response.status_code == 200  # Should redirect and render index
    # assert b'Welcome to Robosite' in response.data
    
    # Check session after redirection
    with client.session_transaction() as session:
        assert session.get('user', {}).get('email') == 'member1@robotics.com'
        assert session.get('user', {}).get('access') == 2

def test_logout(client, init_controllers):
    """Test user logout."""
    # Set up session first
    with client.session_transaction() as session:
        session.clear()  # Clear any existing session
        session['user'] = {
            'email': 'member1@robotics.com',
            'team': 'phoenixes',
            'access': 2
        }
        session['user_email'] = 'member1@robotics.com'
    
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200  # Should redirect to index
    assert b'You have been successfully logged out.' in response.data
    
    # Check if session is cleared
    with client.session_transaction() as session:
        assert 'user' not in session
        assert 'user_email' not in session

def test_register(client, init_controllers):
    """Test user registration."""
    # Use a valid team_id from your test data, e.g., 1 for 'phoenixes'
    response = client.post('/register', data={
        'email': 'newuser@robotics.com',
        'password': 'password',
        'team': '1'  # Pass as string, not int
    }, follow_redirects=False)
    if response.status_code != 302:
        print("Registration response data:", response.data.decode())
    assert response.status_code == 302  # Should redirect on success

    # Follow redirect and check welcome message
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome to Robosite' in response.data

    # Check session after registration
    with client.session_transaction() as session:
        assert session.get('user', {}).get('email') == 'newuser@robotics.com'
        assert session.get('user', {}).get('access') == 2
