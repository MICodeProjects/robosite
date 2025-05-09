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
    
    @staticmethod
    def initialize_DB(self, DB_name: str) -> None:
        """
        Ensure that the JSON database file exists. If not, create it with an empty list.
        """
        # Create the data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
        # Use the provided DB_name to construct the path
        self.db_path = os.path.join(self.data_dir, DB_name)
    
        # Create the database file if it doesn't exist
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as file:
                json.dump([], file)

    @staticmethod
    def exists(lesson=None, id=None) -> bool:
        """Checks if a lesson exists by either name or id"""
        if lesson is None and id is None:
            return False
            
        DB_PATH = 'data/lessons.json'
        Lesson_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            lessons = json.load(file)
            
        for l in lessons:
            if (lesson and l.get('name') == lesson) or (id and l.get('id') == id):
                return True
                
        return False
    
    @staticmethod
    def create(lesson_info: Dict) -> Dict:
        """Creates a new lesson"""
        try:
            if 'name' not in lesson_info:
                return {"status": "error", "data": "Lesson name is required"}
                
            if Lesson_Model.exists(lesson=lesson_info['name']):
                return {"status": "error", "data": f"Lesson {lesson_info['name']} already exists"}
                
            DB_PATH = 'data/lessons.json'
            Lesson_Model.initialize_DB(DB_PATH)
            
            with open(DB_PATH, 'r') as file:
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
            
            with open(DB_PATH, 'w') as file:
                json.dump(lessons, file, indent=2)
                
            return {"status": "success", "data": new_lesson}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    @staticmethod
    def get(lesson=None, id=None) -> Dict:
        """Gets a lesson by name or id"""
        try:
            if lesson is None and id is None:
                return {"status": "error", "data": "Either lesson name or id must be provided"}
                
            DB_PATH = 'data/lessons.json'
            Lesson_Model.initialize_DB(DB_PATH)
            
            with open(DB_PATH, 'r') as file:
                lessons = json.load(file)
                
            for l in lessons:
                if (lesson and l['name'] == lesson) or (id and l['id'] == id):
                    return {"status": "success", "data": l}
                    
            return {"status": "error", "data": "Lesson not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    @staticmethod
    def get_all() -> Dict:
        """Gets all lessons"""
        try:
            DB_PATH = 'data/lessons.json'
            Lesson_Model.initialize_DB(DB_PATH)
            
            with open(DB_PATH, 'r') as file:
                lessons = json.load(file)
                
            return {"status": "success", "data": lessons}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    @staticmethod
    def get_by_unit_id(unit_id: int) -> Dict:
        """Gets all lessons for a specific unit"""
        try:
            DB_PATH = 'data/lessons.json'
            Lesson_Model.initialize_DB(DB_PATH)
            
            with open(DB_PATH, 'r') as file:
                lessons = json.load(file)
                
            unit_lessons = [lesson for lesson in lessons if lesson['unit_id'] == unit_id]
            return {"status": "success", "data": unit_lessons}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    @staticmethod
    def update(lesson_info: Dict) -> Dict:
        """Updates a lesson"""
        try:
            if 'id' not in lesson_info:
                return {"status": "error", "data": "Lesson ID is required"}
                
            if not Lesson_Model.exists(id=lesson_info['id']):
                return {"status": "error", "data": f"Lesson with id {lesson_info['id']} not found"}
                
            DB_PATH = 'data/lessons.json'
            
            with open(DB_PATH, 'r') as file:
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
                    
            with open(DB_PATH, 'w') as file:
                json.dump(lessons, file, indent=2)
                
            return {"status": "success", "data": updated_lesson}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    @staticmethod
    def remove(lesson=None, id=None) -> Dict:
        """Removes a lesson"""
        try:
            if lesson is None and id is None:
                return {"status": "error", "data": "Either lesson name or id must be provided"}
                
            DB_PATH = 'data/lessons.json'
            Lesson_Model.initialize_DB(DB_PATH)
            
            with open(DB_PATH, 'r') as file:
                lessons = json.load(file)
                
            initial_length = len(lessons)
            lessons = [l for l in lessons if not ((lesson and l['name'] == lesson) or (id and l['id'] == id))]
            
            if len(lessons) == initial_length:
                return {"status": "error", "data": "Lesson not found"}
            
            with open(DB_PATH, 'w') as file:
                json.dump(lessons, file, indent=2)
                
            return {"status": "success", "data": "Lesson removed successfully"}
        except Exception as e:
            return {"status": "error", "data": str(e)}