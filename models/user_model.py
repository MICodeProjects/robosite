import os
from typing import Dict, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import Base, User, Team


class User_Model:
    """
    User Model class for managing user data in the Robosite application.
    
    This class handles CRUD operations for User entities stored in SQLite database.
    Each User has email, team, and access level attributes.
    
    Access levels:
    - 1: Guest (cannot submit assignments or edit)
    - 2: Member (can submit assignments and are on a team, but cannot edit)
    - 3: Captain/Teacher (can edit assignments and assign assignments)
    """
    
    def __init__(self):
        """Initialize the User Model with the database file path."""
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.root_dir, 'data')
        self.engine = None
        self.Session = None

    def initialize_DB(self, DB_name: str) -> None:
        """Initialize SQLite database and ensure tables exist.
        
        Args:
            DB_name: Name of the database file
        """
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize database connection
        db_path = os.path.join(self.data_dir, DB_name)
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def exists(self, email: str) -> bool:
        """
        Check if a user with the given email exists in the database.
        
        Args:
            email: The email to check
            
        Returns:
            bool: True if the user exists, False otherwise
        """
        session = self.Session()
        try:
            return session.query(User).filter_by(email=email).first() is not None
        finally:
            session.close()
    
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
            
            session = self.Session()
            try:
                # Get or create team
                team = None
                if user_info['team'] != 'none':
                    team = session.query(Team).filter_by(name=user_info['team']).first()
                    if not team:
                        team = Team(name=user_info['team'])
                        session.add(team)
                        session.flush()  # Get the team ID
                
                # Create new user
                new_user = User(
                    email=user_info['email'],
                    team_id=team.id if team else None,
                    access=user_info['access']
                )
                session.add(new_user)
                session.commit()
                
                return {"status": "success", "data": {
                    "email": new_user.email,
                    "team": user_info['team'],
                    "access": new_user.access
                }}
            except Exception as e:
                session.rollback()
                return {"status": "error", "data": str(e)}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get(self, email: str) -> Dict:
        """Get a user by email."""
        session = self.Session()
        try:
            user = session.query(User).filter_by(email=email).first()
            if user:
                return {"status": "success", "data": {
                    "email": user.email,
                    "team": user.team.name if user.team else "none",
                    "access": user.access
                }}
            return {"status": "error", "data": f"User with email {email} not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}
        finally:
            session.close()

    def get_all(self) -> Dict:
        """Get all users from the database."""
        session = self.Session()
        try:
            users = session.query(User).all()
            return {"status": "success", "data": [
                {
                    "email": user.email,
                    "team": user.team.name if user.team else "none",
                    "access": user.access
                } for user in users
            ]}
        except Exception as e:
            return {"status": "error", "data": str(e)}
        finally:
            session.close()
    
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
            
            session = self.Session()
            try:
                user = session.query(User).filter_by(email=user_info['email']).first()
                if not user:
                    return {"status": "error", "data": f"User with email {user_info['email']} not found"}
                
                # Update fields
                if 'access' in user_info:
                    user.access = user_info['access']
                if 'team' in user_info:
                    if user_info['team'] == 'none':
                        user.team_id = None
                    else:
                        team = session.query(Team).filter_by(name=user_info['team']).first()
                        if not team:
                            team = Team(name=user_info['team'])
                            session.add(team)
                            session.flush()
                        user.team_id = team.id
                
                session.commit()
                
                return {"status": "success", "data": {
                    "email": user.email,
                    "team": user.team.name if user.team else "none",
                    "access": user.access
                }}
            except Exception as e:
                session.rollback()
                return {"status": "error", "data": str(e)}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def remove(self, email: str) -> Dict:
        """Remove a user by email."""
        session = self.Session()
        try:
            user = session.query(User).filter_by(email=email).first()
            if user:
                session.delete(user)
                session.commit()
                return {"status": "success", "data": "User removed successfully"}
            return {"status": "error", "data": f"User with email {email} not found"}
        except Exception as e:
            session.rollback()
            return {"status": "error", "data": str(e)}
        finally:
            session.close()

# Example usage
if __name__ == "__main__":
    user_model = User_Model()
    user_model.initialize_DB("robosite.db")
    
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