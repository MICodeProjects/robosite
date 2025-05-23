import os
from typing import Dict, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from .database import Base, LessonComponent

class lesson_component_Model:
    """
    LessonComponent Model - Handles all interactions with the lesson component database using SQLAlchemy
    
    Attributes:
        - name: string
        - id: int
        - lesson_id: int
        - type: int
        - content: string (json)
    """
    
    def __init__(self):
        """Initialize the LessonComponent Model."""
        self.engine = None
        self.Session = None

    def initialize_DB(self, DB_name: str) -> None:
        """Initialize SQLite database connection using SQLAlchemy"""
        if os.path.isabs(DB_name):
            db_path = DB_name
        else:
            # Convert JSON path to SQLite path
            db_dir = os.path.dirname(DB_name)
            db_name = os.path.splitext(os.path.basename(DB_name))[0] + '.db'
            db_path = os.path.join(db_dir, db_name)
            
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
        # Create database engine
        db_url = f'sqlite:///{db_path}'
        self.engine = create_engine(db_url)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.Session = sessionmaker(bind=self.engine)

    def exists(self, lesson_component: Optional[str] = None, id: Optional[int] = None) -> bool:
        """Check if a lesson component exists by name or id"""
        if lesson_component is None and id is None:
            return False
            
        session = self.Session()
        try:
            query = session.query(LessonComponent)
            if lesson_component:
                query = query.filter(LessonComponent.name == lesson_component)
            if id:
                query = query.filter(LessonComponent.id == id)
            return session.query(query.exists()).scalar()
        finally:
            session.close()

    def create(self, component_info: Dict) -> Dict:
        """Create a new lesson component"""
        try:
            if 'name' not in component_info or 'lesson_id' not in component_info:
                return {"status": "error", "data": "Component name and lesson_id are required"}
                
            if self.exists(lesson_component=component_info['name']):
                return {"status": "error", "data": f"Component {component_info['name']} already exists"}
                
            session = self.Session()
            try:
                new_component = LessonComponent(
                    name=component_info['name'],
                    lesson_id=component_info['lesson_id'],
                    type=component_info.get('type', 1),
                    content=component_info.get('content', '{}')
                )
                
                session.add(new_component)
                session.commit()
                
                return {"status": "success", "data": {
                    'id': new_component.id,
                    'name': new_component.name,
                    'lesson_id': new_component.lesson_id,
                    'type': new_component.type,
                    'content': new_component.content
                }}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get(self, lesson_component: Optional[str] = None, id: Optional[int] = None) -> Dict:
        """Get a lesson component by name or id"""
        try:
            if lesson_component is None and id is None:
                return {"status": "error", "data": "Either component name or id must be provided"}
                
            session = self.Session()
            try:
                query = session.query(LessonComponent)
                if lesson_component:
                    query = query.filter(LessonComponent.name == lesson_component)
                if id:
                    query = query.filter(LessonComponent.id == id)
                    
                result = query.first()
                if not result:
                    return {"status": "error", "data": "Component not found"}
                    
                return {"status": "success", "data": {
                    'id': result.id,
                    'name': result.name,
                    'lesson_id': result.lesson_id,
                    'type': result.type,
                    'content': result.content
                }}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get_all(self) -> Dict:
        """Get all lesson components"""
        try:
            session = self.Session()
            try:
                components = session.query(LessonComponent).order_by(LessonComponent.id).all()
                
                component_list = [{
                    'id': component.id,
                    'name': component.name,
                    'lesson_id': component.lesson_id,
                    'type': component.type,
                    'content': component.content
                } for component in components]
                
                return {"status": "success", "data": component_list}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get_by_lesson_id(self, lesson_id: int) -> Dict:
        """Get all components for a specific lesson"""
        try:
            session = self.Session()
            try:
                components = session.query(LessonComponent).filter(
                    LessonComponent.lesson_id == lesson_id
                ).order_by(LessonComponent.id).all()
                
                component_list = [{
                    'id': component.id,
                    'name': component.name,
                    'lesson_id': component.lesson_id,
                    'type': component.type,
                    'content': component.content
                } for component in components]
                
                return {"status": "success", "data": component_list}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}
            
    def update(self, component_info: Dict) -> Dict:
        """Update a lesson component"""
        try:
            if 'id' not in component_info:
                return {"status": "error", "data": "Component ID is required"}
                
            if not self.exists(id=component_info['id']):
                return {"status": "error", "data": f"Component with id {component_info['id']} not found"}
                
            session = self.Session()
            try:
                component = session.query(LessonComponent).filter(
                    LessonComponent.id == component_info['id']
                ).first()
                
                # Update fields if provided
                if 'name' in component_info:
                    component.name = component_info['name']
                if 'lesson_id' in component_info:
                    component.lesson_id = component_info['lesson_id']
                if 'type' in component_info:
                    component.type = component_info['type']
                if 'content' in component_info:
                    component.content = component_info['content']
                
                session.commit()
                
                return {"status": "success", "data": {
                    'id': component.id,
                    'name': component.name,
                    'lesson_id': component.lesson_id,
                    'type': component.type,
                    'content': component.content
                }}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}
            
    def remove(self, lesson_component: Optional[str] = None, id: Optional[int] = None) -> Dict:
        """Remove a lesson component"""
        try:
            if lesson_component is None and id is None:
                return {"status": "error", "data": "Either component name or id must be provided"}
                
            session = self.Session()
            try:
                query = session.query(LessonComponent)
                if lesson_component:
                    query = query.filter(LessonComponent.name == lesson_component)
                if id:
                    query = query.filter(LessonComponent.id == id)
                    
                result = query.first()
                if not result:
                    return {"status": "error", "data": "Component not found"}
                    
                session.delete(result)
                session.commit()
                
                return {"status": "success", "data": "Component removed successfully"}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}