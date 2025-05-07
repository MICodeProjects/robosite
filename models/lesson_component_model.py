import json
import os

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
    
    @staticmethod
    def initialize_DB(DB_name):
        """
        Initializes the lesson component database if it doesn't exist
        
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
    def exists(component=None, id=None):
        """
        Checks if a lesson component exists by either name or id
        
        Args:
            component (str, optional): Component name
            id (int, optional): Component ID
            
        Returns:
            bool: True if component exists, False otherwise
        """
        if component is None and id is None:
            return False
            
        DB_PATH = 'data/lesson_components.json'
        Lesson_Component_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            components = json.load(file)
            
        for c in components:
            if (component and c.get('name') == component) or (id and c.get('id') == id):
                return True
                
        return False
    
    @staticmethod
    def create(component_info):
        """
        Creates a new lesson component
        
        Args:
            component_info (dict): Component information with required fields
            
        Returns:
            dict: Created component data or None if component already exists
        """
        if 'name' not in component_info or 'lesson_id' not in component_info:
            return None
            
        if Lesson_Component_Model.exists(component=component_info['name']):
            return None
            
        DB_PATH = 'data/lesson_components.json'
        Lesson_Component_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
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
        
        with open(DB_PATH, 'w') as file:
            json.dump(components, file, indent=2)
            
        return new_component
    
    @staticmethod
    def get(component=None, id=None):
        """
        Gets a lesson component by name or id
        
        Args:
            component (str, optional): Component name
            id (int, optional): Component ID
            
        Returns:
            dict: Component data or None if component doesn't exist
        """
        if component is None and id is None:
            return None
            
        DB_PATH = 'data/lesson_components.json'
        Lesson_Component_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            components = json.load(file)
            
        for c in components:
            if (component and c['name'] == component) or (id and c['id'] == id):
                return c
                
        return None
    
    @staticmethod
    def get_all():
        """
        Gets all lesson components
        
        Returns:
            list: List of all components
        """
        DB_PATH = 'data/lesson_components.json'
        Lesson_Component_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            components = json.load(file)
            
        return components
    
    @staticmethod
    def get_all_lesson_component_by_lesson(lesson_id):
        """
        Gets all components for a specific lesson
        
        Args:
            lesson_id (int): Lesson ID
            
        Returns:
            list: List of components in the lesson
        """
        DB_PATH = 'data/lesson_components.json'
        Lesson_Component_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            components = json.load(file)
            
        lesson_components = [component for component in components if component['lesson_id'] == lesson_id]
        return lesson_components
    
    @staticmethod
    def update(component_info):
        """
        Updates a lesson component
        
        Args:
            component_info (dict): Component info with at least 'id' field and fields to update
            
        Returns:
            dict: Updated component data or None if component doesn't exist
        """
        if 'id' not in component_info or not Lesson_Component_Model.exists(id=component_info['id']):
            return None
            
        DB_PATH = 'data/lesson_components.json'
        
        with open(DB_PATH, 'r') as file:
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
                
        with open(DB_PATH, 'w') as file:
            json.dump(components, file, indent=2)
            
        return updated_component
    
    @staticmethod
    def remove(component=None, id=None):
        """
        Removes a lesson component
        
        Args:
            component (str, optional): Component name
            id (int, optional): Component ID
            
        Returns:
            dict: Removed component data or None if component doesn't exist
        """
        if component is None and id is None:
            return None
            
        DB_PATH = 'data/lesson_components.json'
        Lesson_Component_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            components = json.load(file)
            
        removed_component = None
        for i, c in enumerate(components):
            if (component and c['name'] == component) or (id and c['id'] == id):
                removed_component = components.pop(i)
                break
                
        if removed_component:
            with open(DB_PATH, 'w') as file:
                json.dump(components, file, indent=2)
                
        return removed_component