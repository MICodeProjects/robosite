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
    def exists(unit=None, id=None) -> bool:
        """Checks if a unit exists by either name or id"""
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
    def create(unit_name: str) -> Dict:
        """Creates a new unit"""
        try:
            if Unit_Model.exists(unit=unit_name):
                return {"status": "error", "data": f"Unit {unit_name} already exists"}
                
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
                
            return {"status": "success", "data": new_unit}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    @staticmethod
    def get(unit=None, id=None) -> Dict:
        """Gets a unit by name or id"""
        try:
            if unit is None and id is None:
                return {"status": "error", "data": "Either unit name or id must be provided"}
                
            DB_PATH = 'data/units.json'
            Unit_Model.initialize_DB(DB_PATH)
            
            with open(DB_PATH, 'r') as file:
                units = json.load(file)
                
            for u in units:
                if (unit and u['name'] == unit) or (id and u['id'] == id):
                    return {"status": "success", "data": u}
                    
            return {"status": "error", "data": "Unit not found"}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    @staticmethod
    def get_all() -> Dict:
        """Gets all units"""
        try:
            DB_PATH = 'data/units.json'
            Unit_Model.initialize_DB(DB_PATH)
            
            with open(DB_PATH, 'r') as file:
                units = json.load(file)
                
            return {"status": "success", "data": units}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    @staticmethod
    def update(unit_info: Dict) -> Dict:
        """Updates a unit"""
        try:
            if 'id' not in unit_info:
                return {"status": "error", "data": "Unit ID is required"}
                
            if not Unit_Model.exists(id=unit_info['id']):
                return {"status": "error", "data": f"Unit with id {unit_info['id']} not found"}
                
            DB_PATH = 'data/units.json'
            
            with open(DB_PATH, 'r') as file:
                units = json.load(file)
                
            for unit in units:
                if unit['id'] == unit_info['id']:
                    if 'name' in unit_info:
                        unit['name'] = unit_info['name']
                    updated_unit = unit
                    break
                    
            with open(DB_PATH, 'w') as file:
                json.dump(units, file, indent=2)
                
            return {"status": "success", "data": updated_unit}
        except Exception as e:
            return {"status": "error", "data": str(e)}
    
    @staticmethod
    def remove(unit=None, id=None) -> Dict:
        """Removes a unit"""
        try:
            if unit is None and id is None:
                return {"status": "error", "data": "Either unit name or id must be provided"}
                
            DB_PATH = 'data/units.json'
            Unit_Model.initialize_DB(DB_PATH)
            
            with open(DB_PATH, 'r') as file:
                units = json.load(file)
                
            initial_length = len(units)
            units = [u for u in units if not ((unit and u['name'] == unit) or (id and u['id'] == id))]
            
            if len(units) == initial_length:
                return {"status": "error", "data": "Unit not found"}
            
            with open(DB_PATH, 'w') as file:
                json.dump(units, file, indent=2)
                
            return {"status": "success", "data": "Unit removed successfully"}
        except Exception as e:
            return {"status": "error", "data": str(e)}