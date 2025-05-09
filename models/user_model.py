import os
import json
from typing import Dict, List, Optional, Union


class User_Model:
    """
    User Model class for managing user data in the Robosite application.
    
    This class handles CRUD operations for User entities stored in users.json.
    Each User has email, team, and access level attributes.
    
    Access levels:
    - 1: Guest (cannot submit assignments or edit)
    - 2: Member (can submit assignments and are on a team, but cannot edit)
    - 3: Captain/Teacher (can edit assignments and assign assignments)
    """
    
    def __init__(self):
        """Initialize the User Model with the database file path."""
        # Set the path to the data directory and database file
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        self.db_path = os.path.join(self.data_dir, 'users.json')

    def initialize_DB(self, DB_name: str) -> None:
        """
        Ensure that the JSON database file exists. If not, create it with an empty list.
    
        Args:
            DB_name: The name of the database file
        """
        # Create the data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
        # Use the provided DB_name to construct the path
        self.db_path = os.path.join(self.data_dir, DB_name)
    
        # Create the users database file if it doesn't exist
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as file:
                json.dump([], file)

    def exists(self, email: str) -> bool:
        """
        Check if a user with the given email exists in the database.
        
        Args:
            email: The email to check
            
        Returns:
            bool: True if the user exists, False otherwise
        """
        # Open the database
        with open(self.db_path, 'r') as file:
            users = json.load(file)
        
        # Check if a user with the given email exists
        for user in users:
            if user.get('email') == email:
                return True
        
        return False
    
    def create(self, user_info: Dict) -> Dict:
        """Create a new user in the database."""
        try:
            # Validate required fields
            if 'email' not in user_info:
                return {"status": "error", "data": "Email is required"}
            
            if 'team' not in user_info:
                user_info['team'] = 'none'  # Default team
            
            if 'access' not in user_info:
                user_info['access'] = 1  # Default access level (guest)
                
            # Check valid team options
            valid_teams = ["phoenixes", "pigeons", "none", "teacher"]
            if user_info['team'] not in valid_teams:
                return {"status": "error", "data": f"Team must be one of: {', '.join(valid_teams)}"}
                
            # Check valid access levels
            valid_access = [1, 2, 3]
            if user_info['access'] not in valid_access:
                return {"status": "error", "data": f"Access must be one of: {', '.join(map(str, valid_access))}"}
            
            # Check if user already exists
            if self.exists(user_info['email']):
                return {"status": "error", "data": f"User with email {user_info['email']} already exists"}
            
            # Open the database
            with open(self.db_path, 'r') as file:
                users = json.load(file)
            
            # Add the new user
            users.append(user_info)
            
            # Save the database
            with open(self.db_path, 'w') as file:
                json.dump(users, file, indent=2)
            
            return {"status": "success", "data": user_info}
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get(self, email: str) -> Dict:
        """Get a user by email."""
        try:
            with open(self.db_path, 'r') as file:
                users = json.load(file)
            
            for user in users:
                if user.get('email') == email:
                    return {"status": "success", "data": user}
            
            return {"status": "error", "data": f"User with email {email} not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get_all(self) -> Dict:
        """Get all users from the database."""
        try:
            with open(self.db_path, 'r') as file:
                users = json.load(file)
            return {"status": "success", "data": users}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def update(self, user_info: Dict) -> Dict:
        """Update a user's information."""
        try:
            # Validate required fields
            if 'email' not in user_info:
                return {"status": "error", "data": "Email is required"}
            
            # Check valid team options if provided
            if 'team' in user_info:
                valid_teams = ["phoenixes", "pigeons", "none", "teacher"]
                if user_info['team'] not in valid_teams:
                    return {"status": "error", "data": f"Team must be one of: {', '.join(valid_teams)}"}
            
            # Check valid access levels if provided
            if 'access' in user_info:
                valid_access = [1, 2, 3]
                if user_info['access'] not in valid_access:
                    return {"status": "error", "data": f"Access must be one of: {', '.join(map(str, valid_access))}"}
            
            # Open the database
            with open(self.db_path, 'r') as file:
                users = json.load(file)
            
            # Find and update the user
            for i, user in enumerate(users):
                if user.get('email') == user_info['email']:
                    # Update existing fields
                    for key, value in user_info.items():
                        users[i][key] = value
                    updated_user = users[i]
                    
                    # Save the database
                    with open(self.db_path, 'w') as file:
                        json.dump(users, file, indent=2)
                    
                    return {"status": "success", "data": updated_user}
            
            return {"status": "error", "data": f"User with email {user_info['email']} not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def remove(self, email: str) -> Dict:
        """Remove a user by email."""
        try:
            # Open the database
            with open(self.db_path, 'r') as file:
                users = json.load(file)
            
            initial_count = len(users)
            
            # Remove the user
            users = [user for user in users if user.get('email') != email]
            
            # Check if a user was removed
            if len(users) < initial_count:
                # Save the database
                with open(self.db_path, 'w') as file:
                    json.dump(users, file, indent=2)
                return {"status": "success", "data": "User removed successfully"}
            
            return {"status": "error", "data": f"User with email {email} not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}

 

# Example usage
if __name__ == "__main__":
    # For testing purposes
    user_model = User_Model()
    
    # Example: Create a new user
    try:
        new_user = user_model.create({
            'email': 'test@example.com',
            'team': 'phoenixes',
            'access': 2
        })
        print(f"Created user: {new_user}")
    except ValueError as e:
        print(f"Error creating user: {e}")
    
    # Example: Get a user
    user = user_model.get('test@example.com')
    print(f"Retrieved user: {user}")