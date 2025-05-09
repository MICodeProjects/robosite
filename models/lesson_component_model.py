import json
import os
from typing import Dict

class Lesson_Component_Model:
    """
    Lesson Component Model - Handles all interactions with the lesson component database
    
    Attributes:
        - name: string
        - id: int
        - lesson_id: int
        - type: int
        - content: string (json)
    """
    
    def __init__(self):
        """Initialize the Lesson Component Model with the database file path."""
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

    def exists(self, component=None, id=None) -> bool:
        """Checks if a component exists by either name or id"""
        if component is None and id is None:
            return False
            
        with open(self.db_path, 'r') as file:
            components = json.load(file)
            
        for c in components:
            if (component and c.get('name') == component) or (id and c.get('id') == id):
                return True
                
        return False
    
    def create(self, component_info: Dict) -> Dict:
        """Creates a new lesson component"""
        try:
            if 'name' not in component_info or 'lesson_id' not in component_info:
                return {"status": "error", "data": "Component name and lesson_id are required"}
                
            if self.exists(component=component_info['name']):
                return {"status": "error", "data": f"Component {component_info['name']} already exists"}
                
            with open(self.db_path, 'r') as file:
                components = json.load(file)
                
            # Generate a new ID
            new_id = 1
            if components:
                new_id = max(component['id'] for component in components) + 1
                
            new_component = {
                'name': component_info['name'],
                'id': new_id,
                'lesson_id': component_info['lesson_id'],
                'type': component_info.get('type', 1),
                'content': component_info.get('content', '{}')
            }
            
            components.append(new_component)
            
            with open(self.db_path, 'w') as file:
                json.dump(components, file, indent=2)
                
            return {"status": "success", "data": new_component}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def get(self, component=None, id=None) -> Dict:
        """Gets a component by name or id"""
        try:
            if component is None and id is None:
                return {"status": "error", "data": "Either component name or id must be provided"}
                
            with open(self.db_path, 'r') as file:
                components = json.load(file)
                
            for c in components:
                if (component and c['name'] == component) or (id and c['id'] == id):
                    return {"status": "success", "data": c}
                    
            return {"status": "error", "data": "Component not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def get_all(self) -> Dict:
        """Gets all components"""
        try:
            with open(self.db_path, 'r') as file:
                components = json.load(file)
                
            return {"status": "success", "data": components}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def get_by_lesson_id(self, lesson_id: int) -> Dict:
        """Gets all components for a specific lesson"""
        try:
            with open(self.db_path, 'r') as file:
                components = json.load(file)
                
            lesson_components = [component for component in components if component['lesson_id'] == lesson_id]
            return {"status": "success", "data": lesson_components}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def update(self, component_info: Dict) -> Dict:
        """Updates a component"""
        try:
            if 'id' not in component_info:
                return {"status": "error", "data": "Component ID is required"}
                
            if not self.exists(id=component_info['id']):
                return {"status": "error", "data": f"Component with id {component_info['id']} not found"}
                
            with open(self.db_path, 'r') as file:
                components = json.load(file)
                
            for component in components:
                if component['id'] == component_info['id']:
                    # Update fields if provided
                    if 'name' in component_info:
                        component['name'] = component_info['name']
                    if 'lesson_id' in component_info:
                        component['lesson_id'] = component_info['lesson_id']
                    if 'type' in component_info:
                        component['type'] = component_info['type']
                    if 'content' in component_info:
                        component['content'] = component_info['content']
                    updated_component = component
                    break
                    
            with open(self.db_path, 'w') as file:
                json.dump(components, file, indent=2)
                
            return {"status": "success", "data": updated_component}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def remove(self, component=None, id=None) -> Dict:
        """Removes a component"""
        try:
            if component is None and id is None:
                return {"status": "error", "data": "Either component name or id must be provided"}
                
            with open(self.db_path, 'r') as file:
                components = json.load(file)
                
            initial_length = len(components)
            components = [c for c in components if not ((component and c['name'] == component) or (id and c['id'] == id))]
            
            if len(components) == initial_length:
                return {"status": "error", "data": "Component not found"}
            
            with open(self.db_path, 'w') as file:
                json.dump(components, file, indent=2)
                
            return {"status": "success", "data": "Component removed successfully"}
        except Exception as e:
            return {"status": "error", "data": str(e)}