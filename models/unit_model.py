import json
import os
from typing import Dict

class Unit_Model:
    """
    Unit Model - Handles all interactions with the unit database
    
    Attributes:
        - name: string
        - id: int
    """
    
    def __init__(self):
        """Initialize the Unit Model with the database file path."""
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

    def exists(self, unit=None, id=None) -> bool:
        """Checks if a unit exists by either name or id"""
        if unit is None and id is None:
            return False
            
        with open(self.db_path, 'r') as file:
            units = json.load(file)
            
        for u in units:
            if (unit and u.get('name') == unit) or (id and u.get('id') == id):
                return True
                
        return False
    
    def create(self, unit_name: str) -> Dict:
        """Creates a new unit"""
        try:
            if self.exists(unit=unit_name):
                return {"status": "error", "data": f"Unit {unit_name} already exists"}
                
            with open(self.db_path, 'r') as file:
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
            
            with open(self.db_path, 'w') as file:
                json.dump(units, file, indent=2)
                
            return {"status": "success", "data": new_unit}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def get(self, unit=None, id=None) -> Dict:
        """Gets a unit by name or id"""
        try:
            if unit is None and id is None:
                return {"status": "error", "data": "Either unit name or id must be provided"}
                
            with open(self.db_path, 'r') as file:
                units = json.load(file)
                
            for u in units:
                if (unit and u['name'] == unit) or (id and u['id'] == id):
                    return {"status": "success", "data": u}
                    
            return {"status": "error", "data": "Unit not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def get_all(self) -> Dict:
        """Gets all units"""
        try:
            with open(self.db_path, 'r') as file:
                units = json.load(file)
                
            return {"status": "success", "data": units}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def update(self, unit_info: Dict) -> Dict:
        """Updates a unit"""
        try:
            if 'id' not in unit_info:
                return {"status": "error", "data": "Unit ID is required"}
                
            if not self.exists(id=unit_info['id']):
                return {"status": "error", "data": f"Unit with id {unit_info['id']} not found"}
                
            with open(self.db_path, 'r') as file:
                units = json.load(file)
                
            for unit in units:
                if unit['id'] == unit_info['id']:
                    if 'name' in unit_info:
                        unit['name'] = unit_info['name']
                    updated_unit = unit
                    break
                    
            with open(self.db_path, 'w') as file:
                json.dump(units, file, indent=2)
                
            return {"status": "success", "data": updated_unit}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    def remove(self, unit=None, id=None) -> Dict:
        """Removes a unit"""
        try:
            if unit is None and id is None:
                return {"status": "error", "data": "Either unit name or id must be provided"}
                
            with open(self.db_path, 'r') as file:
                units = json.load(file)
                
            initial_length = len(units)
            units = [u for u in units if not ((unit and u['name'] == unit) or (id and u['id'] == id))]
            
            if len(units) == initial_length:
                return {"status": "error", "data": "Unit not found"}
            
            with open(self.db_path, 'w') as file:
                json.dump(units, file, indent=2)
                
            return {"status": "success", "data": "Unit removed successfully"}
        except Exception as e:
            return {"status": "error", "data": str(e)}