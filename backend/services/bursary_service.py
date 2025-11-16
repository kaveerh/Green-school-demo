"""
Bursary Service

Business logic layer for Bursary operations with assignment and capacity management.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.bursary_repository import BursaryRepository
from repositories.school_repository import SchoolRepository
from models.bursary import Bursary
from decimal import Decimal
from datetime import date
import uuid


class BursaryService:
    """Service layer for Bursary business logic"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = BursaryRepository(session)
        self.school_repository = SchoolRepository(session)

    async def create_bursary(
        self,
        school_id: uuid.UUID,
        name: str,
        bursary_type: str,
        coverage_type: str,
        coverage_value: Decimal,
        academic_year: str,
        eligible_grades: List[int],
        created_by_id: uuid.UUID,
        description: Optional[str] = None,
        max_coverage_amount: Optional[Decimal] = None,
        max_recipients: Optional[int] = None,
        application_deadline: Optional[date] = None,
        sponsor_name: Optional[str] = None,
        sponsor_contact: Optional[str] = None,
        terms_and_conditions: Optional[str] = None,
        is_active: bool = True
    ) -> Bursary:
        """Create a new bursary program"""

        # Validate school exists
        school = await self.school_repository.get_by_id(school_id)
        if not school:
            raise ValueError("School not found")

        # Validate bursary type
        valid_types = ['merit', 'need', 'sports', 'academic', 'other']
        if bursary_type not in valid_types:
            raise ValueError(f"Bursary type must be one of: {', '.join(valid_types)}")

        # Validate coverage type
        if coverage_type not in ['percentage', 'fixed_amount']:
            raise ValueError("Coverage type must be 'percentage' or 'fixed_amount'")

        # Validate coverage value
        if coverage_value <= 0:
            raise ValueError("Coverage value must be greater than 0")

        if coverage_type == 'percentage' and coverage_value > 100:
            raise ValueError("Percentage coverage cannot exceed 100%")

        # Validate eligible grades
        if not eligible_grades:
            raise ValueError("At least one eligible grade must be specified")

        for grade in eligible_grades:
            if grade < 1 or grade > 7:
                raise ValueError("Eligible grades must be between 1 and 7")

        # Validate max recipients
        if max_recipients is not None and max_recipients <= 0:
            raise ValueError("Max recipients must be greater than 0 or null for unlimited")

        bursary_data = {
            'school_id': school_id,
            'name': name,
            'description': description,
            'bursary_type': bursary_type,
            'coverage_type': coverage_type,
            'coverage_value': coverage_value,
            'max_coverage_amount': max_coverage_amount,
            'academic_year': academic_year,
            'eligible_grades': eligible_grades,
            'max_recipients': max_recipients,
            'current_recipients': 0,
            'is_active': is_active,
            'application_deadline': application_deadline,
            'sponsor_name': sponsor_name,
            'sponsor_contact': sponsor_contact,
            'terms_and_conditions': terms_and_conditions
        }

        return await self.repository.create(bursary_data, created_by_id)

    async def update_bursary(
        self,
        bursary_id: uuid.UUID,
        updated_by_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        coverage_type: Optional[str] = None,
        coverage_value: Optional[Decimal] = None,
        max_coverage_amount: Optional[Decimal] = None,
        eligible_grades: Optional[List[int]] = None,
        max_recipients: Optional[int] = None,
        application_deadline: Optional[date] = None,
        sponsor_name: Optional[str] = None,
        sponsor_contact: Optional[str] = None,
        terms_and_conditions: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Bursary]:
        """Update bursary program"""

        update_data = {}

        if name is not None:
            update_data['name'] = name

        if description is not None:
            update_data['description'] = description

        if coverage_type is not None:
            if coverage_type not in ['percentage', 'fixed_amount']:
                raise ValueError("Coverage type must be 'percentage' or 'fixed_amount'")
            update_data['coverage_type'] = coverage_type

        if coverage_value is not None:
            if coverage_value <= 0:
                raise ValueError("Coverage value must be greater than 0")
            update_data['coverage_value'] = coverage_value

        if max_coverage_amount is not None:
            update_data['max_coverage_amount'] = max_coverage_amount

        if eligible_grades is not None:
            if not eligible_grades:
                raise ValueError("At least one eligible grade must be specified")
            for grade in eligible_grades:
                if grade < 1 or grade > 7:
                    raise ValueError("Eligible grades must be between 1 and 7")
            update_data['eligible_grades'] = eligible_grades

        if max_recipients is not None:
            if max_recipients <= 0:
                raise ValueError("Max recipients must be greater than 0 or null")
            update_data['max_recipients'] = max_recipients

        if application_deadline is not None:
            update_data['application_deadline'] = application_deadline

        if sponsor_name is not None:
            update_data['sponsor_name'] = sponsor_name

        if sponsor_contact is not None:
            update_data['sponsor_contact'] = sponsor_contact

        if terms_and_conditions is not None:
            update_data['terms_and_conditions'] = terms_and_conditions

        if is_active is not None:
            update_data['is_active'] = is_active

        if not update_data:
            return await self.repository.get_by_id(bursary_id)

        return await self.repository.update(bursary_id, update_data, updated_by_id)

    async def get_bursary(
        self,
        bursary_id: uuid.UUID,
        include_relationships: bool = True
    ) -> Optional[Bursary]:
        """Get bursary by ID"""
        if include_relationships:
            return await self.repository.get_with_relationships(bursary_id)
        return await self.repository.get_by_id(bursary_id)

    async def list_bursaries(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None,
        bursary_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        has_capacity: Optional[bool] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Bursary], int]:
        """List bursaries with filters"""
        return await self.repository.get_by_school(
            school_id=school_id,
            academic_year=academic_year,
            bursary_type=bursary_type,
            is_active=is_active,
            has_capacity=has_capacity,
            page=page,
            limit=limit
        )

    async def get_available_for_student(
        self,
        school_id: uuid.UUID,
        grade_level: int,
        academic_year: str
    ) -> List[Bursary]:
        """Get all bursaries available for a student"""
        return await self.repository.get_available_for_student(
            school_id=school_id,
            grade_level=grade_level,
            academic_year=academic_year
        )

    async def get_by_type(
        self,
        school_id: uuid.UUID,
        bursary_type: str,
        academic_year: str,
        is_active: bool = True
    ) -> List[Bursary]:
        """Get bursaries by type"""
        return await self.repository.get_by_type(
            school_id=school_id,
            bursary_type=bursary_type,
            academic_year=academic_year,
            is_active=is_active
        )

    async def get_recipients(
        self,
        bursary_id: uuid.UUID,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Any], int]:
        """Get all students receiving this bursary"""
        return await self.repository.get_recipients(
            bursary_id=bursary_id,
            page=page,
            limit=limit
        )

    async def check_eligibility(
        self,
        bursary_id: uuid.UUID,
        grade_level: int
    ) -> Dict[str, Any]:
        """Check if a student is eligible for a bursary"""
        bursary = await self.repository.get_by_id(bursary_id)
        if not bursary:
            raise ValueError("Bursary not found")

        eligible = True
        reasons = []

        # Check if active
        if not bursary.is_active:
            eligible = False
            reasons.append("Bursary is not active")

        # Check capacity
        if not bursary.has_capacity:
            eligible = False
            reasons.append(f"Bursary has reached maximum capacity ({bursary.max_recipients} recipients)")

        # Check deadline
        if bursary.is_deadline_passed:
            eligible = False
            reasons.append(f"Application deadline has passed ({bursary.application_deadline})")

        # Check grade eligibility
        if not bursary.is_grade_eligible(grade_level):
            eligible = False
            reasons.append(f"Grade {grade_level} is not eligible (eligible grades: {bursary.eligible_grades})")

        return {
            "eligible": eligible,
            "bursary_id": str(bursary.id),
            "bursary_name": bursary.name,
            "reasons": reasons if not eligible else ["Student is eligible"],
            "coverage_info": {
                "type": bursary.coverage_type,
                "value": float(bursary.coverage_value),
                "max_amount": float(bursary.max_coverage_amount) if bursary.max_coverage_amount else None
            }
        }

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get bursary statistics"""
        return await self.repository.get_statistics(school_id, academic_year)

    async def activate_bursary(
        self,
        bursary_id: uuid.UUID,
        updated_by_id: uuid.UUID
    ) -> Optional[Bursary]:
        """Activate a bursary"""
        return await self.repository.update(
            bursary_id,
            {'is_active': True},
            updated_by_id
        )

    async def deactivate_bursary(
        self,
        bursary_id: uuid.UUID,
        updated_by_id: uuid.UUID
    ) -> Optional[Bursary]:
        """Deactivate a bursary"""
        return await self.repository.update(
            bursary_id,
            {'is_active': False},
            updated_by_id
        )

    async def delete_bursary(
        self,
        bursary_id: uuid.UUID,
        deleted_by_id: uuid.UUID
    ) -> bool:
        """Delete bursary (soft delete)"""
        # Note: Should check if any student fees reference this bursary
        bursary = await self.repository.get_by_id(bursary_id)
        if not bursary:
            return False

        if bursary.current_recipients > 0:
            raise ValueError(
                f"Cannot delete bursary with {bursary.current_recipients} active recipients. "
                "Please remove recipients first."
            )

        return await self.repository.delete(bursary_id, deleted_by_id)
