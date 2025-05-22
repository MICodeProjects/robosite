import json
import os
from typing import Dict

class lesson_component_Model:
    """
    lesson_component Model - Handles all interactions with the lesson_component database
    
    Attributes:
        - name: string
        - id: int
        - lesson_id: int
        - type: int
        - content: string (json)
    """
    
    def __init__(self):
        """Initialize the lesson_component Model with the database file path."""
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

    def exists(self, lesson_component=None, id=None) -> bool:
        """Checks if a lesson_component exists by either name or id"""
        if lesson_component is None and id is None:
            return False
            
        with open(self.db_path, 'r') as file:
            lesson_components = json.load(file)
            
        for c in lesson_components:
            if (lesson_component and c.get('name') == lesson_component) or (id and c.get('id') == id):
                return True
                
        return False
    
    def create(self, lesson_component_info: Dict) -> Dict:
        """Creates a new lesson_component"""
        try:
            if 'name' not in lesson_component_info or 'lesson_id' not in lesson_component_info:
                return {"status": "error", "data": "lesson_component name and lesson_id are required"}
                
            if self.exists(lesson_component=lesson_component_info['name']):
                return {"status": "error", "data": f"lesson_component {lesson_component_info['name']} already exists"}
                
            with open(self.db_path, 'r') as file:
                lesson_components = json.load(file)
                
            # Generate a new ID
            new_id = 1
            if lesson_components:
                new_id = max(lesson_component['id'] for lesson_component in lesson_components) + 1
                
            new_lesson_component = {
                'name': lesson_component_info['name'],
                'id': new_id,
                'lesson_id': lesson_component_info['lesson_id'],
                'type': lesson_component_info.get('type', 1),
                'content': lesson_component_info.get('content', '{}')
            }
            
            lesson_components.append(new_lesson_component)
            
            with open(self.db_path, 'w') as file:
                json.dump(lesson_components, file, indent=2)
                
            return {"status": "success", "data": new_lesson_component}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def get(self, lesson_component=None, id=None) -> Dict:
        """Gets a lesson_component by name or id"""
        try:
            if lesson_component is None and id is None:
                return {"status": "error", "data": "Either lesson_component name or id must be provided"}
                
            with open(self.db_path, 'r') as file:
                lesson_components = json.load(file)
                
            for c in lesson_components:
                if (lesson_component and c['name'] == lesson_component) or (id and c['id'] == id):
                    return {"status": "success", "data": c}
                    
            return {"status": "error", "data": "lesson_component not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def get_all(self) -> Dict:
        """Gets all lesson_components"""
        try:
            with open(self.db_path, 'r') as file:
                lesson_components = json.load(file)
                
            return {"status": "success", "data": lesson_components}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def get_by_lesson_id(self, lesson_id: int) -> Dict:
        """Gets all lesson_components for a specific lesson"""
        try:
            with open(self.db_path, 'r') as file:
                lesson_components = json.load(file)
                
            lesson_components = [lesson_component for lesson_component in lesson_components if lesson_component['lesson_id'] == lesson_id]
            return {"status": "success", "data": lesson_components}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def update(self, lesson_component_info: Dict) -> Dict:
        """Updates a lesson_component"""
        try:
            if 'id' not in lesson_component_info:
                return {"status": "error", "data": "lesson_component ID is required"}
                
            if not self.exists(id=lesson_component_info['id']):
                return {"status": "error", "data": f"lesson_component with id {lesson_component_info['id']} not found"}
                
            with open(self.db_path, 'r') as file:
                lesson_components = json.load(file)
                
            for lesson_component in lesson_components:
                if lesson_component['id'] == lesson_component_info['id']:
                    # Update fields if provided
                    if 'name' in lesson_component_info:
                        lesson_component['name'] = lesson_component_info['name']
                    if 'lesson_id' in lesson_component_info:
                        lesson_component['lesson_id'] = lesson_component_info['lesson_id']
                    if 'type' in lesson_component_info:
                        lesson_component['type'] = lesson_component_info['type']
                    if 'content' in lesson_component_info:
                        lesson_component['content'] = lesson_component_info['content']
                    updated_lesson_component = lesson_component
                    break
                    
            with open(self.db_path, 'w') as file:
                json.dump(lesson_components, file, indent=2)
                
            return {"status": "success", "data": updated_lesson_component}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def remove(self, lesson_component=None, id=None) -> Dict:
        """Removes a lesson_component"""
        try:
            if lesson_component is None and id is None:
                return {"status": "error", "data": "Either lesson_component name or id must be provided"}
                
            with open(self.db_path, 'r') as file:
                lesson_components = json.load(file)
                
            initial_length = len(lesson_components)
            lesson_components = [c for c in lesson_components if not ((lesson_component and c['name'] == lesson_component) or (id and c['id'] == id))]
            
            if len(lesson_components) == initial_length:
                return {"status": "error", "data": "lesson_component not found"}
            
            with open(self.db_path, 'w') as file:
                json.dump(lesson_components, file, indent=2)
                
            return {"status": "success", "data": "lesson_component removed successfully"}
        except Exception as e:
            return {"status": "error", "data": str(e)}