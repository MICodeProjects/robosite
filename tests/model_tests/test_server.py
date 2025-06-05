"""Test the Flask server routes and middleware."""
import pytest

def test_index_page(client):
    """Test the index page is accessible to all users."""
    response = client.get('/')
    assert response.status_code == 200

def test_teams_page_requires_auth(client):
    """Test teams page requires authentication."""
    response = client.get('/teams')
    assert response.status_code == 302  # Redirect to login
    assert 'login' in response.location

def test_teams_page_with_auth(auth_client):
    """Test teams page is accessible when authenticated."""
    response = auth_client.get('/teams')
    assert response.status_code == 200
    assert b'Robotics Teams' in response.data

def test_access_control_member_routes(client):
    """Test routes requiring member access (level 2)."""
    routes = [
        '/units',
        '/teams',
        '/lessons/1',
        '/lesson_components/1',
        '/todo'
    ]
    
    # Test without authentication
    for route in routes:
        response = client.get(route)
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
    
    for route in routes:
        response = client.get(route)
        assert response.status_code == 302
        assert 'index' in response.location

def test_access_control_admin_routes(client):
    """Test routes requiring admin access (level 3)."""
    routes = [
        ('/teams/create', 'POST'),
        ('/teams/update', 'POST'),
        ('/users/update', 'POST'),
        ('/users/delete', 'POST'),
        ('/units/create', 'POST'),
        ('/units/update', 'POST'),
        ('/units/delete', 'POST')
    ]
    
    # Test with member access (level 2)
    with client.session_transaction() as session:
        session['user_email'] = 'member1@robotics.com'
        session['user'] = {
            'email': 'member1@robotics.com',
            'team': 'phoenixes',
            'access': 2
        }
    
    for route, method in routes:
        if method == 'POST':
            response = client.post(route, data={})
        else:
            response = client.get(route)
            
        assert response.status_code == 302
        assert 'index' in response.location

def test_static_files(client):
    """Test static files are served correctly."""
    response = client.get('/static/css/styles.css')
    assert response.status_code == 200
    assert response.content_type == 'text/css; charset=utf-8'

def test_404_handling(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent')
    assert response.status_code == 404

def test_session_management(auth_client):
    """Test session management."""
    response = auth_client.get('/teams')
    assert response.status_code == 200
    
    with auth_client.session_transaction() as session:
        assert 'user_email' in session
        assert session['user']['access'] == 3
        assert session['user']['team'] == 'phoenixes'
