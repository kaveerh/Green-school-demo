"""
Student Repository
Data access layer for student operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, delete as sql_delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from datetime import date
import uuid

from models.student import Student, ParentStudentRelationship
from repositories.base_repository import BaseRepository


class StudentRepository(BaseRepository[Student]):
    """Repository for student data access"""

    def __init__(self, db: AsyncSession):
        super().__init__(Student, db)

    async def get_by_student_id(self, school_id: uuid.UUID, student_id: str) -> Optional[Student]:
        """Get student by student_id within a school"""
        query = select(Student).where(
            and_(
                Student.school_id == school_id,
                Student.student_id == student_id,
                Student.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Student]:
        """Get student by user_id"""
        query = select(Student).where(
            and_(
                Student.user_id == user_id,
                Student.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_grade_level(
        self,
        school_id: uuid.UUID,
        grade_level: int,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Student], dict]:
        """Get students by grade level with pagination"""
        offset = (page - 1) * limit

        # Count query
        count_query = select(func.count(Student.id)).where(
            and_(
                Student.school_id == school_id,
                Student.grade_level == grade_level,
                Student.deleted_at.is_(None)
            )
        )
        total = await self.session.scalar(count_query)

        # Data query
        query = select(Student).where(
            and_(
                Student.school_id == school_id,
                Student.grade_level == grade_level,
                Student.deleted_at.is_(None)
            )
        ).offset(offset).limit(limit).order_by(Student.created_at.desc())

        result = await self.session.execute(query)
        students = result.scalars().all()

        return students, {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }

    async def get_enrolled_students(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Student], dict]:
        """Get all currently enrolled students"""
        offset = (page - 1) * limit

        # Count query
        count_query = select(func.count(Student.id)).where(
            and_(
                Student.school_id == school_id,
                Student.status == "enrolled",
                Student.deleted_at.is_(None)
            )
        )
        total = await self.session.scalar(count_query)

        # Data query
        query = select(Student).where(
            and_(
                Student.school_id == school_id,
                Student.status == "enrolled",
                Student.deleted_at.is_(None)
            )
        ).offset(offset).limit(limit).order_by(Student.grade_level, Student.student_id)

        result = await self.session.execute(query)
        students = result.scalars().all()

        return students, {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }

    async def search_students(
        self,
        school_id: uuid.UUID,
        search: Optional[str] = None,
        grade_level: Optional[int] = None,
        status: Optional[str] = None,
        gender: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        sort: str = "created_at",
        order: str = "desc"
    ) -> Tuple[List[Student], dict]:
        """Search students with filters and pagination"""
        offset = (page - 1) * limit

        # Build base conditions
        conditions = [
            Student.school_id == school_id,
            Student.deleted_at.is_(None)
        ]

        # Add search condition
        if search:
            conditions.append(
                or_(
                    Student.student_id.ilike(f"%{search}%"),
                    # Note: Would need to join with users table to search by name
                )
            )

        # Add filter conditions
        if grade_level is not None:
            conditions.append(Student.grade_level == grade_level)
        if status:
            conditions.append(Student.status == status)
        if gender:
            conditions.append(Student.gender == gender)

        # Count query
        count_query = select(func.count(Student.id)).where(and_(*conditions))
        total = await self.session.scalar(count_query)

        # Data query with sorting
        query = select(Student).where(and_(*conditions))

        # Apply sorting
        if hasattr(Student, sort):
            order_column = getattr(Student, sort)
            if order == "asc":
                query = query.order_by(order_column.asc())
            else:
                query = query.order_by(order_column.desc())
        else:
            query = query.order_by(Student.created_at.desc())

        # Eagerly load user relationship
        query = query.options(selectinload(Student.user))
        query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)
        students = result.scalars().all()

        return students, {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }

    async def get_statistics(self, school_id: uuid.UUID) -> dict:
        """Get student statistics for a school"""
        # Total students
        total_query = select(func.count(Student.id)).where(
            and_(
                Student.school_id == school_id,
                Student.deleted_at.is_(None)
            )
        )
        total = await self.session.scalar(total_query)

        # By status
        status_query = select(
            Student.status,
            func.count(Student.id)
        ).where(
            and_(
                Student.school_id == school_id,
                Student.deleted_at.is_(None)
            )
        ).group_by(Student.status)

        status_result = await self.session.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result}

        # By grade level
        grade_query = select(
            Student.grade_level,
            func.count(Student.id)
        ).where(
            and_(
                Student.school_id == school_id,
                Student.deleted_at.is_(None)
            )
        ).group_by(Student.grade_level)

        grade_result = await self.session.execute(grade_query)
        by_grade = {f"grade_{row[0]}": row[1] for row in grade_result}

        # By gender
        gender_query = select(
            Student.gender,
            func.count(Student.id)
        ).where(
            and_(
                Student.school_id == school_id,
                Student.deleted_at.is_(None)
            )
        ).group_by(Student.gender)

        gender_result = await self.session.execute(gender_query)
        by_gender = {row[0] or "not_specified": row[1] for row in gender_result}

        # Currently enrolled
        enrolled_query = select(func.count(Student.id)).where(
            and_(
                Student.school_id == school_id,
                Student.status == "enrolled",
                Student.deleted_at.is_(None)
            )
        )
        enrolled = await self.session.scalar(enrolled_query)

        return {
            "total": total,
            "by_status": by_status,
            "by_grade_level": by_grade,
            "by_gender": by_gender,
            "currently_enrolled": enrolled,
            "average_age": 0  # Would need to calculate from date_of_birth
        }


class ParentStudentRelationshipRepository(BaseRepository[ParentStudentRelationship]):
    """Repository for parent-student relationship data access"""

    def __init__(self, db: AsyncSession):
        super().__init__(ParentStudentRelationship, db)

    async def get_by_student(self, student_id: uuid.UUID) -> List[ParentStudentRelationship]:
        """Get all parent relationships for a student"""
        query = select(ParentStudentRelationship).where(
            and_(
                ParentStudentRelationship.student_id == student_id,
                ParentStudentRelationship.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_parent(self, parent_id: uuid.UUID) -> List[ParentStudentRelationship]:
        """Get all children for a parent"""
        query = select(ParentStudentRelationship).where(
            and_(
                ParentStudentRelationship.parent_id == parent_id,
                ParentStudentRelationship.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_relationship(
        self,
        parent_id: uuid.UUID,
        student_id: uuid.UUID
    ) -> Optional[ParentStudentRelationship]:
        """Get specific parent-student relationship"""
        query = select(ParentStudentRelationship).where(
            and_(
                ParentStudentRelationship.parent_id == parent_id,
                ParentStudentRelationship.student_id == student_id,
                ParentStudentRelationship.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_primary_contact(self, student_id: uuid.UUID) -> Optional[ParentStudentRelationship]:
        """Get primary contact for a student"""
        query = select(ParentStudentRelationship).where(
            and_(
                ParentStudentRelationship.student_id == student_id,
                ParentStudentRelationship.is_primary_contact == True,
                ParentStudentRelationship.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def unlink_parent(self, parent_id: uuid.UUID, student_id: uuid.UUID) -> bool:
        """Remove parent-student relationship (soft delete)"""
        relationship = await self.get_relationship(parent_id, student_id)
        if relationship:
            await self.delete(relationship.id)
            return True
        return False
