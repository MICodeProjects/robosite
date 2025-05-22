import pytest
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import lesson_component_model
from tests.sample_lesson_component_data import SAMPLE_lesson_componentS

@pytest.fixture
def lesson_component():
    """Create a fresh lesson_component_Model instance for each test"""
    lesson_component = lesson_component_model.lesson_component_Model()
    lesson_component.initialize_DB("data/lesson_components.json")
    return lesson_component

@pytest.fixture
def setup_lesson_component_data(lesson_component):
    """Setup test data before each test"""
    if os.path.exists("data/lesson_components.json"):
        os.remove("data/lesson_components.json")
    
    with open("data/lesson_components.json", "w") as f:
        json.dump(SAMPLE_lesson_componentS, f)

    yield
    
    if os.path.exists("data/lesson_components.json"):
        os.remove("data/lesson_components.json")

def test_lesson_component_creation(lesson_component, setup_lesson_component_data):
    """Test creating a new replacewithsmthhhelse"""
    content = {"text": "New lesson_component content"}
    result = lesson_component.create({
        "name": "New lesson_component",
        "lesson_id": 1,
        "type": 1,
        "content": json.dumps(content)
    })
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "New lesson_component"
    
    with open("data/lesson_components.json", "r") as f:
        lesson_components = json.load(f)
    
    assert any(c["name"] == "New lesson_component" for c in lesson_components)

def test_lesson_component_get_by_id(lesson_component, setup_lesson_component_data):
    """Test retrieving a lesson_component by ID"""
    result = lesson_component.get(id=1)
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Introduction Text"
    assert result["data"]["lesson_id"] == 1
    assert result["data"]["type"] == 1

def test_lesson_component_update(lesson_component, setup_lesson_component_data):
    """Test updating lesson_component information"""
    new_content = {"url": "https://example.com/updated_video"}
    result = lesson_component.update({
        "id": 2,
        "content": json.dumps(new_content)
    })
    
    assert result["status"] == "success"
    content = json.loads(result["data"]["content"])
    assert content["url"] == "https://example.com/updated_video"

def test_lesson_component_delete(lesson_component, setup_lesson_component_data):
    """Test deleting a lesson_component"""
    result = lesson_component.remove(id=5)
    
    assert result["status"] == "success"
    
    with open("data/lesson_components.json", "r") as f:
        lesson_components = json.load(f)
    
    assert not any(c["id"] == 5 for c in lesson_components)

def test_get_all_lesson_components(lesson_component, setup_lesson_component_data):
    """Test retrieving all lesson_components"""
    result = lesson_component.get_all()
    
    assert result["status"] == "success"
    assert len(result["data"]) == len(SAMPLE_lesson_componentS)

def test_get_lesson_components_by_lesson(lesson_component, setup_lesson_component_data):
    """Test getting all lesson_components for a specific lesson"""
    result = lesson_component.get_by_lesson_id(1)
    
    assert result["status"] == "success"
    assert all(lesson_component["lesson_id"] == 1 for lesson_component in result["data"])

def test_invalid_lesson_component_id(lesson_component, setup_lesson_component_data):
    """Test getting a nonexistent lesson_component"""
    result = lesson_component.get(id=999)
    
    assert result["status"] == "error"
    assert "not found" in result["data"]

def test_missing_required_fields(lesson_component, setup_lesson_component_data):
    """Test creating a lesson_component without required fields"""
    result = lesson_component.create({
        "name": "Test lesson_component"
        # Missing lesson_id
    })
    
    assert result["status"] == "error"
    assert "required" in result["data"].lower()

def test_lesson_component_content_validation(lesson_component, setup_lesson_component_data):
    """Test that lesson_component content is valid JSON"""
    result = lesson_component.get(id=1)
    
    assert result["status"] == "success"
    content = json.loads(result["data"]["content"])
    assert isinstance(content, dict)
    assert "text" in content