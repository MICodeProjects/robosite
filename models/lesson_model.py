import json
import os
from typing import Dict

class Lesson_Model:
    """
    Lesson Model - Handles all interactions with the lesson database
    
    Attributes:
        - name: string
        - id: int
        - type: int
        - img: string
        - unit_id: int
    """
    
    def __init__(self):
        """Initialize the Lesson Model with the database file path."""
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.root_dir, 'data')
        self.db_path = None  # Will be set in initialize_DB

    def initialize_DB(self, DB_name: str) -> None:
        """
        Ensure that the JSON database file exists. If not, create it with an empty list.
    
        Args:
            DB_name: The name of the database file (can be relative or absolute path)
        """
        if os.path.isabs(DB_name):
            self.db_path = DB_name
        else:
            # If relative path is provided, make it relative to data directory
            self.db_path = os.path.join(self.root_dir, DB_name)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create the database file if it doesn't exist
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as file:
                json.dump([], file)

    def exists(self, lesson=None, id=None) -> bool:
        """Checks if a lesson exists by either name or id"""
        if lesson is None and id is None:
            return False
            
        with open(self.db_path, 'r') as file:
            lessons = json.load(file)
            
        for l in lessons:
            if (lesson and l.get('name') == lesson) or (id and l.get('id') == id):
                return True
                
        return False
    
    def create(self, lesson_info: Dict) -> Dict:
        """Creates a new lesson"""
        try:
            if 'name' not in lesson_info:
                return {"status": "error", "data": "Lesson name is required"}
                
            if self.exists(lesson=lesson_info['name']):
                return {"status": "error", "data": f"Lesson {lesson_info['name']} already exists"}
                
            with open(self.db_path, 'r') as file:
                lessons = json.load(file)
                
            # Generate a new ID
            new_id = 1
            if lessons:
                new_id = max(lesson['id'] for lesson in lessons) + 1
                
            new_lesson = {
                'name': lesson_info['name'],
                'id': new_id,
                'type': lesson_info.get('type', 1),
                'img': lesson_info.get('img', ''),
                'unit_id': lesson_info.get('unit_id', 0)
            }
            
            lessons.append(new_lesson)
            
            with open(self.db_path, 'w') as file:
                json.dump(lessons, file, indent=2)
                
            return {"status": "success", "data": new_lesson}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def get(self, lesson=None, id=None) -> Dict:
        """Gets a lesson by name or id"""
        try:
            if lesson is None and id is None:
                return {"status": "error", "data": "Either lesson name or id must be provided"}
                
            with open(self.db_path, 'r') as file:
                lessons = json.load(file)
                
            for l in lessons:
                if (lesson and l['name'] == lesson) or (id and l['id'] == id):
                    return {"status": "success", "data": l}
                    
            return {"status": "error", "data": "Lesson not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def get_all(self) -> Dict:
        """Gets all lessons"""
        try:
            with open(self.db_path, 'r') as file:
                lessons = json.load(file)
                
            return {"status": "success", "data": lessons}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def get_by_unit_id(self, unit_id: int) -> Dict:
        """Gets all lessons for a specific unit"""
        try:
            with open(self.db_path, 'r') as file:
                lessons = json.load(file)
                
            unit_lessons = [lesson for lesson in lessons if lesson['unit_id'] == unit_id]
            return {"status": "success", "data": unit_lessons}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def update(self, lesson_info: Dict) -> Dict:
        """Updates a lesson"""
        try:
            if 'id' not in lesson_info:
                return {"status": "error", "data": "Lesson ID is required"}
                
            if not self.exists(id=lesson_info['id']):
                return {"status": "error", "data": f"Lesson with id {lesson_info['id']} not found"}
                
            with open(self.db_path, 'r') as file:
                lessons = json.load(file)
                
            for lesson in lessons:
                if lesson['id'] == lesson_info['id']:
                    # Update fields if provided
                    if 'name' in lesson_info:
                        lesson['name'] = lesson_info['name']
                    if 'type' in lesson_info:
                        lesson['type'] = lesson_info['type']
                    if 'img' in lesson_info:
                        lesson['img'] = lesson_info['img']
                    if 'unit_id' in lesson_info:
                        lesson['unit_id'] = lesson_info['unit_id']
                    updated_lesson = lesson
                    break
                    
            with open(self.db_path, 'w') as file:
                json.dump(lessons, file, indent=2)
                
            return {"status": "success", "data": updated_lesson}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def remove(self, lesson=None, id=None) -> Dict:
        """Removes a lesson"""
        try:
            if lesson is None and id is None:
                return {"status": "error", "data": "Either lesson name or id must be provided"}
                
            with open(self.db_path, 'r') as file:
                lessons = json.load(file)
                
            initial_length = len(lessons)
            lessons = [l for l in lessons if not ((lesson and l['name'] == lesson) or (id and l['id'] == id))]
            
            if len(lessons) == initial_length:
                return {"status": "error", "data": "Lesson not found"}
            
            with open(self.db_path, 'w') as file:
                json.dump(lessons, file, indent=2)
                
            return {"status": "success", "data": "Lesson removed successfully"}
        except Exception as e:
            return {"status": "error", "data": str(e)}