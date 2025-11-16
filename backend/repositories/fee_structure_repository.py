"""
Fee Structure Repository

Data access layer for FeeStructure operations with specialized queries.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from models.fee_structure import FeeStructure
from models.school import School
from repositories.base_repository import BaseRepository
import uuid


class FeeStructureRepository(BaseRepository[FeeStructure]):
    """Repository for FeeStructure data access"""

    def __init__(self, session: AsyncSession):
        super().__init__(FeeStructure, session)

    async def get_with_relationships(self, fee_structure_id: uuid.UUID) -> Optional[FeeStructure]:
        """Get fee structure with all relationships loaded"""
        query = select(FeeStructure).where(
            and_(
                FeeStructure.id == fee_structure_id,
                FeeStructure.deleted_at.is_(None)
            )
        ).options(
            selectinload(FeeStructure.school)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_school_and_grade(
        self,
        school_id: uuid.UUID,
        grade_level: int,
        academic_year: str
    ) -> Optional[FeeStructure]:
        """Get fee structure for a specific school, grade, and academic year"""
        query = select(FeeStructure).where(
            and_(
                FeeStructure.school_id == school_id,
                FeeStructure.grade_level == grade_level,
                FeeStructure.academic_year == academic_year,
                FeeStructure.deleted_at.is_(None)
            )
        ).options(
            selectinload(FeeStructure.school)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None,
        grade_level: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[FeeStructure], int]:
        """Get fee structures for a school with optional filters"""
        offset = (page - 1) * limit

        conditions = [
            FeeStructure.school_id == school_id,
            FeeStructure.deleted_at.is_(None)
        ]

        if academic_year:
            conditions.append(FeeStructure.academic_year == academic_year)
        if grade_level:
            conditions.append(FeeStructure.grade_level == grade_level)
        if is_active is not None:
            conditions.append(FeeStructure.is_active == is_active)

        # Count query
        count_query = select(func.count(FeeStructure.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(FeeStructure).where(and_(*conditions)).options(
            selectinload(FeeStructure.school)
        ).offset(offset).limit(limit).order_by(
            FeeStructure.academic_year.desc(),
            FeeStructure.grade_level.asc()
        )

        result = await self.session.execute(query)
        fee_structures = result.scalars().all()

        return list(fee_structures), total

    async def get_active_by_year(
        self,
        school_id: uuid.UUID,
        academic_year: str
    ) -> List[FeeStructure]:
        """Get all active fee structures for a school and academic year"""
        query = select(FeeStructure).where(
            and_(
                FeeStructure.school_id == school_id,
                FeeStructure.academic_year == academic_year,
                FeeStructure.is_active == True,
                FeeStructure.deleted_at.is_(None)
            )
        ).order_by(FeeStructure.grade_level.asc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def exists_for_grade_and_year(
        self,
        school_id: uuid.UUID,
        grade_level: int,
        academic_year: str,
        exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if fee structure exists for given school, grade, and year"""
        conditions = [
            FeeStructure.school_id == school_id,
            FeeStructure.grade_level == grade_level,
            FeeStructure.academic_year == academic_year,
            FeeStructure.deleted_at.is_(None)
        ]

        if exclude_id:
            conditions.append(FeeStructure.id != exclude_id)

        query = select(func.count(FeeStructure.id)).where(and_(*conditions))
        result = await self.session.execute(query)
        count = result.scalar()

        return count > 0

    async def get_years_for_school(self, school_id: uuid.UUID) -> List[str]:
        """Get all distinct academic years for a school"""
        query = select(FeeStructure.academic_year).where(
            and_(
                FeeStructure.school_id == school_id,
                FeeStructure.deleted_at.is_(None)
            )
        ).distinct().order_by(FeeStructure.academic_year.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def deactivate_old_structures(
        self,
        school_id: uuid.UUID,
        academic_year: str
    ) -> int:
        """Deactivate fee structures older than specified academic year"""
        query = select(FeeStructure).where(
            and_(
                FeeStructure.school_id == school_id,
                FeeStructure.academic_year < academic_year,
                FeeStructure.is_active == True,
                FeeStructure.deleted_at.is_(None)
            )
        )

        result = await self.session.execute(query)
        structures = result.scalars().all()

        count = 0
        for structure in structures:
            structure.is_active = False
            count += 1

        await self.session.flush()
        return count
