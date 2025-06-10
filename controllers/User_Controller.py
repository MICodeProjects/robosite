from flask import render_template, request, redirect, url_for, session, flash
from models.user_model import UserModel
from controllers.base_controller import BaseController


class UserController(BaseController):
    def __init__(self, user_model: UserModel):
        self.user_model = user_model

    
    def update(self):
        """Update user information."""
        
        # Check user has required access level
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('teams.view'))
        
        new_team_id = request.form.get('team_id')
        user_email=request.form.get('email')

        if not user_email:
            flash('Email is required', 'error')
            return redirect(url_for('teams.view'))
        
        user_google_id=self.user_model.get(email=user_email)["data"]["google_id"]

        
        user_info = {'google_id': user_google_id}
        if new_team_id:
            user_info['team_id'] = int(new_team_id)
        # if access:
        #     user_info['access'] = int(access)
        
        result = self.user_model.update(user_info)
        if result['status'] == 'success':
            flash('User updated successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('teams.view'))
    
    def delete(self):
        """Delete a user."""
        # Check user has required access level
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('teams.view'))
        
        google_id = request.form.get('google_id')
        if not google_id:
            flash('google_id is required', 'error')
            return redirect(url_for('teams.view'))
        
        # First get user to know their team
        user_result = self.user_model.get(google_id=google_id)
        if user_result['status'] == 'success':
            user = user_result['data']
            if user['team'] != 'none':
                # Remove user from their team will be handled by team controller
                pass
        
        # Now delete the user
        result = self.user_model.remove(google_id=google_id)
        if result['status'] == 'success':
            flash('User deleted successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('teams.view'))
