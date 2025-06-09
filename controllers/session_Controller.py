from flask import render_template, request, redirect, url_for, session, flash
from models.user_model import UserModel
from models.team_model import TeamModel  # Import TeamModel
import os  # Import os module

class SessionController:
    def __init__(self, user_model: UserModel, team_model: TeamModel):
        self.user_model = user_model
        self.team_model = team_model
        # Ensure Session is initialized
        if not hasattr(self.user_model, 'Session') or self.user_model.Session is None:
            db_url = os.environ.get('DB_URL', 'sqlite:///:memory:')
            self.user_model.initialize_DB(db_url)
        if not hasattr(self.team_model, 'Session') or self.team_model.Session is None:
            db_url = os.environ.get('DB_URL', 'sqlite:///:memory:')
            self.team_model.initialize_DB(db_url)

    def index(self):
        """Home page."""
        # Only read from session, do not set session['user'] or session['user_email']
        current_user = self.get_current_user()
        if current_user.get('email'):
            flash('Welcome to Robosite', 'success')
        return render_template('index.html', user=current_user)

    def login(self):
        """Login page."""
        if request.method == 'POST':
            email = request.form['email']
            user_result = self.user_model.get(email)
            
            if user_result['status'] == 'success':
                user = user_result['data']
                # Update session
                session['user'] = user
                session['user_email'] = user['email']
                flash('Welcome to Robosite', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials.', 'error')
                return render_template('login.html')
        return render_template('login.html')

    def register(self):
        """Register page."""
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']  # In real app, hash this!
            team_id = request.form['team']
            
            print(f"Attempting registration for email: {email}, team_id: {team_id}")
            # Create user
            result = self.user_model.create({
                'email': email,
                'team_id': team_id,
                'access': 2  # Default access level for new members
            })
            print(f"User create result: {result}")
            
            if result['status'] == 'success':
                # Update session after successful registration
                session['user'] = result['data']
                session['user_email'] = result['data']['email']
                flash('Welcome to Robosite', 'success')
                print(f"Registration successful for user: {email}")
                return redirect(url_for('index'))
            else:
                flash(result['data'], 'error')
                print(f"Registration failed for user: {email}, reason: {result['data']}")
                return render_template('register.html', teams=self.team_model.get_all_teams()["data"])
        
        print("Rendering register page")
        teams = self.team_model.get_all_teams()
        print(f"Teams data: {teams}")
        return render_template('register.html', teams=teams["data"])

    def profile(self):
        """Profile page."""
        return render_template('profile.html')

    def settings(self):
        """Settings page."""
        return render_template('settings.html')

    def logout(self):
        """Logout page."""
        if 'user' in session:
            session.pop('user', None)
            session.pop('user_email', None)
            flash('You have been successfully logged out.', 'info')
        return redirect(url_for('index'))

    def get_current_user(self):
        """Get the current user from the session."""
        # Prefer session['user'] if present (set after login/register)
        if 'user' in session and session['user'].get('email'):
            return session['user']
        if 'user_email' in session:
            result = self.user_model.get(session['user_email'])
            if result['status'] == 'success':
                return result['data']
            session.pop('user', None)
            session.pop('user_email', None)
        return {'email': None, 'team_id': None, 'access': 1}  # Default guest user
