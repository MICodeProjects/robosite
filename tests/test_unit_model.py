import pytest
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import unit_model
from tests.sample_unit_data import SAMPLE_UNITS

@pytest.fixture
def unit():
    """Create a fresh Unit_Model instance for each test"""
    unit = unit_model.Unit_Model()
    unit.initialize_DB("data/units.json")
    return unit

@pytest.fixture
def setup_unit_data(unit):
    """Setup test data before each test"""
    if os.path.exists("data/units.json"):
        os.remove("data/units.json")
    
    with open("data/units.json", "w") as f:
        json.dump(SAMPLE_UNITS, f)

    yield
    
    if os.path.exists("data/units.json"):
        os.remove("data/units.json")

def test_unit_creation(unit, setup_unit_data):
    """Test creating a new unit"""
    result = unit.create("Machine Learning in Robotics")
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Machine Learning in Robotics"
    
    with open("data/units.json", "r") as f:
        units = json.load(f)
    
    assert any(u["name"] == "Machine Learning in Robotics" for u in units)

def test_unit_get_by_id(unit, setup_unit_data):
    """Test retrieving a unit by ID"""
    result = unit.get(id=1)
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Introduction to Robotics"
    assert result["data"]["id"] == 1

def test_unit_update(unit, setup_unit_data):
    """Test updating unit information"""
    result = unit.update({
        "id": 2,
        "name": "Python Programming for Robotics"
    })
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Python Programming for Robotics"

def test_unit_delete(unit, setup_unit_data):
    """Test deleting a unit"""
    result = unit.remove(id=5)
    
    assert result["status"] == "success"
    
    with open("data/units.json", "r") as f:
        units = json.load(f)
    
    assert not any(u["id"] == 5 for u in units)

def test_get_all_units(unit, setup_unit_data):
    """Test retrieving all units"""
    result = unit.get_all()
    
    assert result["status"] == "success"
    assert len(result["data"]) == len(SAMPLE_UNITS)

def test_invalid_unit_id(unit, setup_unit_data):
    """Test getting a nonexistent unit"""
    result = unit.get(id=999)
    
    assert result["status"] == "error"
    assert "not found" in result["data"]

def test_unit_duplicate_name(unit, setup_unit_data):
    """Test creating a unit with existing name"""
    result = unit.create("Introduction to Robotics")
    
    assert result["status"] == "error"
    assert "already exists" in result["data"]

def test_update_nonexistent_unit(unit, setup_unit_data):
    """Test updating a nonexistent unit"""
    result = unit.update({
        "id": 999,
        "name": "New Name"
    })
    
    assert result["status"] == "error"
    assert "not found" in result["data"]

def test_unit_order(unit, setup_unit_data):
    """Test units are returned in order by ID"""
    result = unit.get_all()
    
    assert result["status"] == "success"
    units = result["data"]
    for i in range(len(units)-1):
        assert units[i]["id"] < units[i+1]["id"]