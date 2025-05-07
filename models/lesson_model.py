import json
import os

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
    def initialize_DB(DB_name):
        """
        Initializes the lesson database if it doesn't exist
        
        Args:
            DB_name (str): Name of the database file
            
        Returns:
            bool: True if database was created, False if it already existed
        """
        directory = os.path.dirname(DB_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        if not os.path.exists(DB_name):
            with open(DB_name, 'w') as file:
                json.dump([], file)
            return True
        return False
    
    @staticmethod
    def exists(lesson=None, id=None):
        """
        Checks if a lesson exists by either name or id
        
        Args:
            lesson (str, optional): Lesson name
            id (int, optional): Lesson ID
            
        Returns:
            bool: True if lesson exists, False otherwise
        """
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
    def create(lesson_info):
        """
        Creates a new lesson
        
        Args:
            lesson_info (dict): Lesson information with required fields
            
        Returns:
            dict: Created lesson data or None if lesson already exists
        """
        if 'name' not in lesson_info or Lesson_Model.exists(lesson=lesson_info['name']):
            return None
            
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
            
        return new_lesson
    
    @staticmethod
    def get(lesson=None, id=None):
        """
        Gets a lesson by name or id
        
        Args:
            lesson (str, optional): Lesson name
            id (int, optional): Lesson ID
            
        Returns:
            dict: Lesson data or None if lesson doesn't exist
        """
        if lesson is None and id is None:
            return None
            
        DB_PATH = 'data/lessons.json'
        Lesson_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            lessons = json.load(file)
            
        for l in lessons:
            if (lesson and l['name'] == lesson) or (id and l['id'] == id):
                return l
                
        return None
    
    @staticmethod
    def get_all():
        """
        Gets all lessons
        
        Returns:
            list: List of all lessons
        """
        DB_PATH = 'data/lessons.json'
        Lesson_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            lessons = json.load(file)
            
        return lessons
    
    @staticmethod
    def get_lesson_by_unit(unit_id):
        """
        Gets all lessons for a specific unit
        
        Args:
            unit_id (int): Unit ID
            
        Returns:
            list: List of lessons in the unit
        """
        DB_PATH = 'data/lessons.json'
        Lesson_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            lessons = json.load(file)
            
        unit_lessons = [lesson for lesson in lessons if lesson['unit_id'] == unit_id]
        return unit_lessons
    
    @staticmethod
    def update(lesson_info):
        """
        Updates a lesson
        
        Args:
            lesson_info (dict): Lesson info with at least 'id' field and fields to update
            
        Returns:
            dict: Updated lesson data or None if lesson doesn't exist
        """
        if 'id' not in lesson_info or not Lesson_Model.exists(id=lesson_info['id']):
            return None
            
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
            
        return updated_lesson
    
    @staticmethod
    def remove(lesson=None, id=None):
        """
        Removes a lesson
        
        Args:
            lesson (str, optional): Lesson name
            id (int, optional): Lesson ID
            
        Returns:
            dict: Removed lesson data or None if lesson doesn't exist
        """
        if lesson is None and id is None:
            return None
            
        DB_PATH = 'data/lessons.json'
        Lesson_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            lessons = json.load(file)
            
        removed_lesson = None
        for i, l in enumerate(lessons):
            if (lesson and l['name'] == lesson) or (id and l['id'] == id):
                removed_lesson = lessons.pop(i)
                break
                
        if removed_lesson:
            with open(DB_PATH, 'w') as file:
                json.dump(lessons, file, indent=2)
                
        return removed_lesson