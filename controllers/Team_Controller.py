from flask import render_template, request, redirect, url_for, session, flash
from models.team_model import Team_Model
from models.user_model import User_Model

class Team_Controller:
    def __init__(self, team_model: Team_Model, user_model: User_Model):
        self.team_model = team_model
        self.user_model = user_model

    def view(self):
        """Render the teams page."""
        # Get current user from user controller
        current_user = self.get_current_user()
        # Put user in session for template to access
        session['user'] = current_user
        
        # Get all teams
        result = self.team_model.get_all_teams()
        teams = result['data'] if result['status'] == 'success' else []
        
        # Get all users for admin section
        all_users_result = self.user_model.get_all()
        all_users = all_users_result['data'] if all_users_result['status'] == 'success' else []
        
        # Calculate team statistics
        for team in teams:
            # Add placeholder stats for now
            team['stats'] = {
                'completed_assignments': 0,
                'pending_assignments': 0,
                'completion_rate': 0
            }
        
        return render_template('team.html', teams=teams, all_users=all_users)
    
    def create_team(self):
        """Create a new team."""
        # Check user has required access level
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('teams.view'))
        
        team_name = request.form.get('team_name')
        if not team_name:
            flash('Team name is required', 'error')
            return redirect(url_for('teams.view'))
        
        result = self.team_model.create(team_name)
        if result['status'] == 'success':
            flash('Team created successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('teams.view'))
    
    def update_team(self):
        """Update a team's information."""
        # Check user has required access level
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('teams.view'))
        
        team_id = request.form.get('team_id')
        team_name = request.form.get('team_name')
        
        if not team_id or not team_name:
            flash('Team ID and name are required', 'error')
            return redirect(url_for('teams.view'))
        
        result = self.team_model.update_team(int(team_id), {'name': team_name})
        if result['status'] == 'success':
            flash('Team updated successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('teams.view'))
    
    def add_user_to_team(self):
        """Add a user to a team."""
        # Check user has required access level
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('teams.view'))
        
        email = request.form.get('email')
        team_id = request.form.get('team_id')
        
        if not email or not team_id:
            flash('Email and team ID are required', 'error')
            return redirect(url_for('teams.view'))
        
        result = self.team_model.add_user(email=email, team_id=int(team_id))
        if result['status'] == 'success':
            # Also update user's team field
            user_update = self.user_model.update({'email': email, 'team': result['data']['name']})
            if user_update['status'] == 'success':
                flash('User added to team successfully', 'success')
            else:
                flash('User added but failed to update user record', 'warning')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('teams.view'))
    
    def remove_user_from_team(self):
        """Remove a user from a team."""
        # Check user has required access level
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('teams.view'))
        
        email = request.form.get('email')
        team_id = request.form.get('team_id')
        
        if not email or not team_id:
            flash('Email and team ID are required', 'error')
            return redirect(url_for('teams.view'))
        
        result = self.team_model.remove_user(email=email, team_id=int(team_id))
        if result['status'] == 'success':
            # Also update user's team field
            user_update = self.user_model.update({'email': email, 'team': 'none'})
            if user_update['status'] == 'success':
                flash('User removed from team successfully', 'success')
            else:
                flash('User removed but failed to update user record', 'warning')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('teams.view'))
    
    def get_current_user(self):
        """Get the current user from the session."""
        if 'user_email' in session:
            result = self.user_model.get(session['user_email'])
            if result['status'] == 'success':
                return result['data']
        return {'email': None, 'team': 'none', 'access': 1}  # Default guest user
