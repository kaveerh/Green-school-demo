"""
Bursary Repository

Data access layer for Bursary operations with specialized queries.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from models.bursary import Bursary
from models.school import School
from repositories.base_repository import BaseRepository
import uuid
from datetime import date


class BursaryRepository(BaseRepository[Bursary]):
    """Repository for Bursary data access"""

    def __init__(self, session: AsyncSession):
        super().__init__(Bursary, session)

    async def get_with_relationships(self, bursary_id: uuid.UUID) -> Optional[Bursary]:
        """Get bursary with all relationships loaded"""
        query = select(Bursary).where(
            and_(
                Bursary.id == bursary_id,
                Bursary.deleted_at.is_(None)
            )
        ).options(
            selectinload(Bursary.school),
            selectinload(Bursary.student_fees)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None,
        bursary_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        has_capacity: Optional[bool] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Bursary], int]:
        """Get bursaries for a school with optional filters"""
        offset = (page - 1) * limit

        conditions = [
            Bursary.school_id == school_id,
            Bursary.deleted_at.is_(None)
        ]

        if academic_year:
            conditions.append(Bursary.academic_year == academic_year)
        if bursary_type:
            conditions.append(Bursary.bursary_type == bursary_type)
        if is_active is not None:
            conditions.append(Bursary.is_active == is_active)

        # Base query
        query_base = select(Bursary).where(and_(*conditions))

        # Add capacity filter if requested
        if has_capacity is not None and has_capacity:
            # Only bursaries with capacity
            query_base = query_base.where(
                or_(
                    Bursary.max_recipients.is_(None),  # Unlimited
                    Bursary.current_recipients < Bursary.max_recipients
                )
            )

        # Count query
        count_query = select(func.count()).select_from(query_base.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = query_base.options(
            selectinload(Bursary.school)
        ).offset(offset).limit(limit).order_by(
            Bursary.academic_year.desc(),
            Bursary.name.asc()
        )

        result = await self.session.execute(query)
        bursaries = result.scalars().all()

        return list(bursaries), total

    async def get_available_for_student(
        self,
        school_id: uuid.UUID,
        grade_level: int,
        academic_year: str
    ) -> List[Bursary]:
        """Get all available bursaries for a student based on grade and year"""
        today = date.today()

        query = select(Bursary).where(
            and_(
                Bursary.school_id == school_id,
                Bursary.academic_year == academic_year,
                Bursary.is_active == True,
                Bursary.deleted_at.is_(None),
                # Grade is eligible
                Bursary.eligible_grades.contains([grade_level]),
                # Has capacity or unlimited
                or_(
                    Bursary.max_recipients.is_(None),
                    Bursary.current_recipients < Bursary.max_recipients
                ),
                # Deadline not passed or no deadline
                or_(
                    Bursary.application_deadline.is_(None),
                    Bursary.application_deadline >= today
                )
            )
        ).order_by(Bursary.name.asc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_type(
        self,
        school_id: uuid.UUID,
        bursary_type: str,
        academic_year: str,
        is_active: bool = True
    ) -> List[Bursary]:
        """Get bursaries by type for a school and academic year"""
        query = select(Bursary).where(
            and_(
                Bursary.school_id == school_id,
                Bursary.bursary_type == bursary_type,
                Bursary.academic_year == academic_year,
                Bursary.is_active == is_active,
                Bursary.deleted_at.is_(None)
            )
        ).order_by(Bursary.name.asc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_recipients(
        self,
        bursary_id: uuid.UUID,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Any], int]:
        """Get all students receiving this bursary"""
        from models.student_fee import StudentFee
        from models.student import Student
        from models.user import User

        offset = (page - 1) * limit

        conditions = [
            StudentFee.bursary_id == bursary_id,
            StudentFee.deleted_at.is_(None)
        ]

        # Count query
        count_query = select(func.count(StudentFee.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(StudentFee).where(and_(*conditions)).options(
            selectinload(StudentFee.student).selectinload(Student.user),
            selectinload(StudentFee.school)
        ).offset(offset).limit(limit).order_by(StudentFee.created_at.desc())

        result = await self.session.execute(query)
        student_fees = result.scalars().all()

        return list(student_fees), total

    async def increment_recipients(self, bursary_id: uuid.UUID) -> bool:
        """Increment the current recipients count"""
        bursary = await self.get_by_id(bursary_id)
        if not bursary:
            return False

        bursary.increment_recipients()
        await self.session.flush()
        return True

    async def decrement_recipients(self, bursary_id: uuid.UUID) -> bool:
        """Decrement the current recipients count"""
        bursary = await self.get_by_id(bursary_id)
        if not bursary:
            return False

        bursary.decrement_recipients()
        await self.session.flush()
        return True

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get bursary statistics for a school"""
        from models.student_fee import StudentFee

        conditions = [
            Bursary.school_id == school_id,
            Bursary.deleted_at.is_(None)
        ]

        if academic_year:
            conditions.append(Bursary.academic_year == academic_year)

        # Total bursaries
        total_query = select(func.count(Bursary.id)).where(and_(*conditions))
        total_result = await self.session.execute(total_query)
        total_bursaries = total_result.scalar()

        # Active bursaries
        active_query = select(func.count(Bursary.id)).where(
            and_(*conditions, Bursary.is_active == True)
        )
        active_result = await self.session.execute(active_query)
        active_bursaries = active_result.scalar()

        # Total recipients
        recipients_query = select(func.sum(Bursary.current_recipients)).where(and_(*conditions))
        recipients_result = await self.session.execute(recipients_query)
        total_recipients = recipients_result.scalar() or 0

        # Total bursary amount distributed (from student_fees)
        if academic_year:
            amount_query = select(func.sum(StudentFee.bursary_amount)).where(
                and_(
                    StudentFee.school_id == school_id,
                    StudentFee.academic_year == academic_year,
                    StudentFee.bursary_id.isnot(None),
                    StudentFee.deleted_at.is_(None)
                )
            )
        else:
            amount_query = select(func.sum(StudentFee.bursary_amount)).where(
                and_(
                    StudentFee.school_id == school_id,
                    StudentFee.bursary_id.isnot(None),
                    StudentFee.deleted_at.is_(None)
                )
            )
        amount_result = await self.session.execute(amount_query)
        total_amount = amount_result.scalar() or 0

        # By type
        type_query = select(
            Bursary.bursary_type,
            func.count(Bursary.id).label('count'),
            func.sum(Bursary.current_recipients).label('recipients')
        ).where(and_(*conditions)).group_by(Bursary.bursary_type)
        type_result = await self.session.execute(type_query)
        by_type = {row[0]: {"count": row[1], "recipients": row[2] or 0} for row in type_result}

        return {
            "total_bursaries": total_bursaries,
            "active_bursaries": active_bursaries,
            "total_recipients": int(total_recipients),
            "total_amount_distributed": float(total_amount),
            "by_type": by_type
        }
