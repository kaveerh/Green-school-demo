"""
Fee Structure Service

Business logic layer for FeeStructure operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.fee_structure_repository import FeeStructureRepository
from repositories.school_repository import SchoolRepository
from models.fee_structure import FeeStructure
from decimal import Decimal
import uuid


class FeeStructureService:
    """Service layer for FeeStructure business logic"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = FeeStructureRepository(session)
        self.school_repository = SchoolRepository(session)

    async def create_fee_structure(
        self,
        school_id: uuid.UUID,
        grade_level: int,
        academic_year: str,
        yearly_amount: Decimal,
        monthly_amount: Decimal,
        weekly_amount: Decimal,
        created_by_id: uuid.UUID,
        yearly_discount: Decimal = Decimal('10.00'),
        monthly_discount: Decimal = Decimal('5.00'),
        weekly_discount: Decimal = Decimal('0.00'),
        sibling_2_discount: Decimal = Decimal('10.00'),
        sibling_3_discount: Decimal = Decimal('15.00'),
        sibling_4_plus_discount: Decimal = Decimal('20.00'),
        apply_sibling_to_all: bool = False,
        is_active: bool = True
    ) -> FeeStructure:
        """Create a new fee structure"""

        # Validate school exists
        school = await self.school_repository.get_by_id(school_id)
        if not school:
            raise ValueError("School not found")

        # Validate grade level
        if grade_level < 1 or grade_level > 7:
            raise ValueError("Grade level must be between 1 and 7")

        # Check for duplicate
        exists = await self.repository.exists_for_grade_and_year(
            school_id=school_id,
            grade_level=grade_level,
            academic_year=academic_year
        )
        if exists:
            raise ValueError(
                f"Fee structure already exists for grade {grade_level} in {academic_year}"
            )

        # Validate amounts
        if yearly_amount <= 0 or monthly_amount <= 0 or weekly_amount <= 0:
            raise ValueError("Fee amounts must be greater than 0")

        # Validate discounts
        if not (0 <= yearly_discount <= 100):
            raise ValueError("Yearly discount must be between 0 and 100")
        if not (0 <= monthly_discount <= 100):
            raise ValueError("Monthly discount must be between 0 and 100")
        if not (0 <= weekly_discount <= 100):
            raise ValueError("Weekly discount must be between 0 and 100")

        fee_data = {
            'school_id': school_id,
            'grade_level': grade_level,
            'academic_year': academic_year,
            'yearly_amount': yearly_amount,
            'monthly_amount': monthly_amount,
            'weekly_amount': weekly_amount,
            'yearly_discount': yearly_discount,
            'monthly_discount': monthly_discount,
            'weekly_discount': weekly_discount,
            'sibling_2_discount': sibling_2_discount,
            'sibling_3_discount': sibling_3_discount,
            'sibling_4_plus_discount': sibling_4_plus_discount,
            'apply_sibling_to_all': apply_sibling_to_all,
            'is_active': is_active
        }

        return await self.repository.create(fee_data, created_by_id)

    async def update_fee_structure(
        self,
        fee_structure_id: uuid.UUID,
        updated_by_id: uuid.UUID,
        yearly_amount: Optional[Decimal] = None,
        monthly_amount: Optional[Decimal] = None,
        weekly_amount: Optional[Decimal] = None,
        yearly_discount: Optional[Decimal] = None,
        monthly_discount: Optional[Decimal] = None,
        weekly_discount: Optional[Decimal] = None,
        sibling_2_discount: Optional[Decimal] = None,
        sibling_3_discount: Optional[Decimal] = None,
        sibling_4_plus_discount: Optional[Decimal] = None,
        apply_sibling_to_all: Optional[bool] = None,
        is_active: Optional[bool] = None
    ) -> Optional[FeeStructure]:
        """Update fee structure"""

        update_data = {}

        if yearly_amount is not None:
            if yearly_amount <= 0:
                raise ValueError("Yearly amount must be greater than 0")
            update_data['yearly_amount'] = yearly_amount

        if monthly_amount is not None:
            if monthly_amount <= 0:
                raise ValueError("Monthly amount must be greater than 0")
            update_data['monthly_amount'] = monthly_amount

        if weekly_amount is not None:
            if weekly_amount <= 0:
                raise ValueError("Weekly amount must be greater than 0")
            update_data['weekly_amount'] = weekly_amount

        # Validate and update discounts
        for field, value in [
            ('yearly_discount', yearly_discount),
            ('monthly_discount', monthly_discount),
            ('weekly_discount', weekly_discount),
            ('sibling_2_discount', sibling_2_discount),
            ('sibling_3_discount', sibling_3_discount),
            ('sibling_4_plus_discount', sibling_4_plus_discount)
        ]:
            if value is not None:
                if not (0 <= value <= 100):
                    raise ValueError(f"{field} must be between 0 and 100")
                update_data[field] = value

        if apply_sibling_to_all is not None:
            update_data['apply_sibling_to_all'] = apply_sibling_to_all

        if is_active is not None:
            update_data['is_active'] = is_active

        if not update_data:
            return await self.repository.get_by_id(fee_structure_id)

        return await self.repository.update(fee_structure_id, update_data, updated_by_id)

    async def get_fee_structure(
        self,
        fee_structure_id: uuid.UUID,
        include_relationships: bool = True
    ) -> Optional[FeeStructure]:
        """Get fee structure by ID"""
        if include_relationships:
            return await self.repository.get_with_relationships(fee_structure_id)
        return await self.repository.get_by_id(fee_structure_id)

    async def get_by_school_and_grade(
        self,
        school_id: uuid.UUID,
        grade_level: int,
        academic_year: str
    ) -> Optional[FeeStructure]:
        """Get fee structure for specific school, grade, and year"""
        return await self.repository.get_by_school_and_grade(
            school_id=school_id,
            grade_level=grade_level,
            academic_year=academic_year
        )

    async def list_fee_structures(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None,
        grade_level: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[FeeStructure], int]:
        """List fee structures with filters"""
        return await self.repository.get_by_school(
            school_id=school_id,
            academic_year=academic_year,
            grade_level=grade_level,
            is_active=is_active,
            page=page,
            limit=limit
        )

    async def get_active_structures(
        self,
        school_id: uuid.UUID,
        academic_year: str
    ) -> List[FeeStructure]:
        """Get all active fee structures for a school and year"""
        return await self.repository.get_active_by_year(school_id, academic_year)

    async def get_academic_years(self, school_id: uuid.UUID) -> List[str]:
        """Get all academic years for a school"""
        return await self.repository.get_years_for_school(school_id)

    async def deactivate_fee_structure(
        self,
        fee_structure_id: uuid.UUID,
        updated_by_id: uuid.UUID
    ) -> Optional[FeeStructure]:
        """Deactivate a fee structure"""
        return await self.repository.update(
            fee_structure_id,
            {'is_active': False},
            updated_by_id
        )

    async def activate_fee_structure(
        self,
        fee_structure_id: uuid.UUID,
        updated_by_id: uuid.UUID
    ) -> Optional[FeeStructure]:
        """Activate a fee structure"""
        return await self.repository.update(
            fee_structure_id,
            {'is_active': True},
            updated_by_id
        )

    async def deactivate_old_structures(
        self,
        school_id: uuid.UUID,
        academic_year: str
    ) -> int:
        """Deactivate fee structures older than specified year"""
        return await self.repository.deactivate_old_structures(school_id, academic_year)

    async def delete_fee_structure(
        self,
        fee_structure_id: uuid.UUID,
        deleted_by_id: uuid.UUID
    ) -> bool:
        """Delete fee structure (soft delete)"""
        # Note: Should check if any student fees reference this structure
        return await self.repository.delete(fee_structure_id, deleted_by_id)
