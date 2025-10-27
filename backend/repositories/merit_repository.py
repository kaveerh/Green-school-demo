"""
Merit Repository

Data access layer for Merit operations with specialized queries.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from models.merit import Merit
from repositories.base_repository import BaseRepository
from datetime import date, timedelta
import uuid


class MeritRepository(BaseRepository[Merit]):
    """Repository for Merit data access"""

    def __init__(self, session: AsyncSession):
        super().__init__(Merit, session)

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        category: Optional[str] = None,
        quarter: Optional[str] = None,
        awarded_by_id: Optional[uuid.UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Merit], int]:
        """Get merits for a school with optional filters"""
        offset = (page - 1) * limit

        # Build base conditions
        conditions = [
            Merit.school_id == school_id,
            Merit.deleted_at.is_(None)
        ]

        if category:
            conditions.append(Merit.category == category)
        if quarter:
            conditions.append(Merit.quarter == quarter)
        if awarded_by_id:
            conditions.append(Merit.awarded_by_id == awarded_by_id)
        if start_date:
            conditions.append(Merit.awarded_date >= start_date)
        if end_date:
            conditions.append(Merit.awarded_date <= end_date)

        # Count query
        count_query = select(func.count(Merit.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Merit).where(and_(*conditions)).offset(offset).limit(limit).order_by(
            desc(Merit.awarded_date),
            desc(Merit.created_at)
        )

        result = await self.session.execute(query)
        merits = result.scalars().all()

        return list(merits), total

    async def get_by_student(
        self,
        student_id: uuid.UUID,
        category: Optional[str] = None,
        quarter: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Merit], int]:
        """Get merits for a student"""
        offset = (page - 1) * limit

        conditions = [
            Merit.student_id == student_id,
            Merit.deleted_at.is_(None)
        ]

        if category:
            conditions.append(Merit.category == category)
        if quarter:
            conditions.append(Merit.quarter == quarter)

        # Count query
        count_query = select(func.count(Merit.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Merit).where(and_(*conditions)).offset(offset).limit(limit).order_by(
            desc(Merit.awarded_date)
        )

        result = await self.session.execute(query)
        merits = result.scalars().all()

        return list(merits), total

    async def get_student_summary(self, student_id: uuid.UUID) -> Dict[str, Any]:
        """Get merit summary for a student"""
        conditions = [
            Merit.student_id == student_id,
            Merit.deleted_at.is_(None)
        ]

        # Total points
        total_query = select(func.sum(Merit.points)).where(and_(*conditions))
        total_result = await self.session.execute(total_query)
        total_points = total_result.scalar() or 0

        # By category
        category_query = select(
            Merit.category,
            func.sum(Merit.points).label('points'),
            func.count(Merit.id).label('count')
        ).where(and_(*conditions)).group_by(Merit.category)
        category_result = await self.session.execute(category_query)
        by_category = {row[0]: {'points': int(row[1]), 'count': row[2]} for row in category_result}

        # By quarter
        quarter_query = select(
            Merit.quarter,
            func.sum(Merit.points).label('points')
        ).where(and_(*conditions)).group_by(Merit.quarter)
        quarter_result = await self.session.execute(quarter_query)
        by_quarter = {row[0]: int(row[1]) for row in quarter_result if row[0]}

        # Recent merits
        recent_query = select(Merit).where(and_(*conditions)).order_by(
            desc(Merit.awarded_date)
        ).limit(5)
        recent_result = await self.session.execute(recent_query)
        recent_merits = list(recent_result.scalars().all())

        return {
            "total_points": int(total_points),
            "by_category": by_category,
            "by_quarter": by_quarter,
            "recent_merits": [m.to_dict(include_relationships=True) for m in recent_merits],
            "merit_count": len(recent_merits)
        }

    async def get_by_class(
        self,
        class_id: uuid.UUID,
        quarter: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Merit], int]:
        """Get merits for a class"""
        offset = (page - 1) * limit

        conditions = [
            Merit.class_id == class_id,
            Merit.deleted_at.is_(None)
        ]

        if quarter:
            conditions.append(Merit.quarter == quarter)
        if category:
            conditions.append(Merit.category == category)

        # Count query
        count_query = select(func.count(Merit.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Merit).where(and_(*conditions)).offset(offset).limit(limit).order_by(
            desc(Merit.awarded_date)
        )

        result = await self.session.execute(query)
        merits = result.scalars().all()

        return list(merits), total

    async def get_class_summary(self, class_id: uuid.UUID, quarter: Optional[str] = None) -> Dict[str, Any]:
        """Get class merit statistics"""
        conditions = [
            Merit.class_id == class_id,
            Merit.deleted_at.is_(None)
        ]

        if quarter:
            conditions.append(Merit.quarter == quarter)

        # Total points
        total_query = select(func.sum(Merit.points)).where(and_(*conditions))
        total_result = await self.session.execute(total_query)
        total_points = total_result.scalar() or 0

        # Count unique students
        students_query = select(func.count(func.distinct(Merit.student_id))).where(and_(*conditions))
        students_result = await self.session.execute(students_query)
        student_count = students_result.scalar() or 1

        # By category
        category_query = select(
            Merit.category,
            func.sum(Merit.points).label('points')
        ).where(and_(*conditions)).group_by(Merit.category)
        category_result = await self.session.execute(category_query)
        by_category = {row[0]: int(row[1]) for row in category_result}

        # Top students
        top_query = select(
            Merit.student_id,
            func.sum(Merit.points).label('total_points')
        ).where(and_(*conditions)).group_by(Merit.student_id).order_by(
            desc('total_points')
        ).limit(5)
        top_result = await self.session.execute(top_query)
        top_students = [{"student_id": str(row[0]), "total_points": int(row[1])} for row in top_result]

        return {
            "total_points": int(total_points),
            "average_per_student": round(float(total_points) / student_count, 2),
            "by_category": by_category,
            "top_students": top_students
        }

    async def get_by_teacher(
        self,
        teacher_id: uuid.UUID,
        quarter: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Merit], int]:
        """Get merits awarded by a teacher"""
        offset = (page - 1) * limit

        conditions = [
            Merit.awarded_by_id == teacher_id,
            Merit.deleted_at.is_(None)
        ]

        if quarter:
            conditions.append(Merit.quarter == quarter)

        # Count query
        count_query = select(func.count(Merit.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Merit).where(and_(*conditions)).offset(offset).limit(limit).order_by(
            desc(Merit.awarded_date)
        )

        result = await self.session.execute(query)
        merits = result.scalars().all()

        return list(merits), total

    async def get_leaderboard(
        self,
        school_id: uuid.UUID,
        grade_level: Optional[int] = None,
        quarter: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get merit leaderboard"""
        # Import here to avoid circular dependency
        from models.student import Student

        conditions = [
            Merit.school_id == school_id,
            Merit.deleted_at.is_(None)
        ]

        if quarter:
            conditions.append(Merit.quarter == quarter)

        # Build query with student join for grade filtering
        query = select(
            Merit.student_id,
            func.sum(Merit.points).label('total_points'),
            func.count(Merit.id).label('merit_count')
        ).where(and_(*conditions))

        if grade_level:
            query = query.join(Student, Student.id == Merit.student_id).where(
                Student.grade_level == grade_level
            )

        query = query.group_by(Merit.student_id).order_by(desc('total_points')).limit(limit)

        result = await self.session.execute(query)
        leaderboard = [
            {
                "student_id": str(row[0]),
                "total_points": int(row[1]),
                "merit_count": row[2],
                "rank": idx + 1
            }
            for idx, row in enumerate(result)
        ]

        return leaderboard

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        quarter: Optional[str] = None,
        grade_level: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get school-wide merit statistics"""
        from models.student import Student

        conditions = [
            Merit.school_id == school_id,
            Merit.deleted_at.is_(None)
        ]

        if quarter:
            conditions.append(Merit.quarter == quarter)

        # Total merits and points
        total_query = select(
            func.count(Merit.id).label('total_merits'),
            func.sum(Merit.points).label('total_points')
        ).where(and_(*conditions))

        if grade_level:
            total_query = total_query.join(Student, Student.id == Merit.student_id).where(
                Student.grade_level == grade_level
            )

        total_result = await self.session.execute(total_query)
        totals = total_result.one()

        # By category
        category_query = select(
            Merit.category,
            func.count(Merit.id).label('count'),
            func.sum(Merit.points).label('points')
        ).where(and_(*conditions)).group_by(Merit.category)

        category_result = await self.session.execute(category_query)
        by_category = {row[0]: {'count': row[1], 'points': int(row[2])} for row in category_result}

        # By quarter (if not filtering by quarter)
        by_quarter = {}
        if not quarter:
            quarter_query = select(
                Merit.quarter,
                func.sum(Merit.points).label('points')
            ).where(and_(*conditions)).group_by(Merit.quarter)
            quarter_result = await self.session.execute(quarter_query)
            by_quarter = {row[0]: int(row[1]) for row in quarter_result if row[0]}

        # Unique students
        students_query = select(func.count(func.distinct(Merit.student_id))).where(and_(*conditions))
        students_result = await self.session.execute(students_query)
        unique_students = students_result.scalar() or 1

        return {
            "total_merits": totals[0] or 0,
            "total_points": int(totals[1] or 0),
            "by_category": by_category,
            "by_quarter": by_quarter,
            "unique_students": unique_students,
            "average_per_student": round(float(totals[1] or 0) / unique_students, 2)
        }

    async def create_batch(
        self,
        merits_data: List[Dict[str, Any]],
        batch_id: uuid.UUID
    ) -> List[Merit]:
        """Create multiple merits in a batch (for class awards)"""
        merits = []
        for merit_data in merits_data:
            merit_data['batch_id'] = batch_id
            merit_data['is_class_award'] = True
            merit = await self.create(merit_data)
            merits.append(merit)

        return merits
