"""
Repositories Package
Data access layer with repository pattern
"""
from repositories.base_repository import BaseRepository
from repositories.user_repository import UserRepository

# Export all repositories
__all__ = [
    "BaseRepository",
    "UserRepository",
]
