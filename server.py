from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
# You would import other models as they're implemented
from models import user_model
from models import team_model
from models import unit_model
from models import lesson_model
from models import lesson_component_model

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
# DB_names
robosite_db_location = "/models/robosite_db.db"

# Initialize models

from models.user_model import User_Model
from models.team_model import Team_Model
from models.unit_model import Unit_Model
from models.lesson_model import Lesson_Model
from models.lesson_component_model import Lesson_Component_Model

def init_databases():
    """Initialize all database files"""
    User_Model.initialize_DB('data/users.json')
    Team_Model.initialize_DB('data/teams.json')
    Unit_Model.initialize_DB('data/units.json')
    Lesson_Model.initialize_DB('data/lessons.json')
    Lesson_Component_Model.initialize_DB('data/lesson_components.json')
    
    print("All databases initialized successfully!")

# Middleware to check user access level
def get_current_user():
    """Get the current user from the session."""
    if 'user_email' in session:
        return user_model.get(session['user_email'])
    return {'email': None, 'team': 'none', 'access': 1}  # Default guest user


# Routes
@app.route('/')
def index():
    """Home page route."""
    current_user = get_current_user()
    return render_template('index.html', user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route."""
    if request.method == 'POST':
        email = request.form.get('email')
        # In a real app, you would verify password here
        
        user = user_model.get(email)
        if user:
            session['user_email'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('User not found', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout route."""
    session.pop('user_email', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register route."""
    if request.method == 'POST':
        email = request.form.get('email')
        team = request.form.get('team', 'none')
        
        # Default access level is 2 (member) for new registrations
        try:
            user_model.create({
                'email': email,
                'team': team,
                'access': 2  # Default to member access
            })
            session['user_email'] = email
            flash('Registration successful!', 'success')
            return redirect(url_for('index'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('register.html')


@app.route('/to_do')
def to_do():
    """To-do page route."""
    current_user = get_current_user()
    
    # Check if user has sufficient access level
    if current_user['access'] < 2:
        flash('You must be a team member to access this page', 'error')
        return redirect(url_for('index'))
    
    # Here you would fetch tasks from a Task_Model
    tasks = []  # Placeholder for task data
    
    return render_template('to_do.html', user=current_user, tasks=tasks)


@app.route('/team')
def team():
    """Team management page route."""
    current_user = get_current_user()
    
    # Check if user has sufficient access level
    if current_user['access'] < 2:
        flash('You must be a team member to access this page', 'error')
        return redirect(url_for('index'))
    
    # Here you would fetch team data from Team_Model
    teams = {
        'phoenixes': [],
        'pigeons': [],
        'teacher': []
    }
    
    # Group users by team
    all_users = user_model.get_all()
    for user in all_users:
        team_name = user.get('team')
        if team_name in teams:
            teams[team_name].append(user)
    
    return render_template('team.html', user=current_user, teams=teams)


@app.route('/units')
def units():
    """Units listing page route."""
    current_user = get_current_user()
    
    # Here you would fetch units and lessons from Unit_Model and Lesson_Model
    units = []  # Placeholder for unit data
    
    return render_template('units.html', user=current_user, units=units)


@app.route('/lesson/<int:lesson_id>')
def lesson(lesson_id):
    """Lesson page route."""
    current_user = get_current_user()
    
    # Here you would fetch lesson and components from Lesson_Model and Lesson_Component_Model
    lesson_data = {
        'id': lesson_id,
        'name': f'Sample Lesson {lesson_id}',
        'unit_id': 1,
        'type': 1,
        'img': 'placeholder.jpg'
    }
    
    components = [
        {
            'id': 1,
            'name': 'Introduction',
            'type': 1,
            'content': 'This is the introduction to the lesson.'
        },
        {
            'id': 2,
            'name': 'Main Content',
            'type': 2,
            'content': 'This is the main content of the lesson.'
        }
    ]
    
    return render_template('lesson.html', 
                           user=current_user, 
                           lesson=lesson_data, 
                           components=components)


# User management routes (for access level 3)
@app.route('/admin/users')
def admin_users():
    """Admin user management route."""
    current_user = get_current_user()
    
    # Check if user has sufficient access level
    if current_user['access'] < 3:
        flash('You must be a captain or teacher to access this page', 'error')
        return redirect(url_for('index'))
    
    users = user_model.get_all()
    return render_template('admin/users.html', user=current_user, users=users)


@app.route('/admin/users/update/<email>', methods=['POST'])
def admin_update_user(email):
    """Admin update user route."""
    current_user = get_current_user()
    
    # Check if user has sufficient access level
    if current_user['access'] < 3:
        flash('You must be a captain or teacher to perform this action', 'error')
        return redirect(url_for('index'))
    
    team = request.form.get('team')
    access = int(request.form.get('access', 2))
    
    try:
        user_model.update({
            'email': email,
            'team': team,
            'access': access
        })
        flash(f'User {email} updated successfully', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('admin_users'))


@app.route('/admin/users/delete/<email>')
def admin_delete_user(email):
    """Admin delete user route."""
    current_user = get_current_user()
    
    # Check if user has sufficient access level
    if current_user['access'] < 3:
        flash('You must be a captain or teacher to perform this action', 'error')
        return redirect(url_for('index'))
    
    # Don't allow deleting yourself
    if email == current_user['email']:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin_users'))
    
    if user_model.remove(email):
        flash(f'User {email} deleted successfully', 'success')
    else:
        flash(f'User {email} not found', 'error')
    
    return redirect(url_for('admin_users'))


if __name__ == '__main__':
    init_databases()
    app.run(debug=True)