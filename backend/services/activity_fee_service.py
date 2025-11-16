"""
Activity Fee Service

Business logic layer for ActivityFee operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.activity_fee_repository import ActivityFeeRepository
from repositories.activity_repository import ActivityRepository
from repositories.school_repository import SchoolRepository
from models.activity_fee import ActivityFee
from decimal import Decimal
import uuid


class ActivityFeeService:
    """Service layer for ActivityFee business logic"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ActivityFeeRepository(session)
        self.activity_repository = ActivityRepository(session)
        self.school_repository = SchoolRepository(session)

    async def create_activity_fee(
        self,
        school_id: uuid.UUID,
        activity_id: uuid.UUID,
        academic_year: str,
        fee_amount: Decimal,
        fee_frequency: str,
        created_by_id: uuid.UUID,
        allow_prorate: bool = True,
        prorate_calculation: Optional[str] = None,
        description: Optional[str] = None,
        is_active: bool = True
    ) -> ActivityFee:
        """Create a new activity fee structure"""

        # Validate school exists
        school = await self.school_repository.get_by_id(school_id)
        if not school:
            raise ValueError("School not found")

        # Validate activity exists
        activity = await self.activity_repository.get_by_id(activity_id)
        if not activity:
            raise ValueError("Activity not found")

        # Validate activity belongs to school
        if activity.school_id != school_id:
            raise ValueError("Activity does not belong to this school")

        # Validate fee frequency
        valid_frequencies = ['one_time', 'yearly', 'quarterly', 'monthly']
        if fee_frequency not in valid_frequencies:
            raise ValueError(f"Fee frequency must be one of: {', '.join(valid_frequencies)}")

        # Validate fee amount
        if fee_amount < 0:
            raise ValueError("Fee amount must be 0 or greater")

        # Check for duplicate
        exists = await self.repository.exists_for_activity_and_year(
            activity_id=activity_id,
            academic_year=academic_year
        )
        if exists:
            raise ValueError(f"Activity fee already exists for this activity in {academic_year}")

        fee_data = {
            'school_id': school_id,
            'activity_id': activity_id,
            'academic_year': academic_year,
            'fee_amount': fee_amount,
            'fee_frequency': fee_frequency,
            'allow_prorate': allow_prorate,
            'prorate_calculation': prorate_calculation,
            'description': description,
            'is_active': is_active
        }

        created = await self.repository.create(fee_data, created_by_id)
        # Reload with relationships to avoid lazy-loading issues
        return await self.repository.get_with_relationships(created.id)

    async def update_activity_fee(
        self,
        activity_fee_id: uuid.UUID,
        updated_by_id: uuid.UUID,
        fee_amount: Optional[Decimal] = None,
        fee_frequency: Optional[str] = None,
        allow_prorate: Optional[bool] = None,
        prorate_calculation: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[ActivityFee]:
        """Update activity fee structure"""

        update_data = {}

        if fee_amount is not None:
            if fee_amount < 0:
                raise ValueError("Fee amount must be 0 or greater")
            update_data['fee_amount'] = fee_amount

        if fee_frequency is not None:
            valid_frequencies = ['one_time', 'yearly', 'quarterly', 'monthly']
            if fee_frequency not in valid_frequencies:
                raise ValueError(f"Fee frequency must be one of: {', '.join(valid_frequencies)}")
            update_data['fee_frequency'] = fee_frequency

        if allow_prorate is not None:
            update_data['allow_prorate'] = allow_prorate

        if prorate_calculation is not None:
            update_data['prorate_calculation'] = prorate_calculation

        if description is not None:
            update_data['description'] = description

        if is_active is not None:
            update_data['is_active'] = is_active

        if not update_data:
            return await self.repository.get_with_relationships(activity_fee_id)

        updated = await self.repository.update(activity_fee_id, update_data, updated_by_id)
        if updated:
            # Reload with relationships to avoid lazy-loading issues
            return await self.repository.get_with_relationships(updated.id)
        return None

    async def get_activity_fee(
        self,
        activity_fee_id: uuid.UUID,
        include_relationships: bool = True
    ) -> Optional[ActivityFee]:
        """Get activity fee by ID"""
        if include_relationships:
            return await self.repository.get_with_relationships(activity_fee_id)
        return await self.repository.get_by_id(activity_fee_id)

    async def get_by_activity_and_year(
        self,
        activity_id: uuid.UUID,
        academic_year: str
    ) -> Optional[ActivityFee]:
        """Get fee for specific activity and year"""
        return await self.repository.get_by_activity_and_year(
            activity_id=activity_id,
            academic_year=academic_year
        )

    async def list_activity_fees(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None,
        fee_frequency: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[ActivityFee], int]:
        """List activity fees with filters"""
        return await self.repository.get_by_school(
            school_id=school_id,
            academic_year=academic_year,
            fee_frequency=fee_frequency,
            is_active=is_active,
            page=page,
            limit=limit
        )

    async def get_activity_fees_for_year(
        self,
        school_id: uuid.UUID,
        academic_year: str
    ) -> List[ActivityFee]:
        """Get all active activity fees for a school and year"""
        return await self.repository.get_active_for_year(school_id, academic_year)

    async def get_by_frequency(
        self,
        school_id: uuid.UUID,
        fee_frequency: str,
        academic_year: str,
        is_active: bool = True
    ) -> List[ActivityFee]:
        """Get activity fees by frequency"""
        return await self.repository.get_by_frequency(
            school_id=school_id,
            fee_frequency=fee_frequency,
            academic_year=academic_year,
            is_active=is_active
        )

    async def calculate_student_activity_fees(
        self,
        student_id: uuid.UUID,
        academic_year: str,
        school_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Calculate total activity fees for a student"""
        return await self.repository.get_total_fees_for_student_activities(
            student_id=student_id,
            academic_year=academic_year,
            school_id=school_id
        )

    async def calculate_prorated_fee(
        self,
        activity_fee_id: uuid.UUID,
        months_remaining: int
    ) -> Dict[str, Any]:
        """Calculate prorated fee amount"""
        activity_fee = await self.repository.get_by_id(activity_fee_id)
        if not activity_fee:
            raise ValueError("Activity fee not found")

        if months_remaining <= 0:
            raise ValueError("Months remaining must be greater than 0")

        prorated_amount = activity_fee.calculate_prorated_amount(months_remaining)

        return {
            "activity_fee_id": str(activity_fee.id),
            "original_amount": float(activity_fee.fee_amount),
            "fee_frequency": activity_fee.fee_frequency,
            "can_prorate": activity_fee.can_prorate,
            "months_remaining": months_remaining,
            "prorated_amount": float(prorated_amount),
            "savings": float(activity_fee.fee_amount - prorated_amount) if activity_fee.can_prorate else 0.0
        }

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get activity fee statistics"""
        return await self.repository.get_statistics(school_id, academic_year)

    async def activate_activity_fee(
        self,
        activity_fee_id: uuid.UUID,
        updated_by_id: uuid.UUID
    ) -> Optional[ActivityFee]:
        """Activate an activity fee"""
        updated = await self.repository.update(
            activity_fee_id,
            {'is_active': True},
            updated_by_id
        )
        if updated:
            # Reload with relationships to avoid lazy-loading issues
            return await self.repository.get_with_relationships(updated.id)
        return None

    async def deactivate_activity_fee(
        self,
        activity_fee_id: uuid.UUID,
        updated_by_id: uuid.UUID
    ) -> Optional[ActivityFee]:
        """Deactivate an activity fee"""
        updated = await self.repository.update(
            activity_fee_id,
            {'is_active': False},
            updated_by_id
        )
        if updated:
            # Reload with relationships to avoid lazy-loading issues
            return await self.repository.get_with_relationships(updated.id)
        return None

    async def delete_activity_fee(
        self,
        activity_fee_id: uuid.UUID,
        deleted_by_id: uuid.UUID
    ) -> bool:
        """Delete activity fee (soft delete)"""
        return await self.repository.delete(activity_fee_id, deleted_by_id)
