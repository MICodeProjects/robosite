import os
from typing import Dict, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from .database import Base, Unit, Lesson

class UnitModel:
    """
    Unit Model - Handles all interactions with the unit database using SQLAlchemy
    """
    
    def __init__(self):
        """Initialize the Unit Model."""
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

    def exists(self, unit: Optional[str] = None, id: Optional[int] = None) -> Dict:
        """Check if a unit exists by name or id"""
        if unit is None and id is None:
            return {"status": "error", "data": "No unit name or id input"}

        session = self.Session()
        try:
            query = session.query(Unit)
            if unit:
                unit_exists = query.filter_by(name=unit).first() is not None
                return {"status": "success", "data": unit_exists}

            else:
                unit_exists = query.filter_by(id=id).first() is not None            
                return {"status": "success", "data": unit_exists}
        finally:
            session.close()

    def create(self, unit_name: str) -> Dict:
        """Create a new unit"""
        try:
            exists_result = self.exists(unit=unit_name)
            if exists_result["status"] == "success" and exists_result["data"]==True:
                return {"status": "error", "data": f"Unit {unit_name} already exists"}

            session = self.Session()
            try:
                new_unit = Unit(name=unit_name)
                session.add(new_unit)
                session.commit()

                return {"status": "success", "data": {
                    'name': new_unit.name,
                    'id': new_unit.id
                }}
            except Exception as e:
                session.rollback()
                return {"status": "error", "data": str(e)}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get(self, unit: str = None, id: int = None) -> Dict:
        """Get a unit by name or id"""
        try:
            if unit is None and id is None:
                return {"status": "error", "data": "Either unit name or id must be provided"}

            session = self.Session()
            try:
                query = session.query(Unit).options(joinedload(Unit.lessons))
                if unit:
                    unit_obj = query.filter_by(name=unit).first()
                else:
                    unit_obj = query.filter_by(id=id).first()

                if not unit_obj:
                    return {"status": "error", "data": "Unit not found"}

                return {"status": "success", "data": {
                    'name': unit_obj.name,
                    'id': unit_obj.id
                }}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get_all(self) -> Dict:
        """Get all units"""
        try:
            session = self.Session()
            try:
                units = session.query(Unit).options(joinedload(Unit.lessons)).order_by(Unit.id).all()
                
                unit_list = [{
                    'name': unit.name,
                    'id': unit.id
                } for unit in units]
                
                return {"status": "success", "data": unit_list}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def update(self, unit_info: Dict) -> Dict:
        """Update a unit"""
        try:
            if 'id' not in unit_info:
                return {"status": "error", "data": "Unit ID is required"}

            session = self.Session()
            try:
                unit = session.query(Unit).filter_by(id=unit_info['id']).first()
                if not unit:
                    return {"status": "error", "data": f"Unit with id {unit_info['id']} not found"}

                # Update allowed fields
                if 'name' in unit_info:
                    unit.name = unit_info['name']

                session.commit()

                return {"status": "success", "data": {
                    'name': unit.name,
                    'id': unit.id
                }}
            except Exception as e:
                session.rollback()
                return {"status": "error", "data": str(e)}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def remove(self, unit: str = None, id: int = None) -> Dict:
        """Remove a unit"""
        try:
            if unit is None and id is None:
                return {"status": "error", "data": "Either unit name or id must be provided"}

            session = self.Session()
            try:
                query = session.query(Unit)
                if unit:
                    unit_obj = query.filter_by(name=unit).first()
                else:
                    unit_obj = query.filter_by(id=id).first()

                if not unit_obj:
                    return {"status": "error", "data": "Unit not found"}

                session.delete(unit_obj)
                session.commit()

                return {"status": "success", "data": "Unit removed successfully"}
            except Exception as e:
                session.rollback()
                return {"status": "error", "data": str(e)}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}