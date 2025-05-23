import json
import os
from typing import Dict, List, Optional

class Team_Model:
    """
    Team Model - Handles all interactions with the team database
    
    Attributes:
        - name: string
        - id: int
    """
    
    def __init__(self):
        """Initialize the Team Model with the database file path."""
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.root_dir, 'data')
        self.db_path = None  # Will be set in initialize_DB

    def initialize_DB(self, DB_name: str) -> None:
        """
        Ensure that the JSON database file exists. If not, create it with an empty list.
    
        Args:
            DB_name: The name of the database file (can be relative or absolute path)
        """
        if os.path.isabs(DB_name):
            self.db_path = DB_name
        else:
            # If relative path is provided, make it relative to data directory
            self.db_path = os.path.join(self.root_dir, DB_name)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create the database file if it doesn't exist
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as file:
                json.dump([], file)

    def exists(self, team=None, id=None):
        """
        Checks if a team exists by either name or id
        
        Args:
            team (str, optional): Team name
            id (int, optional): Team ID
            
        Returns:
            bool: True if team exists, False otherwise
        """
        if team is None and id is None:
            return False
            
        with open(self.db_path, 'r') as file:
            teams = json.load(file)
            
        for t in teams:
            if (team and t.get('name') == team) or (id and t.get('id') == id):
                return True
                
        return False
    
    def create(self, team_name: str) -> Dict:
        """Creates a new team"""
        try:
            if self.exists(team=team_name):
                return {"status": "error", "data": f"Team {team_name} already exists"}
                
            with open(self.db_path, 'r') as file:
                teams = json.load(file)
                
            # Generate a new ID
            new_id = 1
            if teams:
                new_id = max(team['id'] for team in teams) + 1
                
            new_team = {
                'name': team_name,
                'id': new_id,
                'members': []
            }
            
            teams.append(new_team)
            
            with open(self.db_path, 'w') as file:
                json.dump(teams, file, indent=2)
                
            return {"status": "success", "data": new_team}
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def add_user(self, email: str, team_name: str = None, team_id: int = None) -> Dict:
        """Adds a user to a team"""
        try:
            if team_name is None and team_id is None:
                return {"status": "error", "data": "Either team_name or team_id must be provided"}
                
            with open(self.db_path, 'r') as file:
                teams = json.load(file)
                
            for team in teams:
                if (team_name and team['name'] == team_name) or (team_id and team['id'] == team_id):
                    if email not in team['members']:
                        team['members'].append(email)
                        with open(self.db_path, 'w') as file:
                            json.dump(teams, file, indent=2)
                        return {"status": "success", "data": team}
                    return {"status": "error", "data": f"User {email} is already a member of this team"}
                    
            return {"status": "error", "data": "Team not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def remove_user(self, email: str, team_name: str = None, team_id: int = None) -> Dict:
        """Removes a user from a team"""
        try:
            if team_name is None and team_id is None:
                return {"status": "error", "data": "Either team_name or team_id must be provided"}
                
            with open(self.db_path, 'r') as file:
                teams = json.load(file)
                
            for team in teams:
                if (team_name and team['name'] == team_name) or (team_id and team['id'] == team_id):
                    if email in team['members']:
                        team['members'].remove(email)
                        with open(self.db_path, 'w') as file:
                            json.dump(teams, file, indent=2)
                        return {"status": "success", "data": team}
                    return {"status": "error", "data": f"User {email} is not a member of this team"}
                    
            return {"status": "error", "data": "Team not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get_team(self, team: str = None, id: int = None) -> Dict:
        """Gets a team by name or id"""
        try:
            if team is None and id is None:
                return {"status": "error", "data": "Either team name or id must be provided"}
                
            with open(self.db_path, 'r') as file:
                teams = json.load(file)
                
            for t in teams:
                if (team and t['name'] == team) or (id and t['id'] == id):
                    return {"status": "success", "data": t}
                    
            return {"status": "error", "data": "Team not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get_all_teams(self) -> Dict:
        """Gets all teams"""
        try:
            with open(self.db_path, 'r') as file:
                teams = json.load(file)
                
            return {"status": "success", "data": teams}
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def update_team(self, id: int, new_data: Dict) -> Dict:
        """Updates a team"""
        try:
            if not self.exists(id=id):
                return {"status": "error", "data": f"Team with id {id} not found"}
                
            with open(self.db_path, 'r') as file:
                teams = json.load(file)
                
            for team in teams:
                if team['id'] == id:
                    # Update only allowed fields
                    if 'name' in new_data:
                        team['name'] = new_data['name']
                    updated_team = team
                    break
                    
            with open(self.db_path, 'w') as file:
                json.dump(teams, file, indent=2)
                
            return {"status": "success", "data": updated_team}
        except Exception as e:
            return {"status": "error", "data": str(e)}