"""
Assessment Repository

Data access layer for Assessment operations with specialized queries.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from models.assessment import Assessment
from models.student import Student
from models.teacher import Teacher
from models.subject import Subject
from models.class_model import Class
from models.user import User
from repositories.base_repository import BaseRepository
import uuid


class AssessmentRepository(BaseRepository[Assessment]):
    """Repository for Assessment data access"""

    def __init__(self, session: AsyncSession):
        super().__init__(Assessment, session)

    async def get_with_relationships(self, assessment_id: uuid.UUID) -> Optional[Assessment]:
        """Get assessment with all relationships loaded"""
        query = select(Assessment).where(
            and_(
                Assessment.id == assessment_id,
                Assessment.deleted_at.is_(None)
            )
        ).options(
            selectinload(Assessment.student).selectinload(Student.user),
            selectinload(Assessment.teacher).selectinload(Teacher.user),
            selectinload(Assessment.subject),
            selectinload(Assessment.class_obj),
            selectinload(Assessment.school)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_student(
        self,
        student_id: uuid.UUID,
        quarter: Optional[str] = None,
        subject_id: Optional[uuid.UUID] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Assessment], int]:
        """Get assessments for a student with optional filters"""
        offset = (page - 1) * limit

        # Build base conditions
        conditions = [
            Assessment.student_id == student_id,
            Assessment.deleted_at.is_(None)
        ]

        if quarter:
            conditions.append(Assessment.quarter == quarter)
        if subject_id:
            conditions.append(Assessment.subject_id == subject_id)

        # Count query
        count_query = select(func.count(Assessment.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Assessment).where(and_(*conditions)).options(
            selectinload(Assessment.subject),
            selectinload(Assessment.teacher).selectinload(Teacher.user)
        ).offset(offset).limit(limit).order_by(desc(Assessment.assessment_date))

        result = await self.session.execute(query)
        assessments = result.scalars().all()

        return list(assessments), total

    async def get_by_class(
        self,
        class_id: uuid.UUID,
        quarter: Optional[str] = None,
        assessment_type: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Assessment], int]:
        """Get assessments for a class with optional filters"""
        offset = (page - 1) * limit

        conditions = [
            Assessment.class_id == class_id,
            Assessment.deleted_at.is_(None)
        ]

        if quarter:
            conditions.append(Assessment.quarter == quarter)
        if assessment_type:
            conditions.append(Assessment.assessment_type == assessment_type)

        # Count query
        count_query = select(func.count(Assessment.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Assessment).where(and_(*conditions)).options(
            selectinload(Assessment.student).selectinload(Student.user)
        ).offset(offset).limit(limit).order_by(desc(Assessment.assessment_date))

        result = await self.session.execute(query)
        assessments = result.scalars().all()

        return list(assessments), total

    async def get_by_teacher(
        self,
        teacher_id: uuid.UUID,
        quarter: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Assessment], int]:
        """Get assessments for a teacher with optional filters"""
        offset = (page - 1) * limit

        conditions = [
            Assessment.teacher_id == teacher_id,
            Assessment.deleted_at.is_(None)
        ]

        if quarter:
            conditions.append(Assessment.quarter == quarter)
        if status:
            conditions.append(Assessment.status == status)

        # Count query
        count_query = select(func.count(Assessment.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Assessment).where(and_(*conditions)).options(
            selectinload(Assessment.student).selectinload(Student.user),
            selectinload(Assessment.class_obj),
            selectinload(Assessment.subject)
        ).offset(offset).limit(limit).order_by(desc(Assessment.assessment_date))

        result = await self.session.execute(query)
        assessments = result.scalars().all()

        return list(assessments), total

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        quarter: Optional[str] = None,
        grade_level: Optional[int] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Assessment], int]:
        """Get assessments for a school with optional filters"""
        offset = (page - 1) * limit

        conditions = [
            Assessment.school_id == school_id,
            Assessment.deleted_at.is_(None)
        ]

        if quarter:
            conditions.append(Assessment.quarter == quarter)

        # If grade_level filter, join with class
        if grade_level:
            query_base = select(Assessment).join(Class, Assessment.class_id == Class.id).where(
                and_(*conditions, Class.grade_level == grade_level)
            )
        else:
            query_base = select(Assessment).where(and_(*conditions))

        # Count query
        count_query = select(func.count()).select_from(query_base.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = query_base.options(
            selectinload(Assessment.student).selectinload(Student.user),
            selectinload(Assessment.subject)
        ).offset(offset).limit(limit).order_by(desc(Assessment.assessment_date))

        result = await self.session.execute(query)
        assessments = result.scalars().all()

        return list(assessments), total

    async def get_statistics(self, school_id: uuid.UUID, quarter: Optional[str] = None) -> Dict[str, Any]:
        """Get assessment statistics for a school"""
        conditions = [
            Assessment.school_id == school_id,
            Assessment.deleted_at.is_(None)
        ]

        if quarter:
            conditions.append(Assessment.quarter == quarter)

        # Total assessments
        total_query = select(func.count(Assessment.id)).where(and_(*conditions))
        total_result = await self.session.execute(total_query)
        total_assessments = total_result.scalar()

        # Graded assessments
        graded_query = select(func.count(Assessment.id)).where(
            and_(*conditions, Assessment.status.in_(['graded', 'returned']))
        )
        graded_result = await self.session.execute(graded_query)
        graded_assessments = graded_result.scalar()

        # Pending assessments
        pending_query = select(func.count(Assessment.id)).where(
            and_(*conditions, Assessment.status == 'pending')
        )
        pending_result = await self.session.execute(pending_query)
        pending_assessments = pending_result.scalar()

        # Average percentage (only graded)
        avg_query = select(func.avg(Assessment.percentage)).where(
            and_(*conditions, Assessment.percentage.isnot(None))
        )
        avg_result = await self.session.execute(avg_query)
        average_score = avg_result.scalar() or 0

        # By assessment type
        type_query = select(
            Assessment.assessment_type,
            func.count(Assessment.id).label('count')
        ).where(and_(*conditions)).group_by(Assessment.assessment_type)
        type_result = await self.session.execute(type_query)
        by_type = {row[0]: row[1] for row in type_result}

        return {
            "total_assessments": total_assessments,
            "graded_assessments": graded_assessments,
            "pending_assessments": pending_assessments,
            "average_score": float(average_score) if average_score else 0.0,
            "by_type": by_type
        }
