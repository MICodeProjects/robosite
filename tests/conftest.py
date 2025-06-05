import pytest
from flask import Flask
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app as flask_app

@pytest.fixture
def app():
    """Create a test Flask application."""
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    return flask_app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Create an authenticated client with admin access."""
    with client.session_transaction() as session:
        session['user_email'] = 'captain@robotics.com'
        session['user'] = {
            'email': 'captain@robotics.com',
            'team': 'phoenixes',
            'access': 3
        }
    return client