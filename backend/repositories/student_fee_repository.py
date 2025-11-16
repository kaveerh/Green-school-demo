"""
Student Fee Repository

Data access layer for StudentFee operations with fee calculation and payment tracking.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from models.student_fee import StudentFee
from models.student import Student
from models.user import User
from models.bursary import Bursary
from models.school import School
from repositories.base_repository import BaseRepository
from decimal import Decimal
import uuid
from datetime import date


class StudentFeeRepository(BaseRepository[StudentFee]):
    """Repository for StudentFee data access with calculation logic"""

    def __init__(self, session: AsyncSession):
        super().__init__(StudentFee, session)

    async def get_with_relationships(self, student_fee_id: uuid.UUID) -> Optional[StudentFee]:
        """Get student fee with all relationships loaded"""
        query = select(StudentFee).where(
            and_(
                StudentFee.id == student_fee_id,
                StudentFee.deleted_at.is_(None)
            )
        ).options(
            selectinload(StudentFee.student).selectinload(Student.user),
            selectinload(StudentFee.school),
            selectinload(StudentFee.bursary),
            selectinload(StudentFee.payments)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_student_and_year(
        self,
        student_id: uuid.UUID,
        academic_year: str
    ) -> Optional[StudentFee]:
        """Get fee record for a student and academic year"""
        query = select(StudentFee).where(
            and_(
                StudentFee.student_id == student_id,
                StudentFee.academic_year == academic_year,
                StudentFee.deleted_at.is_(None)
            )
        ).options(
            selectinload(StudentFee.bursary),
            selectinload(StudentFee.payments)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_student(
        self,
        student_id: uuid.UUID,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[StudentFee], int]:
        """Get all fee records for a student"""
        offset = (page - 1) * limit

        conditions = [
            StudentFee.student_id == student_id,
            StudentFee.deleted_at.is_(None)
        ]

        if status:
            conditions.append(StudentFee.status == status)

        # Count query
        count_query = select(func.count(StudentFee.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(StudentFee).where(and_(*conditions)).options(
            selectinload(StudentFee.bursary),
            selectinload(StudentFee.payments)
        ).offset(offset).limit(limit).order_by(StudentFee.academic_year.desc())

        result = await self.session.execute(query)
        student_fees = result.scalars().all()

        return list(student_fees), total

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None,
        status: Optional[str] = None,
        payment_frequency: Optional[str] = None,
        has_bursary: Optional[bool] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[StudentFee], int]:
        """Get student fees for a school with optional filters"""
        offset = (page - 1) * limit

        conditions = [
            StudentFee.school_id == school_id,
            StudentFee.deleted_at.is_(None)
        ]

        if academic_year:
            conditions.append(StudentFee.academic_year == academic_year)
        if status:
            conditions.append(StudentFee.status == status)
        if payment_frequency:
            conditions.append(StudentFee.payment_frequency == payment_frequency)
        if has_bursary is not None:
            if has_bursary:
                conditions.append(StudentFee.bursary_id.isnot(None))
            else:
                conditions.append(StudentFee.bursary_id.is_(None))

        # Count query
        count_query = select(func.count(StudentFee.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(StudentFee).where(and_(*conditions)).options(
            selectinload(StudentFee.student).selectinload(Student.user),
            selectinload(StudentFee.bursary)
        ).offset(offset).limit(limit).order_by(
            StudentFee.academic_year.desc(),
            StudentFee.status.asc()
        )

        result = await self.session.execute(query)
        student_fees = result.scalars().all()

        return list(student_fees), total

    async def get_overdue(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[StudentFee], int]:
        """Get all overdue fee records"""
        offset = (page - 1) * limit
        today = date.today()

        conditions = [
            StudentFee.school_id == school_id,
            StudentFee.status.in_(['pending', 'partial', 'overdue']),
            StudentFee.balance_due > 0,
            StudentFee.due_date < today,
            StudentFee.deleted_at.is_(None)
        ]

        if academic_year:
            conditions.append(StudentFee.academic_year == academic_year)

        # Count query
        count_query = select(func.count(StudentFee.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(StudentFee).where(and_(*conditions)).options(
            selectinload(StudentFee.student).selectinload(Student.user)
        ).offset(offset).limit(limit).order_by(StudentFee.due_date.asc())

        result = await self.session.execute(query)
        student_fees = result.scalars().all()

        return list(student_fees), total

    async def get_by_bursary(
        self,
        bursary_id: uuid.UUID,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[StudentFee], int]:
        """Get all fee records using a specific bursary"""
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
            selectinload(StudentFee.student).selectinload(Student.user)
        ).offset(offset).limit(limit).order_by(StudentFee.created_at.desc())

        result = await self.session.execute(query)
        student_fees = result.scalars().all()

        return list(student_fees), total

    async def exists_for_student_and_year(
        self,
        student_id: uuid.UUID,
        academic_year: str,
        exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if fee record exists for student and year"""
        conditions = [
            StudentFee.student_id == student_id,
            StudentFee.academic_year == academic_year,
            StudentFee.deleted_at.is_(None)
        ]

        if exclude_id:
            conditions.append(StudentFee.id != exclude_id)

        query = select(func.count(StudentFee.id)).where(and_(*conditions))
        result = await self.session.execute(query)
        count = result.scalar()

        return count > 0

    async def calculate_sibling_order(
        self,
        student_id: uuid.UUID,
        school_id: uuid.UUID,
        academic_year: str
    ) -> int:
        """
        Calculate sibling order for a student based on enrollment date
        Returns 1 for first child, 2 for second, etc.
        """
        from models.parent import Parent
        from models.student import ParentStudentRelationship

        # Get parents of this student
        parent_query = select(ParentStudentRelationship.parent_id).where(
            and_(
                ParentStudentRelationship.student_id == student_id,
                ParentStudentRelationship.deleted_at.is_(None)
            )
        )
        parent_result = await self.session.execute(parent_query)
        parent_ids = [row[0] for row in parent_result]

        if not parent_ids:
            return 1  # No parents, treat as first child

        # Get all students with same parents
        sibling_query = select(Student).join(
            ParentStudentRelationship,
            Student.id == ParentStudentRelationship.student_id
        ).where(
            and_(
                ParentStudentRelationship.parent_id.in_(parent_ids),
                Student.school_id == school_id,
                Student.status == 'enrolled',
                Student.deleted_at.is_(None)
            )
        ).order_by(Student.enrollment_date.asc())

        sibling_result = await self.session.execute(sibling_query)
        siblings = sibling_result.scalars().all()

        # Find position of current student
        for index, sibling in enumerate(siblings, start=1):
            if sibling.id == student_id:
                return index

        return 1  # Default to first child if not found

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get fee statistics for a school"""
        conditions = [
            StudentFee.school_id == school_id,
            StudentFee.deleted_at.is_(None)
        ]

        if academic_year:
            conditions.append(StudentFee.academic_year == academic_year)

        # Total student fees
        total_query = select(func.count(StudentFee.id)).where(and_(*conditions))
        total_result = await self.session.execute(total_query)
        total_fees = total_result.scalar()

        # By status
        status_query = select(
            StudentFee.status,
            func.count(StudentFee.id).label('count')
        ).where(and_(*conditions)).group_by(StudentFee.status)
        status_result = await self.session.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result}

        # Financial totals
        totals_query = select(
            func.sum(StudentFee.total_before_discounts).label('total_before_discounts'),
            func.sum(StudentFee.total_discounts).label('total_discounts'),
            func.sum(StudentFee.bursary_amount).label('total_bursary'),
            func.sum(StudentFee.total_amount_due).label('total_due'),
            func.sum(StudentFee.total_paid).label('total_paid'),
            func.sum(StudentFee.balance_due).label('total_balance')
        ).where(and_(*conditions))
        totals_result = await self.session.execute(totals_query)
        totals_row = totals_result.one()

        # By payment frequency
        frequency_query = select(
            StudentFee.payment_frequency,
            func.count(StudentFee.id).label('count'),
            func.sum(StudentFee.total_amount_due).label('total_amount')
        ).where(and_(*conditions)).group_by(StudentFee.payment_frequency)
        frequency_result = await self.session.execute(frequency_query)
        by_frequency = {
            row[0]: {"count": row[1], "total_amount": float(row[2] or 0)}
            for row in frequency_result
        }

        return {
            "total_student_fees": total_fees,
            "by_status": by_status,
            "total_before_discounts": float(totals_row[0] or 0),
            "total_discounts": float(totals_row[1] or 0),
            "total_bursary_amount": float(totals_row[2] or 0),
            "total_amount_due": float(totals_row[3] or 0),
            "total_paid": float(totals_row[4] or 0),
            "total_balance_due": float(totals_row[5] or 0),
            "collection_rate": (
                (float(totals_row[4] or 0) / float(totals_row[3] or 1)) * 100
                if totals_row[3] and totals_row[3] > 0 else 0
            ),
            "by_payment_frequency": by_frequency
        }

    async def mark_overdue(self, school_id: uuid.UUID) -> int:
        """
        Mark all pending/partial fees as overdue if past due date
        Returns count of fees marked as overdue
        """
        today = date.today()

        query = select(StudentFee).where(
            and_(
                StudentFee.school_id == school_id,
                StudentFee.status.in_(['pending', 'partial']),
                StudentFee.balance_due > 0,
                StudentFee.due_date < today,
                StudentFee.deleted_at.is_(None)
            )
        )

        result = await self.session.execute(query)
        fees = result.scalars().all()

        count = 0
        for fee in fees:
            fee.status = 'overdue'
            count += 1

        await self.session.flush()
        return count
