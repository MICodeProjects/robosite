import json
import os

class Unit_Model:
    """
    Unit Model - Handles all interactions with the unit database
    
    Attributes:
        - name: string
        - id: int
    """
    
    @staticmethod
    def initialize_DB(DB_name):
        """
        Initializes the unit database if it doesn't exist
        
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
    def exists(unit=None, id=None):
        """
        Checks if a unit exists by either name or id
        
        Args:
            unit (str, optional): Unit name
            id (int, optional): Unit ID
            
        Returns:
            bool: True if unit exists, False otherwise
        """
        if unit is None and id is None:
            return False
            
        DB_PATH = 'data/units.json'
        Unit_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            units = json.load(file)
            
        for u in units:
            if (unit and u.get('name') == unit) or (id and u.get('id') == id):
                return True
                
        return False
    
    @staticmethod
    def create(unit_name):
        """
        Creates a new unit
        
        Args:
            unit_name (str): Name of the unit to create
            
        Returns:
            dict: Created unit data or None if unit already exists
        """
        if Unit_Model.exists(unit=unit_name):
            return None
            
        DB_PATH = 'data/units.json'
        Unit_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            units = json.load(file)
            
        # Generate a new ID
        new_id = 1
        if units:
            new_id = max(unit['id'] for unit in units) + 1
            
        new_unit = {
            'name': unit_name,
            'id': new_id
        }
        
        units.append(new_unit)
        
        with open(DB_PATH, 'w') as file:
            json.dump(units, file, indent=2)
            
        return new_unit
    
    @staticmethod
    def get(unit=None, id=None):
        """
        Gets a unit by name or id
        
        Args:
            unit (str, optional): Unit name
            id (int, optional): Unit ID
            
        Returns:
            dict: Unit data or None if unit doesn't exist
        """
        if unit is None and id is None:
            return None
            
        DB_PATH = 'data/units.json'
        Unit_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            units = json.load(file)
            
        for u in units:
            if (unit and u['name'] == unit) or (id and u['id'] == id):
                return u
                
        return None
    
    @staticmethod
    def get_all():
        """
        Gets all units
        
        Returns:
            list: List of all units
        """
        DB_PATH = 'data/units.json'
        Unit_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            units = json.load(file)
            
        return units
    
    @staticmethod
    def update(unit_info):
        """
        Updates a unit
        
        Args:
            unit_info (dict): Unit info with at least 'id' field and fields to update
            
        Returns:
            dict: Updated unit data or None if unit doesn't exist
        """
        if 'id' not in unit_info or not Unit_Model.exists(id=unit_info['id']):
            return None
            
        DB_PATH = 'data/units.json'
        
        with open(DB_PATH, 'r') as file:
            units = json.load(file)
            
        for unit in units:
            if unit['id'] == unit_info['id']:
                # Update name if provided
                if 'name' in unit_info:
                    unit['name'] = unit_info['name']
                updated_unit = unit
                break
                
        with open(DB_PATH, 'w') as file:
            json.dump(units, file, indent=2)
            
        return updated_unit
    
    @staticmethod
    def remove(unit=None, id=None):
        """
        Removes a unit
        
        Args:
            unit (str, optional): Unit name
            id (int, optional): Unit ID
            
        Returns:
            dict: Removed unit data or None if unit doesn't exist
        """
        if unit is None and id is None:
            return None
            
        DB_PATH = 'data/units.json'
        Unit_Model.initialize_DB(DB_PATH)
        
        with open(DB_PATH, 'r') as file:
            units = json.load(file)
            
        removed_unit = None
        for i, u in enumerate(units):
            if (unit and u['name'] == unit) or (id and u['id'] == id):
                removed_unit = units.pop(i)
                break
                
        if removed_unit:
            with open(DB_PATH, 'w') as file:
                json.dump(units, file, indent=2)
                
        return removed_unit