import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, Unit, Lesson, LessonComponent
from models import lesson_model
from tests.test_data.sample_lesson_data import SAMPLE_LESSONS

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
def lesson(engine):
    """Create a fresh Lesson_Model instance for each test"""
    test_lesson = lesson_model.Lesson_Model()
    test_lesson.initialize_DB(TEST_DB)
    return test_lesson

@pytest.fixture
def setup_lesson_data(session):
    """Setup test data before each test"""
    try:
        # Clean up any existing data
        session.query(LessonComponent).delete()
        session.query(Lesson).delete()
        session.commit()
        
        # Create sample lessons
        for lesson_data in SAMPLE_LESSONS:
            lesson = Lesson(
                name=lesson_data["name"],
                type=lesson_data["type"],
                img=lesson_data["img"],
                unit_id=lesson_data["unit_id"]
            )
            session.add(lesson)
        session.commit()
        yield
    finally:
        # Clean up after each test
        session.query(LessonComponent).delete()
        session.query(Lesson).delete()
        session.commit()

def test_lesson_creation(lesson, setup_lesson_data):
    """Test creating a new lesson"""
    result = lesson.create({
        "name": "Advanced Motion Planning",
        "unit_id": 6,
        "type": 1,
        "img": "motion.png"
    })
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Advanced Motion Planning"
    assert result["data"]["unit_id"] == 6
    assert result["data"]["type"] == 1
    assert result["data"]["img"] == "motion.png"

def test_lesson_get_by_id(lesson, setup_lesson_data):
    """Test retrieving a lesson by ID"""
    # First create a lesson to get
    new_lesson = lesson.create({
        "name": "Test Lesson",
        "unit_id": 1,
        "type": 1,
        "img": "test.png"
    })
    lesson_id = new_lesson["data"]["id"]
    
    result = lesson.get(id=lesson_id)
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Test Lesson"
    assert result["data"]["unit_id"] == 1

def test_lesson_get_all(lesson, setup_lesson_data):
    """Test retrieving all lessons"""
    result = lesson.get_all()
    
    assert result["status"] == "success"
    assert len(result["data"]) == len(SAMPLE_LESSONS)

def test_lesson_get_by_unit(lesson, setup_lesson_data):
    """Test getting all lessons for a specific unit"""
    result = lesson.get_by_unit_id(1)
    
    assert result["status"] == "success"
    assert all(lesson["unit_id"] == 1 for lesson in result["data"])

def test_lesson_update(lesson, setup_lesson_data):
    """Test updating lesson information"""
    # First create a lesson to update
    new_lesson = lesson.create({
        "name": "Test Lesson",
        "unit_id": 1,
        "type": 1,
        "img": "test.png"
    })
    lesson_id = new_lesson["data"]["id"]
    
    result = lesson.update({
        "id": lesson_id,
        "name": "Updated Lesson",
        "type": 2,
        "img": "updated.png"
    })
    
    assert result["status"] == "success"
    assert result["data"]["name"] == "Updated Lesson"
    assert result["data"]["type"] == 2
    assert result["data"]["img"] == "updated.png"

def test_lesson_delete(lesson, setup_lesson_data):
    """Test deleting a lesson"""
    # First create a lesson to delete
    new_lesson = lesson.create({
        "name": "Test Lesson",
        "unit_id": 1,
        "type": 1,
        "img": "test.png"
    })
    lesson_id = new_lesson["data"]["id"]
    
    result = lesson.remove(id=lesson_id)
    
    assert result["status"] == "success"
    
    # Verify lesson was deleted
    get_result = lesson.get(id=lesson_id)
    assert get_result["status"] == "error"
    assert "not found" in get_result["data"]

def test_invalid_lesson_id(lesson, setup_lesson_data):
    """Test getting a nonexistent lesson"""
    result = lesson.get(id=999)
    
    assert result["status"] == "error"
    assert "not found" in result["data"]

def test_missing_required_fields(lesson, setup_lesson_data):
    """Test creating a lesson without required fields"""
    result = lesson.create({
        # Missing name field
        "unit_id": 1
    })
    
    assert result["status"] == "error"
    assert "required" in result["data"].lower()

def test_duplicate_lesson_name(lesson, setup_lesson_data):
    """Test creating a lesson with duplicate name"""
    # First create a lesson
    lesson.create({
        "name": "Test Lesson",
        "unit_id": 1
    })
    
    # Try to create another lesson with same name
    result = lesson.create({
        "name": "Test Lesson",
        "unit_id": 2
    })
    
    assert result["status"] == "error"
    assert "exists" in result["data"].lower()