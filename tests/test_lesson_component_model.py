import pytest
import os
import json
from models.lesson_component_model import LessonComponent
from .sample_lesson_component_data import SAMPLE_LESSON_COMPONENTS

@pytest.fixture
def setup_lesson_component_data():
    """Setup test data before each test"""
    if os.path.exists("data/lesson_components.json"):
        os.remove("data/lesson_components.json")
    
    with open("data/lesson_components.json", "w") as f:
        json.dump(SAMPLE_LESSON_COMPONENTS, f)

    yield
    
    if os.path.exists("data/lesson_components.json"):
        os.remove("data/lesson_components.json")

def test_component_creation(setup_lesson_component_data):
    """Test creating a new lesson component"""
    content = {"text": "New component content"}
    component = LessonComponent("New Component", 6, 1, 1, json.dumps(content))
    component.save()
    
    with open("data/lesson_components.json", "r") as f:
        components = json.load(f)
    
    assert any(c["name"] == "New Component" for c in components)

def test_component_get_by_id(setup_lesson_component_data):
    """Test retrieving a component by ID"""
    component = LessonComponent.get_by_id(1)
    assert component.name == "Introduction Text"
    assert component.lesson_id == 1
    assert component.type == 1

def test_component_update(setup_lesson_component_data):
    """Test updating component information"""
    component = LessonComponent.get_by_id(2)
    new_content = {"url": "https://example.com/updated_video"}
    component.content = json.dumps(new_content)
    component.save()
    
    updated_component = LessonComponent.get_by_id(2)
    assert json.loads(updated_component.content)["url"] == "https://example.com/updated_video"

def test_component_delete(setup_lesson_component_data):
    """Test deleting a component"""
    component = LessonComponent.get_by_id(5)
    component.delete()
    
    with open("data/lesson_components.json", "r") as f:
        components = json.load(f)
    
    assert not any(c["id"] == 5 for c in components)

def test_get_all_components(setup_lesson_component_data):
    """Test retrieving all components"""
    components = LessonComponent.get_all()
    assert len(components) == len(SAMPLE_LESSON_COMPONENTS)

def test_get_components_by_lesson(setup_lesson_component_data):
    """Test getting all components for a specific lesson"""
    lesson_components = LessonComponent.get_by_lesson_id(1)
    assert all(component.lesson_id == 1 for component in lesson_components)

def test_invalid_component_id(setup_lesson_component_data):
    """Test getting a nonexistent component"""
    with pytest.raises(Exception):
        LessonComponent.get_by_id(999)

def test_component_content_validation(setup_lesson_component_data):
    """Test that component content is valid JSON"""
    component = LessonComponent.get_by_id(1)
    content = json.loads(component.content)
    assert isinstance(content, dict)
    assert "text" in content