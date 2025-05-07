import json
import os

class Team_Model:
    """
    Team Model - Handles all interactions with the team database
    
    Attributes:
        - name: string
        - id: int
    """
    
    @staticmethod
    def initialize_DB(DB_name):
        """
        Initializes the team database if it doesn't exist
        
        Args:
            DB_name (str): Name of the database file
            
        Returns:
            bool: True if database was created, False if it already existed
        """
        directory = os.path.dirname(DB_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        if not os.path.exists(DB_name):
            with open(DB_name, 'w') as file:
                json.dump([], file)
            return True
        return False
    
    @staticmethod
    def exists(team=None, id=None):
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
            
        DB_PATH = 'data/teams.json'
        Team_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            teams = json.load(file)
            
        for t in teams:
            if (team and t.get('name') == team) or (id and t.get('id') == id):
                return True
                
        return False
    
    @staticmethod
    def create(team_name):
        """
        Creates a new team
        
        Args:
            team_name (str): Name of the team to create
            
        Returns:
            dict: Created team data or None if team already exists
        """
        if Team_Model.exists(team=team_name):
            return None
            
        DB_PATH = 'data/teams.json'
        Team_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
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
        
        with open(DB_PATH, 'w') as file:
            json.dump(teams, file, indent=2)
            
        return new_team
    
    @staticmethod
    def add_user(email, team_name=None, team_id=None):
        """
        Adds a user to a team
        
        Args:
            email (str): User email to add
            team_name (str, optional): Team name
            team_id (int, optional): Team ID
            
        Returns:
            dict: Updated team data or None if team doesn't exist
        """
        if team_name is None and team_id is None:
            return None
            
        DB_PATH = 'data/teams.json'
        Team_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            teams = json.load(file)
            
        team_found = False
        for team in teams:
            if (team_name and team['name'] == team_name) or (team_id and team['id'] == team_id):
                if email not in team['members']:
                    team['members'].append(email)
                team_found = True
                updated_team = team
                break
                
        if not team_found:
            return None
            
        with open(DB_PATH, 'w') as file:
            json.dump(teams, file, indent=2)
            
        return updated_team
    
    @staticmethod
    def remove_user(email, team_name=None, team_id=None):
        """
        Removes a user from a team
        
        Args:
            email (str): User email to remove
            team_name (str, optional): Team name
            team_id (int, optional): Team ID
            
        Returns:
            dict: Updated team data or None if team doesn't exist or user not in team
        """
        if team_name is None and team_id is None:
            return None
            
        DB_PATH = 'data/teams.json'
        Team_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            teams = json.load(file)
            
        team_found = False
        for team in teams:
            if (team_name and team['name'] == team_name) or (team_id and team['id'] == team_id):
                if email in team['members']:
                    team['members'].remove(email)
                    team_found = True
                    updated_team = team
                break
                
        if not team_found:
            return None
            
        with open(DB_PATH, 'w') as file:
            json.dump(teams, file, indent=2)
            
        return updated_team
    
    @staticmethod
    def get_team(team=None, id=None):
        """
        Gets a team by name or id
        
        Args:
            team (str, optional): Team name
            id (int, optional): Team ID
            
        Returns:
            dict: Team data or None if team doesn't exist
        """
        if team is None and id is None:
            return None
            
        DB_PATH = 'data/teams.json'
        Team_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            teams = json.load(file)
            
        for t in teams:
            if (team and t['name'] == team) or (id and t['id'] == id):
                return t
                
        return None
    
    @staticmethod
    def get_all_teams():
        """
        Gets all teams
        
        Returns:
            list: List of all teams
        """
        DB_PATH = 'data/teams.json'
        Team_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            teams = json.load(file)
            
        return teams
    
    @staticmethod
    def update_team(id, new_data):
        """
        Updates a team
        
        Args:
            id (int): Team ID
            new_data (dict): New team data
            
        Returns:
            dict: Updated team data or None if team doesn't exist
        """
        if not Team_Model.exists(id=id):
            return None
            
        DB_PATH = 'data/teams.json'
        
        with open(DB_PATH, 'r') as file:
            teams = json.load(file)
            
        for team in teams:
            if team['id'] == id:
                # Update only allowed fields
                if 'name' in new_data:
                    team['name'] = new_data['name']
                updated_team = team
                break
                
        with open(DB_PATH, 'w') as file:
            json.dump(teams, file, indent=2)
            
        return updated_team