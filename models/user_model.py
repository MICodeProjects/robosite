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
    
    def exists(self, email: str=None, google_id: str=None) -> bool:
        """Check if a user exists by Google ID.
        
        Args:
            google_id: The Google ID to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        if google_id:
            session = self.Session()
            try:
                return session.query(User).filter_by(google_id=google_id).first() is not None
            except Exception as e:
                return False
            finally:
                session.close()
        elif email:
            if not email:
                return {"status": "error", "data": "Email or google id is required"}
            
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
        """Create a new user in the database using Google OAuth information.
        
        Args:
            user_info: Dictionary containing:
                google_id: User's Google ID
                name: User's full name
                email: User's email address
                profile_picture: URL of the user's profile picture (optional)
                access: Access level (optional, defaults to 1)
                team_id: ID of the team (optional)
                
        Returns:
            Dict with keys:
                status: "success" or "error"
                data: User data dict or error message
        """
        try:
            if 'google_id' not in user_info or 'email' not in user_info:
                return {"status": "error", "data": "Google ID and email are required"}
            
            # Check if user already exists
            if self.exists_by_google_id(user_info['google_id']):
                return {"status": "error", "data": "User with this Google ID already exists"}
            
            # Default access level to 1 if not provided
            access = user_info.get('access', 1)
            
            # Create new user
            session = self.Session()
            try:
                new_user = User(
                    google_id=user_info['google_id'],
                    name=user_info['name'],
                    email=user_info['email'],
                    profile_picture=user_info.get('profile_picture'),
                    access=access,
                    team_id=user_info.get('team_id')
                )
                session.add(new_user)
                session.commit()
                
                return {"status": "success", "data": {
                    "google_id": new_user.google_id,
                    "name": new_user.name,
                    "email": new_user.email,
                    "profile_picture": new_user.profile_picture,
                    "access": new_user.access,
                    "team_id": new_user.team_id
                }}
            except Exception as e:
                session.rollback()
                return {"status": "error", "data": str(e)}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def get(self, email: str=None, google_id: str=None) -> Dict:
        """Get a user by Google ID.
        
        Args:
            google_id: The Google ID of the user to retrieve
            
        Returns:
            Dict with keys:
                status: "success" or "error"
                data: User data dict or error message
        """
        if google_id!=None:
            session = self.Session()
            try:
                user = session.query(User).options(joinedload(User.team)).filter_by(google_id=google_id).first()
                if user:
                    return {"status": "success", "data": {
                        "google_id": user.google_id,
                        "name": user.name,
                        "email": user.email,
                        "profile_picture": user.profile_picture,
                        "access": user.access,
                        "team_id": user.team_id
                    }}
                return {"status": "error", "data": "User not found"}
            except Exception as e:
                return {"status": "error", "data": str(e)}
            finally:
                session.close()
        elif email !=None:
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
                