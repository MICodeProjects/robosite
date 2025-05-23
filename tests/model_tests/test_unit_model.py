import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, Unit
from models import unit_model
from tests.test_data.sample_unit_data import SAMPLE_UNITS

# Use SQLite in-memory database for testing
TEST_DB = f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data', 'test_database.db')}"

@pytest.fixture(scope="function")
def engine():
    """Create a fresh database engine for each test"""
    engine = create_engine(TEST_DB)
    Base.metadata.create_all(engine)  # Create all tables
    return engine

@pytest.fixture(scope="function")
def session(engine):
    """Create a new session for each test"""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture(scope="function")
def unit(engine):
    """Create a fresh Unit_Model instance for each test"""
    test_unit = unit_model.Unit_Model()
    test_unit.initialize_DB(TEST_DB)
    return test_unit

@pytest.fixture
def setup_unit_data(session):
    """Setup test data before each test"""
    try:
        # Clean up any existing data
        session.query(Unit).delete()
        session.commit()
        
        # Create sample units
        for unit_data in SAMPLE_UNITS:
            unit = Unit(
                name=unit_data["name"]
            )
            session.add(unit)
        session.commit()
        yield
    finally:
        # Clean up after each test
        session.query(Unit).delete()
        session.commit()

def test_unit_creation(unit, setup_unit_data):
    """Test creating a new unit"""
    result = unit.create("Machine Learning in Robotics")
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Machine Learning in Robotics"

def test_unit_get_by_id(unit, setup_unit_data):
    """Test retrieving a unit by ID"""
    # First create a unit to get
    new_unit = unit.create("Test Unit")
    unit_id = new_unit["data"]["id"]
    
    result = unit.get(id=unit_id)
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Test Unit"
    assert result["data"]["id"] == unit_id

def test_unit_get_all(unit, setup_unit_data):
    """Test retrieving all units"""
    result = unit.get_all()
    
    assert result["status"] == "success"
    assert len(result["data"]) == len(SAMPLE_UNITS)

def test_unit_update(unit, setup_unit_data):
    """Test updating unit information"""
    # First create a unit to update
    new_unit = unit.create("Test Unit")
    unit_id = new_unit["data"]["id"]
    
    result = unit.update({
        "id": unit_id,
        "name": "Updated Unit"
    })
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Updated Unit"

def test_unit_delete(unit, setup_unit_data):
    """Test deleting a unit"""
    # First create a unit to delete
    new_unit = unit.create("Test Unit")
    unit_id = new_unit["data"]["id"]
    
    result = unit.remove(id=unit_id)
    
    assert result["status"] == "success"
    
    # Verify unit was deleted
    get_result = unit.get(id=unit_id)
    assert get_result["status"] == "error"
    assert "not found" in get_result["data"]

def test_invalid_unit_id(unit, setup_unit_data):
    """Test getting a nonexistent unit"""
    result = unit.get(id=999)
    
    assert result["status"] == "error"
    assert "not found" in result["data"]

def test_duplicate_unit_name(unit, setup_unit_data):
    """Test creating a unit with duplicate name"""
    # First create a unit
    unit.create("Test Unit")
    
    # Try to create another unit with same name
    result = unit.create("Test Unit")
    
    assert result["status"] == "error"
    assert "exists" in result["data"].lower()