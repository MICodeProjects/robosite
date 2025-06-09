import pytest
import os
import sys
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, Unit, Lesson, LessonComponent
from models import lesson_model
from test_data.sample_lesson_data import SAMPLE_LESSONS

# Use SQLite in-memory database for testing
TEST_DB = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def engine():
    """Create a fresh database engine for each test"""
    engine = create_engine(TEST_DB, echo=True)  # Add echo=True for debugging
    Base.metadata.drop_all(engine)  # Clear all tables
    Base.metadata.create_all(engine)  # Create fresh tables
    return engine

@pytest.fixture(scope="function")
def session(engine):
    """Create a new session for each test"""
    Session = sessionmaker(bind=engine)
    session = Session()
    return session  # Remove yield as we want setup_lesson_data to manage cleanup

@pytest.fixture(scope="function")
def lesson(engine, session):  # Add session dependency
    """Create a fresh Lesson_Model instance for each test"""
    test_lesson = lesson_model.LessonModel()
    test_lesson.initialize_DB(TEST_DB)
    test_lesson.Session = sessionmaker(bind=engine)  # Use the same engine
    return test_lesson

@pytest.fixture(scope="function", autouse=True)
def setup_lesson_data(engine, session, lesson):  # Add engine and lesson dependencies
    """Setup test data before each test"""
    try:
        # Clean up any existing data
        session.query(LessonComponent).delete()
        session.query(Lesson).delete()
        session.query(Unit).delete()
        session.commit()
        
        # Create units first (since lessons depend on units)
        units = {}
        for lesson_data in SAMPLE_LESSONS:
            if "unit_id" in lesson_data:
                unit = Unit(
                    id=lesson_data["unit_id"],
                    name=f"Unit {lesson_data['unit_id']}"  # Create placeholder unit names
                )
                units[lesson_data["unit_id"]] = unit
                session.add(unit)
        session.commit()
        
        # Create sample lessons
        for lesson_data in SAMPLE_LESSONS:
            lesson = Lesson(
                name=lesson_data.get("name"),
                type=lesson_data.get("type", 1),
                img=lesson_data.get("img", ""),
                unit_id=lesson_data.get("unit_id")
            )
            session.add(lesson)
        session.commit()
        
        # Verify data was created
        units = session.query(Unit).all()
        lessons = session.query(Lesson).all()
        print(f"Created {len(units)} units and {len(lessons)} lessons")  # Debug output
        
        yield
        
        # Cleanup after test
        session.query(LessonComponent).delete()
        session.query(Lesson).delete()
        session.query(Unit).delete()
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

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