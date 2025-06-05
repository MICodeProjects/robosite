import os
from typing import Dict, List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from .database import Base, Team, User

class Team_Model:
    """
    Team Model - Handles all interactions with the team database using SQLAlchemy
    """
    
    def __init__(self):
        """Initialize the Team Model."""
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
                self.engine = create_engine(DB_name, echo=True)  # Add echo=True for debugging
            else:
                db_dir = os.path.dirname(DB_name)
                db_name = os.path.splitext(os.path.basename(DB_name))[0] + '.db'
                db_path = os.path.join(db_dir, db_name)
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                self.engine = create_engine(f'sqlite:///{db_path}', echo=True)

            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)  # Add expire_on_commit=False
            
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            raise

    def exists(self, team: Optional[str] = None, id: Optional[int] = None) -> bool:
        """
        Check if a team exists by name or id
        """
        if team is None and id is None:
            return False

        session = self.Session()
        try:
            query = session.query(Team)
            if team:
                team_exists = query.filter_by(name=team).first() is not None
            else:
                team_exists = query.filter_by(id=id).first() is not None
            return team_exists
        finally:
            session.close()

    def create(self, team_name: str) -> Dict:
        """
        Create a new team
        """
        try:
            if self.exists(team=team_name):
                return {"status": "error", "data": f"Team {team_name} already exists"}

            session = self.Session()
            try:
                new_team = Team(name=team_name)
                session.add(new_team)
                session.commit()

                return {"status": "success", "data": {
                    'name': new_team.name,
                    'id': new_team.id,
                    'members': []
                }}
            except Exception as e:
                session.rollback()
                return {"status": "error", "data": str(e)}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}


    def get_team(self, team: str = None, id: int = None) -> Dict:
        """
        Get a team by name or id
        """
        try:
            if team is None and id is None:
                return {"status": "error", "data": "Either team name or id must be provided"}

            session = self.Session()
            try:
                query = session.query(Team).options(joinedload(Team.users))
                if team:
                    team_obj = query.filter_by(name=team).first()
                else:
                    team_obj = query.filter_by(id=id).first()

                if not team_obj:
                    return {"status": "error", "data": "Team not found"}

                return {"status": "success", "data": {
                    'name': team_obj.name,
                    'id': team_obj.id,
                    'members': [user.email for user in team_obj.users]
                }}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get_all_teams(self) -> Dict:
        """
        Get all teams
        """
        try:
            session = self.Session()
            try:
                teams = session.query(Team).options(joinedload(Team.users)).all()
                
                team_list = [{
                    'name': team.name,
                    'id': team.id,
                    'members': [user.email for user in team.users]
                } for team in teams]
                
                return {"status": "success", "data": team_list}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def update_team(self, id: int, new_data: Dict) -> Dict:
        """
        Update a team
        """
        try:
            session = self.Session()
            try:
                team = session.query(Team).options(joinedload(Team.users)).filter_by(id=id).first()
                if not team:
                    return {"status": "error", "data": f"Team with id {id} not found"}

                # Update only allowed fields
                if 'name' in new_data:
                    team.name = new_data['name']

                session.commit()

                return {"status": "success", "data": {
                    'name': team.name,
                    'id': team.id,
                    'members': [user.email for user in team.users]
                }}
            except Exception as e:
                session.rollback()
                return {"status": "error", "data": str(e)}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}