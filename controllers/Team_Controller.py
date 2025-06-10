from flask import render_template, request, redirect, url_for, session, flash
from models.team_model import TeamModel
from models.user_model import UserModel
from controllers.base_controller import BaseController


class TeamController(BaseController):
    def __init__(self, team_model: TeamModel, user_model: UserModel):
        self.team_model = team_model
        self.user_model = user_model

    def view(self):
        """Render the teams page."""
        # Get current user from user controller
        current_user = self.get_current_user()

        # Get all teams
        result = self.team_model.get_all_teams()
        teams = result['data'] if result['status'] == 'success' else []
        
        # Get all users for admin section
        users_result = self.user_model.get_all()
        users = users_result['data'] if users_result['status'] == 'success' else []

        # get user team name
        user_team_id=current_user["team_id"]
        print("user_team_id: ", user_team_id)
        user_team_name = self.team_model.get(id=int(current_user["team_id"]))
        print(f"self.team_model.get with id {current_user['team_id']} result is ", user_team_name)
        
        return render_template('team.html', teams=teams, user_team_name=user_team_name["data"]["name"], users=users, user=current_user)
    
    def create(self):
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
    
    def update(self):
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
    