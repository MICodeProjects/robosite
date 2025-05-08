import pytest
import os
import json
from models.lesson_model import Lesson
from .sample_lesson_data import SAMPLE_LESSONS

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
    lesson = Lesson("Advanced Motion Planning", 6, 1, "motion.png", 5)
    lesson.save()
    
    with open("data/lessons.json", "r") as f:
        lessons = json.load(f)
    
    assert any(l["name"] == "Advanced Motion Planning" for l in lessons)

def test_lesson_get_by_id(setup_lesson_data):
    """Test retrieving a lesson by ID"""
    lesson = Lesson.get_by_id(1)
    assert lesson.name == "What is Robotics?"
    assert lesson.unit_id == 1
    assert lesson.type == 1

def test_lesson_update(setup_lesson_data):
    """Test updating lesson information"""
    lesson = Lesson.get_by_id(2)
    lesson.name = "Python Fundamentals"
    lesson.img = "python_new.png"
    lesson.save()
    
    updated_lesson = Lesson.get_by_id(2)
    assert updated_lesson.name == "Python Fundamentals"
    assert updated_lesson.img == "python_new.png"

def test_lesson_delete(setup_lesson_data):
    """Test deleting a lesson"""
    lesson = Lesson.get_by_id(5)
    lesson.delete()
    
    with open("data/lessons.json", "r") as f:
        lessons = json.load(f)
    
    assert not any(l["id"] == 5 for l in lessons)

def test_get_all_lessons(setup_lesson_data):
    """Test retrieving all lessons"""
    lessons = Lesson.get_all()
    assert len(lessons) == len(SAMPLE_LESSONS)

def test_get_lessons_by_unit(setup_lesson_data):
    """Test getting all lessons for a specific unit"""
    unit_lessons = Lesson.get_by_unit_id(1)
    assert all(lesson.unit_id == 1 for lesson in unit_lessons)

def test_invalid_lesson_id(setup_lesson_data):
    """Test getting a nonexistent lesson"""
    with pytest.raises(Exception):
        Lesson.get_by_id(999)