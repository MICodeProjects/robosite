import pytest
import os
import json
import sys
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, Lesson, LessonComponent
from models import lesson_component_model
from tests.test_data.sample_lesson_component_data import SAMPLE_lesson_componentS

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
def lesson_component(engine):
    """Create a fresh lesson_component_Model instance for each test"""
    test_component = lesson_component_model.lesson_component_Model()
    test_component.initialize_DB(TEST_DB)
    return test_component

@pytest.fixture
def setup_lesson_component_data(session):
    """Setup test data before each test"""
    try:
        # Clean up any existing data
        session.query(LessonComponent).delete()
        session.commit()
        
        # Create sample lesson components
        for component_data in SAMPLE_lesson_componentS:
            component = LessonComponent(
                name=component_data["name"],
                lesson_id=component_data["lesson_id"],
                type=component_data["type"],
                content=component_data["content"]
            )
            session.add(component)
        session.commit()
        yield
    finally:
        # Clean up after each test
        session.query(LessonComponent).delete()
        session.commit()

def test_lesson_component_creation(lesson_component, setup_lesson_component_data):
    """Test creating a new lesson component"""
    content = {"text": "New lesson_component content"}
    result = lesson_component.create({
        "name": "New lesson_component",
        "lesson_id": 1,
        "type": 1,
        "content": json.dumps(content)
    })
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "New lesson_component"
    assert result["data"]["lesson_id"] == 1
    assert result["data"]["type"] == 1
    assert json.loads(result["data"]["content"])["text"] == "New lesson_component content"

def test_lesson_component_get_by_id(lesson_component, setup_lesson_component_data):
    """Test retrieving a lesson_component by ID"""
    # First create a component to get
    content = {"text": "Test content"}
    new_component = lesson_component.create({
        "name": "Test Component",
        "lesson_id": 1,
        "type": 1,
        "content": json.dumps(content)
    })
    component_id = new_component["data"]["id"]
    
    result = lesson_component.get(id=component_id)
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Test Component"
    assert result["data"]["lesson_id"] == 1
    assert json.loads(result["data"]["content"])["text"] == "Test content"

def test_lesson_component_get_all(lesson_component, setup_lesson_component_data):
    """Test retrieving all lesson_components"""
    result = lesson_component.get_all()
    
    assert result["status"] == "success"
    assert len(result["data"]) == len(SAMPLE_lesson_componentS)

def test_get_lesson_components_by_lesson(lesson_component, setup_lesson_component_data):
    """Test getting all lesson_components for a specific lesson"""
    result = lesson_component.get_by_lesson_id(1)
    
    assert result["status"] == "success"
    assert all(component["lesson_id"] == 1 for component in result["data"])

def test_lesson_component_update(lesson_component, setup_lesson_component_data):
    """Test updating lesson_component information"""
    # First create a component to update
    content = {"text": "Original content"}
    new_component = lesson_component.create({
        "name": "Test Component",
        "lesson_id": 1,
        "type": 1,
        "content": json.dumps(content)
    })
    component_id = new_component["data"]["id"]
    
    updated_content = {"text": "Updated content"}
    result = lesson_component.update({
        "id": component_id,
        "name": "Updated Component",
        "content": json.dumps(updated_content)
    })
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Updated Component"
    assert json.loads(result["data"]["content"])["text"] == "Updated content"

def test_lesson_component_delete(lesson_component, setup_lesson_component_data):
    """Test deleting a lesson_component"""
    # First create a component to delete
    content = {"text": "Test content"}
    new_component = lesson_component.create({
        "name": "Test Component",
        "lesson_id": 1,
        "type": 1,
        "content": json.dumps(content)
    })
    component_id = new_component["data"]["id"]
    
    result = lesson_component.remove(id=component_id)
    
    assert result["status"] == "success"
    
    # Verify component was deleted
    get_result = lesson_component.get(id=component_id)
    assert get_result["status"] == "error"
    assert "not found" in get_result["data"]

def test_invalid_lesson_component_id(lesson_component, setup_lesson_component_data):
    """Test getting a nonexistent lesson_component"""
    result = lesson_component.get(id=999)
    
    assert result["status"] == "error"
    assert "not found" in result["data"]

def test_missing_required_fields(lesson_component, setup_lesson_component_data):
    """Test creating a lesson_component without required fields"""
    result = lesson_component.create({
        # Missing lesson_id
        "name": "Test Component"
    })
    
    assert result["status"] == "error"
    assert "required" in result["data"].lower()

def test_lesson_component_content_validation(lesson_component, setup_lesson_component_data):
    """Test that lesson_component content is valid JSON"""
    content = {"text": "Test content"}
    new_component = lesson_component.create({
        "name": "Test Component",
        "lesson_id": 1,
        "type": 1,
        "content": json.dumps(content)
    })
    
    result = lesson_component.get(id=new_component["data"]["id"])
    
    assert result["status"] == "success"
    loaded_content = json.loads(result["data"]["content"])
    assert isinstance(loaded_content, dict)
    assert loaded_content["text"] == "Test content"