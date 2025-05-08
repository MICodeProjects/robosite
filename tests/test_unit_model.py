import pytest
import os
import json
from models.unit_model import Unit
from .sample_unit_data import SAMPLE_UNITS

@pytest.fixture
def setup_unit_data():
    """Setup test data before each test"""
    if os.path.exists("data/units.json"):
        os.remove("data/units.json")
    
    with open("data/units.json", "w") as f:
        json.dump(SAMPLE_UNITS, f)

    yield
    
    if os.path.exists("data/units.json"):
        os.remove("data/units.json")

def test_unit_creation(setup_unit_data):
    """Test creating a new unit"""
    unit = Unit("Machine Learning in Robotics", 6)
    unit.save()
    
    with open("data/units.json", "r") as f:
        units = json.load(f)
    
    assert any(u["name"] == "Machine Learning in Robotics" for u in units)

def test_unit_get_by_id(setup_unit_data):
    """Test retrieving a unit by ID"""
    unit = Unit.get_by_id(1)
    assert unit.name == "Introduction to Robotics"
    assert unit.id == 1

def test_unit_update(setup_unit_data):
    """Test updating unit information"""
    unit = Unit.get_by_id(2)
    unit.name = "Python Programming for Robotics"
    unit.save()
    
    updated_unit = Unit.get_by_id(2)
    assert updated_unit.name == "Python Programming for Robotics"

def test_unit_delete(setup_unit_data):
    """Test deleting a unit"""
    unit = Unit.get_by_id(5)
    unit.delete()
    
    with open("data/units.json", "r") as f:
        units = json.load(f)
    
    assert not any(u["id"] == 5 for u in units)

def test_get_all_units(setup_unit_data):
    """Test retrieving all units"""
    units = Unit.get_all()
    assert len(units) == len(SAMPLE_UNITS)

def test_invalid_unit_id(setup_unit_data):
    """Test getting a nonexistent unit"""
    with pytest.raises(Exception):
        Unit.get_by_id(999)

def test_unit_order(setup_unit_data):
    """Test units are returned in order by ID"""
    units = Unit.get_all()
    for i in range(len(units)-1):
        assert units[i].id < units[i+1].id