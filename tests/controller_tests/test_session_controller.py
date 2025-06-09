import pytest
import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from flask import url_for
from tests.test_data.sample_user_data import SAMPLE_USERS

def test_login(client, init_controllers):
    """Test user login."""
    # Try to log in with valid credentials
    response = client.post('/login', data={
        'email': 'member1@robotics.com',
        'password': 'password'  # In real app, this would be a hashed password
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome to Robosite' in response.data
    
    # Check if user is in session
    with client.session_transaction() as session:
        assert session['user']['email'] == 'member1@robotics.com'
        assert session['user']['access'] == 2

def test_logout(client, init_controllers):
    """Test user logout."""
    # Log in a user first
    with client.session_transaction() as session:
        session['user'] = {
            'email': 'member1@robotics.com',
            'team': 'phoenixes',
            'access': 2
        }
    
    # Log out
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been successfully logged out.' in response.data
    
    # Check if user is removed from session
    with client.session_transaction() as session:
        assert 'user' not in session

def test_register(client, init_controllers):
    """Test user registration."""
    # Register a new user
    response = client.post('/register', data={
        'email': 'newuser@robotics.com',
        'password': 'password',
        'team': '1'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome to Robosite' in response.data
    
    # Check if user is in session
    with client.session_transaction() as session:
        assert session['user']['email'] == 'newuser@robotics.com'
        assert session['user']['access'] == 2

def test_index(client, init_controllers):
    """Test index page."""
    # Access index page
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to Robosite' in response.data
