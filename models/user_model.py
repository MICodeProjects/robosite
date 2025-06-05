import os
from typing import Dict, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
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
            DB_name: Name of the database file or SQLite URL
        """
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize database connection
        if DB_name.startswith('sqlite:///'):
            self.engine = create_engine(DB_name)
        else:
            db_path = os.path.join(self.data_dir, DB_name)
            self.engine = create_engine(f'sqlite:///{db_path}')
            
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
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
            # Validate required fields
            if 'email' not in user_info:
                return {"status": "error", "data": "Email is required"}
            
            # Check if user already exists
            exists_result = self.exists(user_info['email'])
            if exists_result["status"] == "error":
                return exists_result
            if exists_result["status"]=="success":
                return {"status": "error", "data": f"User with email {user_info['email']} already exists"}
            
            # Validate access level
            access = user_info.access
            if access not in [1, 2, 3]:
                return {"status": "error", "data": "Access must be one of: 1 (Guest), 2 (Member), 3 (Captain/Teacher)"}
            
            session = self.Session()
            try:
                new_user = User(
                    email=user_info['email'],
                    team_id=user_info['team_id'],
                    access=user_info['access']
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
            

            
            # Validate access level if provided
            if 'access' in user_info and user_info['access'] not in [1, 2, 3]:
                return {"status": "error", "data": "Access must be one of: 1 (Guest), 2 (Member), 3 (Captain/Teacher)"}
            
            session = self.Session()
            try:
                user = session.query(User).filter_by(email=user_info['email']).first()
                if not user:
                    return {"status": "error", "data": f"User with email {user_info['email']} not found"}
                
                # Update fields if provided
                if 'team_id' in user_info:
                    user.team_id = user_info['team_id']
                if 'access' in user_info:
                    user.access = user_info['access']
                
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
