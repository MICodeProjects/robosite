from flask import render_template, request, redirect, url_for, session, flash
from models.user_model import UserModel
from models.team_model import TeamModel  # Import TeamModel

class SessionController:
    def __init__(self, user_model: UserModel, team_model: TeamModel):
        self.user_model = user_model
        self.team_model = team_model

    def index(self):
        """Home page."""
        current_user = self.get_current_user()
        session['user'] = current_user
        return render_template('index.html', user=current_user)

    def login(self):
        """Login page."""
        if request.method == 'POST':
            email = request.form['email']
            # In a real app, you would hash and verify the password
            # password = request.form['password']
            
            user_result = self.user_model.get(email)
            if user_result['status'] == 'success':
                user = user_result['data']
                session['user'] = user
                session['user_email'] = user['email']
                flash('Login successful!', 'success')
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
            
            # Create user
            result = self.user_model.create({
                'email': email,
                'team_id': team_id,
                'access': 2  # Default access level for new members
            })
            
            if result['status'] == 'success':
                # Store user info in session
                session['user'] = result['data']
                session['user_email'] = result['data']['email']
                flash('Registration successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash(result['data'], 'error')
                return render_template('register.html', teams=self.team_model.get_all_teams()["data"])
        
        return render_template('register.html', teams=self.team_model.get_all_teams()["data"])

    def profile(self):
        """Profile page."""
        return render_template('profile.html')

    def settings(self):
        """Settings page."""
        return render_template('settings.html')

    def logout(self):
        """Logout page."""
        session.pop('user', None)
        session.pop('user_email', None)
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    def get_current_user(self):
        """Get the current user from the session."""
        if 'user_email' in session:
            result = self.user_model.get(session['user_email'])
            if result['status'] == 'success':
                return result['data']
        return {'email': None, 'team': 'none', 'access': 1}  # Default guest user
