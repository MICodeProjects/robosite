import pytest
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import lesson_model
from tests.sample_lesson_data import SAMPLE_LESSONS

Lesson = lesson_model.Lesson_Model()

@pytest.fixture
def setup_lesson_data():
    """Setup test data before each test"""
    if os.path.exists("data/lessons.json"):
        os.remove("data/lessons.json")
    
    with open("data/lessons.json", "w") as f:
        json.dump(SAMPLE_LESSONS, f)

    yield
    
    if os.path.exists("data/lessons.json"):
        os.remove("data/lessons.json")

def test_lesson_creation(setup_lesson_data):
    """Test creating a new lesson"""
    result = Lesson.create({
        "name": "Advanced Motion Planning",
        "unit_id": 6,
        "type": 1,
        "img": "motion.png"
    })
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Advanced Motion Planning"
    
    with open("data/lessons.json", "r") as f:
        lessons = json.load(f)
    
    assert any(l["name"] == "Advanced Motion Planning" for l in lessons)

def test_lesson_get_by_id(setup_lesson_data):
    """Test retrieving a lesson by ID"""
    result = Lesson.get(id=1)
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "What is Robotics?"
    assert result["data"]["unit_id"] == 1
    assert result["data"]["type"] == 1

def test_lesson_update(setup_lesson_data):
    """Test updating lesson information"""
    result = Lesson.update({
        "id": 2,
        "name": "Python Fundamentals",
        "img": "python_new.png"
    })
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Python Fundamentals"
    assert result["data"]["img"] == "python_new.png"

def test_lesson_delete(setup_lesson_data):
    """Test deleting a lesson"""
    result = Lesson.remove(id=5)
    
    assert result["status"] == "success"
    
    with open("data/lessons.json", "r") as f:
        lessons = json.load(f)
    
    assert not any(l["id"] == 5 for l in lessons)

def test_get_all_lessons(setup_lesson_data):
    """Test retrieving all lessons"""
    result = Lesson.get_all()
    
    assert result["status"] == "success"
    assert len(result["data"]) == len(SAMPLE_LESSONS)

def test_get_lessons_by_unit(setup_lesson_data):
    """Test getting all lessons for a specific unit"""
    result = Lesson.get_by_unit_id(1)
    
    assert result["status"] == "success"
    assert all(lesson["unit_id"] == 1 for lesson in result["data"])

def test_invalid_lesson_id(setup_lesson_data):
    """Test getting a nonexistent lesson"""
    result = Lesson.get(id=999)
    
    assert result["status"] == "error"
    assert "not found" in result["data"]

def test_duplicate_lesson_name(setup_lesson_data):
    """Test creating a lesson with an existing name"""
    result = Lesson.create({
        "name": "What is Robotics?",
        "unit_id": 1
    })
    
    assert result["status"] == "error"
    assert "already exists" in result["data"]

def test_missing_lesson_name(setup_lesson_data):
    """Test creating a lesson without a name"""
    result = Lesson.create({
        "unit_id": 1,
        "type": 1
    })
    
    assert result["status"] == "error"
    assert "name is required" in result["data"].lower()