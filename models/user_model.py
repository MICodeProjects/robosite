import os
from typing import Dict, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from .database import Base, User, Team

class UserModel:
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
            DB_name: Name of the database file or SQLite URL
        """
        try:
            # Initialize database connection
            if DB_name.startswith('sqlite:///'):
                self.engine = create_engine(DB_name, echo=False)  # Set echo=False to suppress SQL output
            else:
                db_path = os.path.join(self.data_dir, DB_name)
                self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
            
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
            
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            raise
        
    def exists(self, email: str) -> Dict:
        """Check if a user with the given email exists in the database.
        
        Args:
            email: The email to check
            
        Returns:
            Dict with keys:
                status: "success" or "error"
                data: bool indicating if user exists, or error message
        """
        if not email:
            return {"status": "error", "data": "Email is required"}
            
        try:
            session = self.Session()
            try:
                exists = session.query(User).filter_by(email=email).first() is not None
                return {"status": "success", "data": exists}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}
        finally:
            session.close()
    
    def create(self, user_info: Dict) -> Dict:
        """Create a new user in the database.
        
        Args:
            user_info: Dictionary containing:
                email: User's email address
                team_id: ID of the team (optional)
                access: Access level (optional, defaults to 1)
                
        Returns:
            Dict with keys:
                status: "success" or "error"
                data: User data dict or error message
        """

        try:
            if 'email' not in user_info:
                return {"status": "error", "data": "Email is required"}
            
            # Check if user already exists
            exists_result = self.exists(user_info['email'])
            if exists_result["status"] == "error":
                return exists_result
            if exists_result["data"]:  # Check the data field, not status
                return {"status": "error", "data": f"User with email {user_info['email']} already exists"}
            
            # Validate access level
            access = user_info.get('access', 1)  # Default to 1 if not provided
            if access not in [1, 2, 3]:
                return {"status": "error", "data": "Access must be one of: 1 (Guest), 2 (Member), 3 (Captain/Teacher)"}
            
            # Validate team_id exists if provided
            session = self.Session()
            try:
                if 'team_id' in user_info:
                    team = session.query(Team).filter_by(id=user_info['team_id']).first()
                    if not team:
                        return {"status": "error", "data": f"Team with id {user_info['team_id']} does not exist"}
                
                new_user = User(
                    email=user_info['email'],
                    team_id=user_info.get('team_id'),
                    access=access
                )
                session.add(new_user)
                session.commit()
                
                return {"status": "success", "data": {
                    "email": new_user.email,
                    "team_id": new_user.team_id,
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
        """Get a user by email.
        
        Args:
            email: The email of the user to retrieve
            
        Returns:
            Dict with keys:
                status: "success" or "error"
                data: User data dict or error message
        """
        session = self.Session()
        try:
            user = session.query(User).filter_by(email=email).first()
            if user:
                return {"status": "success", "data": {
                    "email": user.email,
                    "team_id": user.team_id,
                    "access": user.access
                }}
            return {"status": "error", "data": f"User with email {email} not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}
        finally:
            session.close()
            
    def get_all(self) -> Dict:
        """Get all users from the database.
        
        Returns:
            Dict with keys:
                status: "success" or "error"
                data: List of user data dicts or error message
        """
        session = self.Session()
        try:
            # Use joinedload to eagerly load team relationship and avoid N+1 queries
            users = session.query(User).options(joinedload(User.team)).all()
            return {"status": "success", "data": [
                {
                    "email": user.email,
                    "team_id": user.team_id,
                    "access": user.access
                } for user in users
            ]}
        except Exception as e:
            return {"status": "error", "data": str(e)}
        finally:
            session.close()
    
    def update(self, user_info: Dict) -> Dict:
        """Update a user's information.
        
        Args:
            user_info: Dictionary containing:
                email: User's email address (required)
                team_id: New team ID (optional)
                access: New access level (optional)
                
        Returns:
            Dict with keys:
                status: "success" or "error"
                data: Updated user data dict or error message
        """
        try:
            # Validate required fields
            if 'email' not in user_info:
                return {"status": "error", "data": "Email is required"}
            
            # Get current user data
            current_user = self.get(user_info['email'])
            if current_user["status"] == "error":
                return current_user
            
            # Merge current data with new data
            update_data = {
                'email': user_info['email'],
                'team_id': user_info.get('team_id', current_user["data"]["team_id"]),
                'access': user_info.get('access', current_user["data"]["access"])
            }
            
            # Validate access level
            if update_data['access'] not in [1, 2, 3]:
                return {"status": "error", "data": "Access must be one of: 1 (Guest), 2 (Member), 3 (Captain/Teacher)"}
            
            session = self.Session()
            try:
                user = session.query(User).filter_by(email=user_info['email']).first()
                if not user:
                    return {"status": "error", "data": f"User with email {update_data['email']} not found"}
                
                # Update all fields with merged data
                user.team_id = update_data['team_id']
                user.access = update_data['access']
                
                session.commit()
                
                return {"status": "success", "data": {
                    "email": user.email,
                    "team_id": user.team_id,
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
        """Remove a user from the database by email.
        
        Args:
            email: The email of the user to remove
            
        Returns:
            Dict with keys:
                status: "success" or "error"
                data: Success message or error message
        """
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