import os
from typing import Dict, Optional, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from .database import Base, User, Team

class UserModel:
    """User Model for database operations"""
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

    def remove(self, google_id: str) -> Dict:
        """Delete user by google_id"""
        try:
            session = self.Session()
            user = session.query(User).filter_by(google_id=google_id).first()
            if not user:
                return {"status": "error", "data": "User not found"}
            
            session.delete(user)
            session.commit()
            return {"status": "success", "data": "User deleted successfully"}
        except Exception as e:
            session.rollback()
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
                google_id: User's Google ID (required)
                name: User's full name (optional)
                team_id: New team ID (optional)
                access: New access level (optional)
                
        Returns:
            Dict with keys:
                status: "success" or "error"
                data: Updated user data dict or error message
        """
        session = self.Session()
        try:
            # Verify required field
            if 'google_id' not in user_info:
                return {"status": "error", "data": "Google ID is required"}
            
            # Get existing user
            user = session.query(User).filter_by(google_id=user_info['google_id']).first()
            if not user:
                return {"status": "error", "data": "User not found"}
            
            # Update fields if provided
            if 'name' in user_info:
                user.name = user_info['name']
            if 'team_id' in user_info:
                user.team_id = user_info['team_id']
            if 'access' in user_info:
                user.access = user_info['access']
                
            session.commit()
            
            # Return updated user data
            return {"status": "success", "data": {
                "google_id": user.google_id,
                "name": user.name,
                "email":user.email,
                "access": user.access,
                "team_id": user.team_id
            }}
            
        except Exception as e:
            session.rollback()
            return {"status": "error", "data": str(e)}
        finally:
            session.close()

    
    def exists(self, email: str=None, google_id: str=None) -> Dict:
        """Check if a user exists by Google ID.
        
        Args:
            google_id: The Google ID to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        if google_id:
            session = self.Session()
            try:
                exists = session.query(User).filter_by(email=email).first() is not None
                return {"status":"success", "data":exists}
            except Exception as e:
                return {"status":"error", "data":str(e)}
            finally:
                session.close()
        elif email:
            
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
        else:
            return {"status": "error", "data": "Email or google id is required"}


    def create(self, user_info: Dict) -> Dict:
        """Create a new user in the database using Google OAuth information.
        
        Args:
            user_info: Dictionary containing:
                google_id: User's Google ID
                name: User's full name
                email: User's email address
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
            exists_by_id = self.exists(google_id=user_info['google_id'])
            exists_by_email = self.exists(email=user_info["email"])
            
            if ((exists_by_id["status"] == "success" and exists_by_id["data"]) or 
                (exists_by_email["status"] == "success" and exists_by_email["data"])):
                # User exists, update instead
                return self.update(user_info)
            
            # Default access level to 1 if not provided
            access = user_info.get('access', 1)
            
            # Create new user
            session = self.Session()
            try:
                new_user = User(
                    google_id=user_info['google_id'],
                    name=user_info['name'],
                    email=user_info['email'],
                    access=access,
                    team_id=user_info.get('team_id')
                )
                session.add(new_user)
                session.commit()
                
                return {"status": "success", "data": {
                    "google_id": new_user.google_id,
                    "name": new_user.name,
                    "email": new_user.email,
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
                        "google_id": user.google_id,
                        "name": user.name,
                        "email": user.email,
                        "access": user.access,
                        "team_id": user.team_id
                    }}
                return {"status": "error", "data": f"User not found"}
            except Exception as e:
                return {"status": "error", "data": str(e)}
            finally:
                session.close()
                