"""
Repositories Package
Data access layer with repository pattern
"""
from repositories.base_repository import BaseRepository
from repositories.user_repository import UserRepository
from repositories.fee_structure_repository import FeeStructureRepository
from repositories.bursary_repository import BursaryRepository
from repositories.student_fee_repository import StudentFeeRepository
from repositories.payment_repository import PaymentRepository
from repositories.activity_fee_repository import ActivityFeeRepository

# Export all repositories
__all__ = [
    "BaseRepository",
    "UserRepository",
    "FeeStructureRepository",
    "BursaryRepository",
    "StudentFeeRepository",
    "PaymentRepository",
    "ActivityFeeRepository",
]
