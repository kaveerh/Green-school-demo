"""
Activity Repository

Data access layer for Activity and ActivityEnrollment operations with specialized queries.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, any_
from sqlalchemy.orm import selectinload
from models.activity import Activity, ActivityEnrollment
from models.student import Student
from models.user import User
from repositories.base_repository import BaseRepository
from datetime import date
import uuid


class ActivityRepository(BaseRepository[Activity]):
    """Repository for Activity data access"""

    def __init__(self, session: AsyncSession):
        super().__init__(Activity, session)

    async def get_with_relationships(self, activity_id: uuid.UUID) -> Optional[Activity]:
        """Get activity with all relationships loaded"""
        query = select(Activity).where(
            and_(
                Activity.id == activity_id,
                Activity.deleted_at.is_(None)
            )
        ).options(
            selectinload(Activity.coordinator),
            selectinload(Activity.room),
            selectinload(Activity.school),
            selectinload(Activity.enrollments)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        activity_type: Optional[str] = None,
        status: Optional[str] = None,
        grade_level: Optional[int] = None,
        registration_open: Optional[bool] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Activity], int]:
        """Get activities for a school with optional filters"""
        offset = (page - 1) * limit

        # Build base conditions
        conditions = [
            Activity.school_id == school_id,
            Activity.deleted_at.is_(None)
        ]

        if activity_type:
            conditions.append(Activity.activity_type == activity_type)
        if status:
            conditions.append(Activity.status == status)
        if grade_level:
            conditions.append(Activity.grade_levels.contains([grade_level]))
        if registration_open is not None:
            conditions.append(Activity.registration_open == registration_open)

        # Count query
        count_query = select(func.count(Activity.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Activity).where(and_(*conditions)).options(
            selectinload(Activity.coordinator),
            selectinload(Activity.room)
        ).offset(offset).limit(limit).order_by(desc(Activity.is_featured), asc(Activity.name))

        result = await self.session.execute(query)
        activities = result.scalars().all()

        return list(activities), total

    async def get_by_type(
        self,
        school_id: uuid.UUID,
        activity_type: str,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Activity], int]:
        """Get activities by type"""
        offset = (page - 1) * limit

        conditions = [
            Activity.school_id == school_id,
            Activity.activity_type == activity_type,
            Activity.deleted_at.is_(None)
        ]

        # Count query
        count_query = select(func.count(Activity.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Activity).where(and_(*conditions)).options(
            selectinload(Activity.coordinator),
            selectinload(Activity.room)
        ).offset(offset).limit(limit).order_by(asc(Activity.name))

        result = await self.session.execute(query)
        activities = result.scalars().all()

        return list(activities), total

    async def get_by_coordinator(
        self,
        coordinator_id: uuid.UUID,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Activity], int]:
        """Get activities coordinated by a specific user"""
        offset = (page - 1) * limit

        conditions = [
            Activity.school_id == school_id,
            Activity.coordinator_id == coordinator_id,
            Activity.deleted_at.is_(None)
        ]

        # Count query
        count_query = select(func.count(Activity.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Activity).where(and_(*conditions)).options(
            selectinload(Activity.room),
            selectinload(Activity.enrollments)
        ).offset(offset).limit(limit).order_by(desc(Activity.created_at))

        result = await self.session.execute(query)
        activities = result.scalars().all()

        return list(activities), total

    async def get_by_grade_level(
        self,
        school_id: uuid.UUID,
        grade_level: int,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Activity], int]:
        """Get activities available for a specific grade level"""
        offset = (page - 1) * limit

        conditions = [
            Activity.school_id == school_id,
            Activity.grade_levels.contains([grade_level]),
            Activity.status == 'active',
            Activity.deleted_at.is_(None)
        ]

        # Count query
        count_query = select(func.count(Activity.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Activity).where(and_(*conditions)).options(
            selectinload(Activity.coordinator),
            selectinload(Activity.room)
        ).offset(offset).limit(limit).order_by(desc(Activity.is_featured), asc(Activity.name))

        result = await self.session.execute(query)
        activities = result.scalars().all()

        return list(activities), total

    async def get_featured(
        self,
        school_id: uuid.UUID,
        limit: int = 10
    ) -> List[Activity]:
        """Get featured activities for a school"""
        conditions = [
            Activity.school_id == school_id,
            Activity.is_featured == True,
            Activity.status == 'active',
            Activity.deleted_at.is_(None)
        ]

        query = select(Activity).where(and_(*conditions)).options(
            selectinload(Activity.coordinator),
            selectinload(Activity.room)
        ).limit(limit).order_by(asc(Activity.name))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search(
        self,
        school_id: uuid.UUID,
        query_text: str,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Activity], int]:
        """Search activities by name or description"""
        offset = (page - 1) * limit
        search_pattern = f"%{query_text}%"

        conditions = [
            Activity.school_id == school_id,
            or_(
                Activity.name.ilike(search_pattern),
                Activity.description.ilike(search_pattern),
                Activity.category.ilike(search_pattern)
            ),
            Activity.deleted_at.is_(None)
        ]

        # Count query
        count_query = select(func.count(Activity.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Activity).where(and_(*conditions)).options(
            selectinload(Activity.coordinator),
            selectinload(Activity.room)
        ).offset(offset).limit(limit).order_by(asc(Activity.name))

        result = await self.session.execute(query)
        activities = result.scalars().all()

        return list(activities), total

    async def get_by_code(
        self,
        school_id: uuid.UUID,
        code: str
    ) -> Optional[Activity]:
        """Get activity by code"""
        conditions = [
            Activity.school_id == school_id,
            Activity.code == code,
            Activity.deleted_at.is_(None)
        ]

        query = select(Activity).where(and_(*conditions)).options(
            selectinload(Activity.coordinator),
            selectinload(Activity.room),
            selectinload(Activity.enrollments)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_statistics(
        self,
        school_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get activity statistics for a school"""
        conditions = [
            Activity.school_id == school_id,
            Activity.deleted_at.is_(None)
        ]

        # Total activities
        total_query = select(func.count(Activity.id)).where(and_(*conditions))
        total_result = await self.session.execute(total_query)
        total_activities = total_result.scalar()

        # By type
        type_query = select(
            Activity.activity_type,
            func.count(Activity.id).label('count')
        ).where(and_(*conditions)).group_by(Activity.activity_type)
        type_result = await self.session.execute(type_query)
        by_type = {row[0]: row[1] for row in type_result}

        # By status
        status_query = select(
            Activity.status,
            func.count(Activity.id).label('count')
        ).where(and_(*conditions)).group_by(Activity.status)
        status_result = await self.session.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result}

        # Total enrollments
        enrollment_query = select(func.count(ActivityEnrollment.id)).join(
            Activity, ActivityEnrollment.activity_id == Activity.id
        ).where(
            and_(
                Activity.school_id == school_id,
                ActivityEnrollment.status == 'active',
                Activity.deleted_at.is_(None)
            )
        )
        enrollment_result = await self.session.execute(enrollment_query)
        total_enrollments = enrollment_result.scalar()

        # Average enrollment per activity
        avg_enrollment = total_enrollments / total_activities if total_activities > 0 else 0

        # Total revenue (sum of all payments)
        revenue_query = select(func.sum(ActivityEnrollment.amount_paid)).join(
            Activity, ActivityEnrollment.activity_id == Activity.id
        ).where(
            and_(
                Activity.school_id == school_id,
                Activity.deleted_at.is_(None)
            )
        )
        revenue_result = await self.session.execute(revenue_query)
        total_revenue = float(revenue_result.scalar() or 0)

        # Outstanding payments
        outstanding_query = select(func.count(ActivityEnrollment.id)).join(
            Activity, ActivityEnrollment.activity_id == Activity.id
        ).where(
            and_(
                Activity.school_id == school_id,
                ActivityEnrollment.payment_status.in_(['pending', 'partial']),
                Activity.deleted_at.is_(None)
            )
        )
        outstanding_result = await self.session.execute(outstanding_query)
        total_outstanding = outstanding_result.scalar()

        return {
            "total_activities": total_activities,
            "by_type": by_type,
            "by_status": by_status,
            "total_enrollments": total_enrollments,
            "average_enrollment_per_activity": round(avg_enrollment, 2),
            "total_revenue": total_revenue,
            "total_outstanding": total_outstanding
        }


class ActivityEnrollmentRepository(BaseRepository[ActivityEnrollment]):
    """Repository for ActivityEnrollment data access"""

    def __init__(self, session: AsyncSession):
        super().__init__(ActivityEnrollment, session)

    async def get_with_relationships(self, enrollment_id: uuid.UUID) -> Optional[ActivityEnrollment]:
        """Get enrollment with all relationships loaded"""
        query = select(ActivityEnrollment).where(
            ActivityEnrollment.id == enrollment_id
        ).options(
            selectinload(ActivityEnrollment.activity),
            selectinload(ActivityEnrollment.student)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_activity(
        self,
        activity_id: uuid.UUID,
        status: Optional[str] = None,
        payment_status: Optional[str] = None
    ) -> List[ActivityEnrollment]:
        """Get all enrollments for an activity"""
        conditions = [
            ActivityEnrollment.activity_id == activity_id
        ]

        if status:
            conditions.append(ActivityEnrollment.status == status)
        if payment_status:
            conditions.append(ActivityEnrollment.payment_status == payment_status)

        query = select(ActivityEnrollment).where(and_(*conditions)).options(
            selectinload(ActivityEnrollment.student)
        ).order_by(asc(ActivityEnrollment.enrollment_date))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_student(
        self,
        student_id: uuid.UUID,
        status: Optional[str] = None
    ) -> List[ActivityEnrollment]:
        """Get all activities a student is enrolled in"""
        conditions = [
            ActivityEnrollment.student_id == student_id
        ]

        if status:
            conditions.append(ActivityEnrollment.status == status)

        query = select(ActivityEnrollment).where(and_(*conditions)).options(
            selectinload(ActivityEnrollment.activity)
        ).order_by(desc(ActivityEnrollment.enrollment_date))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def check_enrollment_exists(
        self,
        activity_id: uuid.UUID,
        student_id: uuid.UUID
    ) -> Optional[ActivityEnrollment]:
        """Check if a student is already enrolled in an activity"""
        query = select(ActivityEnrollment).where(
            and_(
                ActivityEnrollment.activity_id == activity_id,
                ActivityEnrollment.student_id == student_id
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_pending_payments(
        self,
        activity_id: Optional[uuid.UUID] = None,
        school_id: Optional[uuid.UUID] = None
    ) -> List[ActivityEnrollment]:
        """Get enrollments with pending payments"""
        conditions = [
            ActivityEnrollment.payment_status.in_(['pending', 'partial'])
        ]

        if activity_id:
            conditions.append(ActivityEnrollment.activity_id == activity_id)

        if school_id:
            query = select(ActivityEnrollment).join(
                Activity, ActivityEnrollment.activity_id == Activity.id
            ).where(
                and_(
                    Activity.school_id == school_id,
                    *conditions
                )
            ).options(
                selectinload(ActivityEnrollment.student),
                selectinload(ActivityEnrollment.activity)
            )
        else:
            query = select(ActivityEnrollment).where(and_(*conditions)).options(
                selectinload(ActivityEnrollment.student),
                selectinload(ActivityEnrollment.activity)
            )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_without_consent(
        self,
        activity_id: Optional[uuid.UUID] = None,
        school_id: Optional[uuid.UUID] = None
    ) -> List[ActivityEnrollment]:
        """Get enrollments missing parent consent"""
        conditions = [
            ActivityEnrollment.parent_consent == False,
            ActivityEnrollment.status == 'active'
        ]

        if activity_id:
            conditions.append(ActivityEnrollment.activity_id == activity_id)

        if school_id:
            query = select(ActivityEnrollment).join(
                Activity, ActivityEnrollment.activity_id == Activity.id
            ).where(
                and_(
                    Activity.school_id == school_id,
                    *conditions
                )
            ).options(
                selectinload(ActivityEnrollment.student),
                selectinload(ActivityEnrollment.activity)
            )
        else:
            query = select(ActivityEnrollment).where(and_(*conditions)).options(
                selectinload(ActivityEnrollment.student),
                selectinload(ActivityEnrollment.activity)
            )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_waitlisted(
        self,
        activity_id: uuid.UUID
    ) -> List[ActivityEnrollment]:
        """Get waitlisted enrollments for an activity"""
        conditions = [
            ActivityEnrollment.activity_id == activity_id,
            ActivityEnrollment.status == 'waitlisted'
        ]

        query = select(ActivityEnrollment).where(and_(*conditions)).options(
            selectinload(ActivityEnrollment.student)
        ).order_by(asc(ActivityEnrollment.enrollment_date))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_active_enrollments(
        self,
        activity_id: uuid.UUID
    ) -> int:
        """Count active enrollments for an activity"""
        query = select(func.count(ActivityEnrollment.id)).where(
            and_(
                ActivityEnrollment.activity_id == activity_id,
                ActivityEnrollment.status == 'active'
            )
        )

        result = await self.session.execute(query)
        return result.scalar()
