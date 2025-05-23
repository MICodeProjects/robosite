import pytest
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import lesson_component_model
from tests.sample_lesson_component_data import SAMPLE_LESSON_COMPONENTS

@pytest.fixture
def component():
    """Create a fresh Lesson_Component_Model instance for each test"""
    component = lesson_component_model.Lesson_Component_Model()
    component.initialize_DB("data/lesson_components.json")
    return component

@pytest.fixture
def setup_lesson_component_data(component):
    """Setup test data before each test"""
    if os.path.exists("data/lesson_components.json"):
        os.remove("data/lesson_components.json")
    
    with open("data/lesson_components.json", "w") as f:
        json.dump(SAMPLE_LESSON_COMPONENTS, f)

    yield
    
    if os.path.exists("data/lesson_components.json"):
        os.remove("data/lesson_components.json")

def test_component_creation(component, setup_lesson_component_data):
    """Test creating a new lesson component"""
    content = {"text": "New component content"}
    result = component.create({
        "name": "New Component",
        "lesson_id": 1,
        "type": 1,
        "content": json.dumps(content)
    })
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "New Component"
    
    with open("data/lesson_components.json", "r") as f:
        components = json.load(f)
    
    assert any(c["name"] == "New Component" for c in components)

def test_component_get_by_id(component, setup_lesson_component_data):
    """Test retrieving a component by ID"""
    result = component.get(id=1)
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Introduction Text"
    assert result["data"]["lesson_id"] == 1
    assert result["data"]["type"] == 1

def test_component_update(component, setup_lesson_component_data):
    """Test updating component information"""
    new_content = {"url": "https://example.com/updated_video"}
    result = component.update({
        "id": 2,
        "content": json.dumps(new_content)
    })
    
    assert result["status"] == "success"
    content = json.loads(result["data"]["content"])
    assert content["url"] == "https://example.com/updated_video"

def test_component_delete(component, setup_lesson_component_data):
    """Test deleting a component"""
    result = component.remove(id=5)
    
    assert result["status"] == "success"
    
    with open("data/lesson_components.json", "r") as f:
        components = json.load(f)
    
    assert not any(c["id"] == 5 for c in components)

def test_get_all_components(component, setup_lesson_component_data):
    """Test retrieving all components"""
    result = component.get_all()
    
    assert result["status"] == "success"
    assert len(result["data"]) == len(SAMPLE_LESSON_COMPONENTS)

def test_get_components_by_lesson(component, setup_lesson_component_data):
    """Test getting all components for a specific lesson"""
    result = component.get_by_lesson_id(1)
    
    assert result["status"] == "success"
    assert all(component["lesson_id"] == 1 for component in result["data"])

def test_invalid_component_id(component, setup_lesson_component_data):
    """Test getting a nonexistent component"""
    result = component.get(id=999)
    
    assert result["status"] == "error"
    assert "not found" in result["data"]

def test_missing_required_fields(component, setup_lesson_component_data):
    """Test creating a component without required fields"""
    result = component.create({
        "name": "Test Component"
        # Missing lesson_id
    })
    
    assert result["status"] == "error"
    assert "required" in result["data"].lower()

def test_component_content_validation(component, setup_lesson_component_data):
    """Test that component content is valid JSON"""
    result = component.get(id=1)
    
    assert result["status"] == "success"
    content = json.loads(result["data"]["content"])
    assert isinstance(content, dict)
    assert "text" in content