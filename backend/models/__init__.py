"""
Models Package
SQLAlchemy ORM models
"""
from models.base import BaseModel
from models.school import School
from models.user import User
from models.teacher import Teacher
from models.student import Student, ParentStudentRelationship
from models.parent import Parent
from models.subject import Subject
from models.room import Room
from models.class_model import Class, StudentClass

# Export all models
__all__ = [
    "BaseModel",
    "School",
    "User",
    "Teacher",
    "Student",
    "Parent",
    "ParentStudentRelationship",
    "Subject",
    "Room",
    "Class",
    "StudentClass",
]
