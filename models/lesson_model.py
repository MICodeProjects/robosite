import os
from typing import Dict, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from .database import Base, Lesson, LessonComponent

class Lesson_Model:
    """
    Lesson Model - Handles all interactions with the lesson database using SQLAlchemy
    
    Attributes:
        - name: string
        - id: int
        - type: int
        - img: string
        - unit_id: int
        - components: List[LessonComponent]
    """
    
    def __init__(self):
        """Initialize the Lesson Model."""
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

    def exists(self, lesson: Optional[str] = None, id: Optional[int] = None) -> bool:
        """Check if a lesson exists by name or id"""
        if lesson is None and id is None:
            return False
            
        session = self.Session()
        try:
            query = session.query(Lesson)
            if lesson:
                query = query.filter(Lesson.name == lesson)
            if id:
                query = query.filter(Lesson.id == id)
            return session.query(query.exists()).scalar()
        finally:
            session.close()

    def create(self, lesson_info: Dict) -> Dict:
        """Create a new lesson"""
        try:
            if 'name' not in lesson_info:
                return {"status": "error", "data": "Lesson name is required"}
                
            if self.exists(lesson=lesson_info['name']):
                return {"status": "error", "data": f"Lesson {lesson_info['name']} already exists"}
                
            session = self.Session()
            try:
                new_lesson = Lesson(
                    name=lesson_info['name'],
                    type=lesson_info.get('type', 1),
                    img=lesson_info.get('img', ''),
                    unit_id=lesson_info.get('unit_id', 0)
                )
                
                session.add(new_lesson)
                session.commit()
                
                return {"status": "success", "data": {
                    'id': new_lesson.id,
                    'name': new_lesson.name,
                    'type': new_lesson.type,
                    'img': new_lesson.img,
                    'unit_id': new_lesson.unit_id
                }}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get(self, lesson: Optional[str] = None, id: Optional[int] = None) -> Dict:
        """Get a lesson by name or id"""
        try:
            if lesson is None and id is None:
                return {"status": "error", "data": "Either lesson name or id must be provided"}
                
            session = self.Session()
            try:
                query = session.query(Lesson).options(joinedload(Lesson.components))
                if lesson:
                    query = query.filter(Lesson.name == lesson)
                if id:
                    query = query.filter(Lesson.id == id)
                    
                result = query.first()
                if not result:
                    return {"status": "error", "data": "Lesson not found"}
                    
                return {"status": "success", "data": {
                    'id': result.id,
                    'name': result.name,
                    'type': result.type,
                    'img': result.img,
                    'unit_id': result.unit_id,
                    'components': [{
                        'id': comp.id,
                        'name': comp.name,
                        'type': comp.type,
                        'content': comp.content
                    } for comp in result.components]
                }}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get_all(self) -> Dict:
        """Get all lessons"""
        try:
            session = self.Session()
            try:
                lessons = session.query(Lesson).options(joinedload(Lesson.components)).order_by(Lesson.id).all()
                
                lesson_list = [{
                    'id': lesson.id,
                    'name': lesson.name,
                    'type': lesson.type,
                    'img': lesson.img,
                    'unit_id': lesson.unit_id,
                    'components': [{
                        'id': comp.id,
                        'name': comp.name,
                        'type': comp.type,
                        'content': comp.content
                    } for comp in lesson.components]
                } for lesson in lessons]
                
                return {"status": "success", "data": lesson_list}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}

    def get_by_unit_id(self, unit_id: int) -> Dict:
        """Get all lessons for a specific unit"""
        try:
            session = self.Session()
            try:
                lessons = session.query(Lesson).filter(Lesson.unit_id == unit_id).options(joinedload(Lesson.components)).order_by(Lesson.id).all()
                
                lesson_list = [{
                    'id': lesson.id,
                    'name': lesson.name,
                    'type': lesson.type,
                    'img': lesson.img,
                    'unit_id': lesson.unit_id,
                    'components': [{
                        'id': comp.id,
                        'name': comp.name,
                        'type': comp.type,
                        'content': comp.content
                    } for comp in lesson.components]
                } for lesson in lessons]
                
                return {"status": "success", "data": lesson_list}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}
            
    def update(self, lesson_info: Dict) -> Dict:
        """Update a lesson"""
        try:
            if 'id' not in lesson_info:
                return {"status": "error", "data": "Lesson ID is required"}
                
            if not self.exists(id=lesson_info['id']):
                return {"status": "error", "data": f"Lesson with id {lesson_info['id']} not found"}
                
            session = self.Session()
            try:
                lesson = session.query(Lesson).filter(Lesson.id == lesson_info['id']).first()
                
                # Update fields if provided
                if 'name' in lesson_info:
                    lesson.name = lesson_info['name']
                if 'type' in lesson_info:
                    lesson.type = lesson_info['type']
                if 'img' in lesson_info:
                    lesson.img = lesson_info['img']
                if 'unit_id' in lesson_info:
                    lesson.unit_id = lesson_info['unit_id']
                
                session.commit()
                
                return {"status": "success", "data": {
                    'id': lesson.id,
                    'name': lesson.name,
                    'type': lesson.type,
                    'img': lesson.img,
                    'unit_id': lesson.unit_id
                }}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}
            
    def remove(self, lesson: Optional[str] = None, id: Optional[int] = None) -> Dict:
        """Remove a lesson"""
        try:
            if lesson is None and id is None:
                return {"status": "error", "data": "Either lesson name or id must be provided"}
                
            session = self.Session()
            try:
                query = session.query(Lesson)
                if lesson:
                    query = query.filter(Lesson.name == lesson)
                if id:
                    query = query.filter(Lesson.id == id)
                    
                result = query.first()
                if not result:
                    return {"status": "error", "data": "Lesson not found"}
                    
                session.delete(result)
                session.commit()
                
                return {"status": "success", "data": "Lesson removed successfully"}
            finally:
                session.close()
        except Exception as e:
            return {"status": "error", "data": str(e)}