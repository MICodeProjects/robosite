from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    google_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    access = Column(Integer, default=2)  # 1=guest, 2=member, 3=admin
    team_id = Column(Integer, ForeignKey('teams.id'))
    team = relationship("Team", back_populates="users")

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship("User", back_populates="team")

class Unit(Base):
    __tablename__ = 'units'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    lessons = relationship("Lesson", back_populates="unit")

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(Integer)
    img = Column(String)
    unit_id = Column(Integer, ForeignKey('units.id'))
    unit = relationship("Unit", back_populates="lessons")
    components = relationship("LessonComponent", back_populates="lesson")

class LessonComponent(Base):
    __tablename__ = 'lesson_components'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(Integer)
    content = Column(String)  # JSON stored as string
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    lesson = relationship("Lesson", back_populates="components")