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

# Export all models
__all__ = [
    "BaseModel",
    "School",
    "User",
    "Teacher",
    "Student",
    "Parent",
    "ParentStudentRelationship",
]
