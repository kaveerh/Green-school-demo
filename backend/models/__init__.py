"""
Models Package
SQLAlchemy ORM models
"""
from models.base import BaseModel
from models.school import School
from models.user import User

# Export all models
__all__ = [
    "BaseModel",
    "School",
    "User",
]
