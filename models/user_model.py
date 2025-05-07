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
        
        # Ensure the database exists
        self.initialize_DB('users.json')
    
    def initialize_DB(self, DB_name: str) -> None:
        """
        Ensure that the JSON database file exists. If not, create it with an empty list.
        
        Args:
            DB_name: The name of the database file
        """
        # Create the data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Create the users database file if it doesn't exist
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as file:
                json.dump([], file)
                
        print(f"Database initialized: {self.db_path}")
    
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
        """
        Create a new user in the database.
        
        Args:
            user_info: Dictionary containing user information (email, team, access)
            
        Returns:
            Dict: The created user information
            
        Raises:
            ValueError: If the user already exists or required fields are missing
        """
        # Validate required fields
        if 'email' not in user_info:
            raise ValueError("Email is required")
        
        if 'team' not in user_info:
            user_info['team'] = 'none'  # Default team
        
        if 'access' not in user_info:
            user_info['access'] = 1  # Default access level (guest)
            
        # Check valid team options
        valid_teams = ["phoenixes", "pigeons", "none", "teacher"]
        if user_info['team'] not in valid_teams:
            raise ValueError(f"Team must be one of: {', '.join(valid_teams)}")
            
        # Check valid access levels
        valid_access = [1, 2, 3]
        if user_info['access'] not in valid_access:
            raise ValueError(f"Access must be one of: {', '.join(map(str, valid_access))}")
        
        # Check if user already exists
        if self.exists(user_info['email']):
            raise ValueError(f"User with email {user_info['email']} already exists")
        
        # Open the database
        with open(self.db_path, 'r') as file:
            users = json.load(file)
        
        # Add the new user
        users.append(user_info)
        
        # Save the database
        with open(self.db_path, 'w') as file:
            json.dump(users, file, indent=2)
        
        return user_info
    
    def get(self, email: str) -> Optional[Dict]:
        """
        Get a user by email.
        
        Args:
            email: The email of the user to retrieve
            
        Returns:
            Dict: The user information or None if not found
        """
        # Open the database
        with open(self.db_path, 'r') as file:
            users = json.load(file)
        
        # Find the user
        for user in users:
            if user.get('email') == email:
                return user
        
        return None
    
    def get_all(self) -> List[Dict]:
        """
        Get all users from the database.
        
        Returns:
            List[Dict]: List of all users
        """
        # Open the database
        with open(self.db_path, 'r') as file:
            users = json.load(file)
        
        return users
    
    def update(self, user_info: Dict) -> Optional[Dict]:
        """
        Update a user's information.
        
        Args:
            user_info: Dictionary containing updated user information
            
        Returns:
            Dict: The updated user information or None if not found
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        if 'email' not in user_info:
            raise ValueError("Email is required")
        
        # Check valid team options if provided
        if 'team' in user_info:
            valid_teams = ["phoenixes", "pigeons", "none", "teacher"]
            if user_info['team'] not in valid_teams:
                raise ValueError(f"Team must be one of: {', '.join(valid_teams)}")
        
        # Check valid access levels if provided
        if 'access' in user_info:
            valid_access = [1, 2, 3]
            if user_info['access'] not in valid_access:
                raise ValueError(f"Access must be one of: {', '.join(map(str, valid_access))}")
        
        # Open the database
        with open(self.db_path, 'r') as file:
            users = json.load(file)
        
        updated_user = None
        
        # Find and update the user
        for i, user in enumerate(users):
            if user.get('email') == user_info['email']:
                # Update existing fields
                for key, value in user_info.items():
                    users[i][key] = value
                
                updated_user = users[i]
                break
        
        # Save the database if a user was updated
        if updated_user:
            with open(self.db_path, 'w') as file:
                json.dump(users, file, indent=2)
        
        return updated_user
    
    def remove(self, email: str) -> bool:
        """
        Remove a user by email.
        
        Args:
            email: The email of the user to remove
            
        Returns:
            bool: True if user was removed, False if not found
        """
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
            return True
        
        return False


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