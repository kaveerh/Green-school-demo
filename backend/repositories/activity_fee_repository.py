"""
Activity Fee Repository

Data access layer for ActivityFee operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from models.activity_fee import ActivityFee
from models.activity import Activity
from models.school import School
from repositories.base_repository import BaseRepository
import uuid


class ActivityFeeRepository(BaseRepository[ActivityFee]):
    """Repository for ActivityFee data access"""

    def __init__(self, session: AsyncSession):
        super().__init__(ActivityFee, session)

    async def get_with_relationships(self, activity_fee_id: uuid.UUID) -> Optional[ActivityFee]:
        """Get activity fee with all relationships loaded"""
        query = select(ActivityFee).where(
            and_(
                ActivityFee.id == activity_fee_id,
                ActivityFee.deleted_at.is_(None)
            )
        ).options(
            selectinload(ActivityFee.activity),
            selectinload(ActivityFee.school)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_activity_and_year(
        self,
        activity_id: uuid.UUID,
        academic_year: str
    ) -> Optional[ActivityFee]:
        """Get fee for a specific activity and academic year"""
        query = select(ActivityFee).where(
            and_(
                ActivityFee.activity_id == activity_id,
                ActivityFee.academic_year == academic_year,
                ActivityFee.deleted_at.is_(None)
            )
        ).options(
            selectinload(ActivityFee.activity)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_activity(
        self,
        activity_id: uuid.UUID,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[ActivityFee], int]:
        """Get all fee structures for an activity"""
        offset = (page - 1) * limit

        conditions = [
            ActivityFee.activity_id == activity_id,
            ActivityFee.deleted_at.is_(None)
        ]

        if is_active is not None:
            conditions.append(ActivityFee.is_active == is_active)

        # Count query
        count_query = select(func.count(ActivityFee.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(ActivityFee).where(and_(*conditions)).options(
            selectinload(ActivityFee.activity)
        ).offset(offset).limit(limit).order_by(ActivityFee.academic_year.desc())

        result = await self.session.execute(query)
        activity_fees = result.scalars().all()

        return list(activity_fees), total

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None,
        fee_frequency: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[ActivityFee], int]:
        """Get activity fees for a school with optional filters"""
        offset = (page - 1) * limit

        conditions = [
            ActivityFee.school_id == school_id,
            ActivityFee.deleted_at.is_(None)
        ]

        if academic_year:
            conditions.append(ActivityFee.academic_year == academic_year)
        if fee_frequency:
            conditions.append(ActivityFee.fee_frequency == fee_frequency)
        if is_active is not None:
            conditions.append(ActivityFee.is_active == is_active)

        # Count query
        count_query = select(func.count(ActivityFee.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(ActivityFee).where(and_(*conditions)).options(
            selectinload(ActivityFee.activity),
            selectinload(ActivityFee.school)
        ).offset(offset).limit(limit).order_by(
            ActivityFee.academic_year.desc(),
            ActivityFee.fee_amount.desc()
        )

        result = await self.session.execute(query)
        activity_fees = result.scalars().all()

        return list(activity_fees), total

    async def get_active_for_year(
        self,
        school_id: uuid.UUID,
        academic_year: str
    ) -> List[ActivityFee]:
        """Get all active activity fees for a school and academic year"""
        query = select(ActivityFee).where(
            and_(
                ActivityFee.school_id == school_id,
                ActivityFee.academic_year == academic_year,
                ActivityFee.is_active == True,
                ActivityFee.deleted_at.is_(None)
            )
        ).options(
            selectinload(ActivityFee.activity)
        ).order_by(ActivityFee.fee_amount.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_frequency(
        self,
        school_id: uuid.UUID,
        fee_frequency: str,
        academic_year: str,
        is_active: bool = True
    ) -> List[ActivityFee]:
        """Get activity fees by frequency for a school and year"""
        query = select(ActivityFee).where(
            and_(
                ActivityFee.school_id == school_id,
                ActivityFee.fee_frequency == fee_frequency,
                ActivityFee.academic_year == academic_year,
                ActivityFee.is_active == is_active,
                ActivityFee.deleted_at.is_(None)
            )
        ).options(
            selectinload(ActivityFee.activity)
        ).order_by(ActivityFee.fee_amount.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def exists_for_activity_and_year(
        self,
        activity_id: uuid.UUID,
        academic_year: str,
        exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if activity fee exists for given activity and year"""
        conditions = [
            ActivityFee.activity_id == activity_id,
            ActivityFee.academic_year == academic_year,
            ActivityFee.deleted_at.is_(None)
        ]

        if exclude_id:
            conditions.append(ActivityFee.id != exclude_id)

        query = select(func.count(ActivityFee.id)).where(and_(*conditions))
        result = await self.session.execute(query)
        count = result.scalar()

        return count > 0

    async def get_total_fees_for_student_activities(
        self,
        student_id: uuid.UUID,
        academic_year: str,
        school_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Calculate total activity fees for a student based on their enrollments
        """
        from models.activity import ActivityEnrollment

        # Get student's activity enrollments
        enrollment_query = select(ActivityEnrollment).where(
            and_(
                ActivityEnrollment.student_id == student_id,
                ActivityEnrollment.status == 'active',
                ActivityEnrollment.deleted_at.is_(None)
            )
        ).options(
            selectinload(ActivityEnrollment.activity)
        )

        enrollment_result = await self.session.execute(enrollment_query)
        enrollments = enrollment_result.scalars().all()

        if not enrollments:
            return {
                "total_activity_fees": 0.0,
                "activity_count": 0,
                "activities": []
            }

        # Get activity IDs
        activity_ids = [enrollment.activity_id for enrollment in enrollments]

        # Get activity fees for these activities
        fee_query = select(ActivityFee).where(
            and_(
                ActivityFee.school_id == school_id,
                ActivityFee.activity_id.in_(activity_ids),
                ActivityFee.academic_year == academic_year,
                ActivityFee.is_active == True,
                ActivityFee.deleted_at.is_(None)
            )
        ).options(
            selectinload(ActivityFee.activity)
        )

        fee_result = await self.session.execute(fee_query)
        activity_fees = fee_result.scalars().all()

        # Calculate totals
        total = 0.0
        activities = []

        for fee in activity_fees:
            fee_amount = float(fee.fee_amount)
            total += fee_amount

            activities.append({
                "activity_id": str(fee.activity_id),
                "activity_name": fee.activity.name if fee.activity else "Unknown",
                "fee_amount": fee_amount,
                "fee_frequency": fee.fee_frequency,
                "annual_cost": float(fee.get_annual_cost())
            })

        return {
            "total_activity_fees": total,
            "activity_count": len(activities),
            "activities": activities
        }

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get activity fee statistics for a school"""
        conditions = [
            ActivityFee.school_id == school_id,
            ActivityFee.deleted_at.is_(None)
        ]

        if academic_year:
            conditions.append(ActivityFee.academic_year == academic_year)

        # Total activity fees
        total_query = select(func.count(ActivityFee.id)).where(and_(*conditions))
        total_result = await self.session.execute(total_query)
        total_fees = total_result.scalar()

        # Active fees
        active_query = select(func.count(ActivityFee.id)).where(
            and_(*conditions, ActivityFee.is_active == True)
        )
        active_result = await self.session.execute(active_query)
        active_fees = active_result.scalar()

        # By frequency
        frequency_query = select(
            ActivityFee.fee_frequency,
            func.count(ActivityFee.id).label('count'),
            func.avg(ActivityFee.fee_amount).label('avg_amount'),
            func.sum(ActivityFee.fee_amount).label('total_amount')
        ).where(and_(*conditions)).group_by(ActivityFee.fee_frequency)
        frequency_result = await self.session.execute(frequency_query)
        by_frequency = {
            row[0]: {
                "count": row[1],
                "average_amount": float(row[2] or 0),
                "total_amount": float(row[3] or 0)
            }
            for row in frequency_result
        }

        # Average fee amount
        avg_query = select(func.avg(ActivityFee.fee_amount)).where(and_(*conditions))
        avg_result = await self.session.execute(avg_query)
        average_fee = avg_result.scalar() or 0

        return {
            "total_activity_fees": total_fees,
            "active_activity_fees": active_fees,
            "average_fee_amount": float(average_fee),
            "by_frequency": by_frequency
        }
