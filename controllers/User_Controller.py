from flask import render_template, request, redirect, url_for, session, flash
from models.user_model import UserModel

class UserController:
    def __init__(self, user_model: UserModel):
        self.user_model = user_model
    
    def get_current_user(self):
        """Get the current user from the session."""
        if 'user' in session and session['user'].get('email'):
            return session['user']
        if 'user_email' in session:
            result = self.user_model.get(session['user_email'])
            if result['status'] == 'success':
                session['user'] = result['data']
                return result['data']
        return {'email': None, 'team': 'none', 'access': 1}  # Default guest user
    
    def update_user(self):
        """Update user information."""
        # Check user has required access level
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('teams.view'))
        
        email = request.form.get('email')
        team_id = request.form.get('team_id')
        access = request.form.get('access')
        
        if not email:
            flash('Email is required', 'error')
            return redirect(url_for('teams.view'))
        
        user_info = {'email': email}
        if team_id:
            user_info['team_id'] = int(team_id)
        if access:
            user_info['access'] = int(access)
        
        result = self.user_model.update(user_info)
        if result['status'] == 'success':
            flash('User updated successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('teams.view'))
    
    def delete_user(self):
        """Delete a user."""
        # Check user has required access level
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('teams.view'))
        
        email = request.form.get('email')
        if not email:
            flash('Email is required', 'error')
            return redirect(url_for('teams.view'))
        
        # First get user to know their team
        user_result = self.user_model.get(email)
        if user_result['status'] == 'success':
            user = user_result['data']
            if user['team'] != 'none':
                # Remove user from their team will be handled by team controller
                pass
        
        # Now delete the user
        result = self.user_model.remove(email)
        if result['status'] == 'success':
            flash('User deleted successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('teams.view'))
