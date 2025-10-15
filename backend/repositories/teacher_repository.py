"""
Teacher Repository
Data access layer for teacher operations
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from repositories.base_repository import BaseRepository
from models.teacher import Teacher
import uuid


class TeacherRepository(BaseRepository[Teacher]):
    """Repository for teacher data access"""

    def __init__(self, session: AsyncSession):
        """
        Initialize teacher repository

        Args:
            session: Async database session
        """
        super().__init__(Teacher, session)

    async def find_by_user_id(
        self,
        user_id: uuid.UUID,
        include_deleted: bool = False
    ) -> Optional[Teacher]:
        """
        Find teacher by user ID

        Args:
            user_id: User UUID
            include_deleted: Whether to include soft-deleted records

        Returns:
            Teacher instance or None
        """
        query = select(self.model).where(self.model.user_id == user_id)

        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_by_employee_id(
        self,
        school_id: uuid.UUID,
        employee_id: str,
        include_deleted: bool = False
    ) -> Optional[Teacher]:
        """
        Find teacher by employee ID within a school

        Args:
            school_id: School UUID
            employee_id: Employee ID
            include_deleted: Whether to include soft-deleted records

        Returns:
            Teacher instance or None
        """
        query = select(self.model).where(
            and_(
                self.model.school_id == school_id,
                self.model.employee_id == employee_id
            )
        )

        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_by_school(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False
    ) -> tuple[List[Teacher], int]:
        """
        Find all teachers in a school with filters

        Args:
            school_id: School UUID
            page: Page number
            limit: Items per page
            filters: Additional filters
            include_deleted: Whether to include soft-deleted records

        Returns:
            Tuple of (teachers list, total count)
        """
        query = select(self.model).where(self.model.school_id == school_id)

        # Apply additional filters
        if filters:
            query = self._apply_filters(query, filters)

        # Exclude soft-deleted records
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * limit
        query = query.order_by(self.model.created_at.desc())
        query = query.offset(offset).limit(limit)

        # Execute query
        result = await self.session.execute(query)
        teachers = result.scalars().all()

        return list(teachers), total

    async def search_teachers(
        self,
        school_id: uuid.UUID,
        search_term: str,
        page: int = 1,
        limit: int = 20,
        include_deleted: bool = False
    ) -> tuple[List[Teacher], int]:
        """
        Search teachers by employee ID, department, or specialization

        Args:
            school_id: School UUID
            search_term: Search term
            page: Page number
            limit: Items per page
            include_deleted: Whether to include soft-deleted records

        Returns:
            Tuple of (teachers list, total count)
        """
        search_pattern = f"%{search_term}%"

        query = select(self.model).where(
            and_(
                self.model.school_id == school_id,
                or_(
                    self.model.employee_id.ilike(search_pattern),
                    self.model.department.ilike(search_pattern),
                    self.model.job_title.ilike(search_pattern)
                )
            )
        )

        # Exclude soft-deleted records
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * limit
        query = query.order_by(self.model.created_at.desc())
        query = query.offset(offset).limit(limit)

        # Execute query
        result = await self.session.execute(query)
        teachers = result.scalars().all()

        return list(teachers), total

    async def find_by_grade(
        self,
        school_id: uuid.UUID,
        grade: int,
        include_deleted: bool = False
    ) -> List[Teacher]:
        """
        Find all teachers who teach a specific grade

        Args:
            school_id: School UUID
            grade: Grade level (1-7)
            include_deleted: Whether to include soft-deleted records

        Returns:
            List of teachers
        """
        # Use PostgreSQL array contains operator
        query = select(self.model).where(
            and_(
                self.model.school_id == school_id,
                self.model.grade_levels.contains([grade])
            )
        )

        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def find_by_specialization(
        self,
        school_id: uuid.UUID,
        specialization: str,
        include_deleted: bool = False
    ) -> List[Teacher]:
        """
        Find all teachers with a specific specialization

        Args:
            school_id: School UUID
            specialization: Specialization (e.g., "MATH", "ELA")
            include_deleted: Whether to include soft-deleted records

        Returns:
            List of teachers
        """
        query = select(self.model).where(
            and_(
                self.model.school_id == school_id,
                self.model.specializations.contains([specialization])
            )
        )

        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def find_active_teachers(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 20
    ) -> tuple[List[Teacher], int]:
        """
        Find all active teachers in a school

        Args:
            school_id: School UUID
            page: Page number
            limit: Items per page

        Returns:
            Tuple of (teachers list, total count)
        """
        filters = {
            'school_id': school_id,
            'status': 'active',
            'is_active': True
        }

        return await self.find_all(
            filters=filters,
            page=page,
            limit=limit,
            include_deleted=False
        )

    async def employee_id_exists(
        self,
        school_id: uuid.UUID,
        employee_id: str,
        exclude_teacher_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if employee ID exists in school

        Args:
            school_id: School UUID
            employee_id: Employee ID to check
            exclude_teacher_id: Teacher ID to exclude from check (for updates)

        Returns:
            True if exists, False otherwise
        """
        query = select(self.model).where(
            and_(
                self.model.school_id == school_id,
                self.model.employee_id == employee_id,
                self.model.deleted_at.is_(None)
            )
        )

        if exclude_teacher_id:
            query = query.where(self.model.id != exclude_teacher_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def count_by_department(
        self,
        school_id: uuid.UUID
    ) -> Dict[str, int]:
        """
        Count teachers by department

        Args:
            school_id: School UUID

        Returns:
            Dictionary of department counts
        """
        query = select(
            self.model.department,
            func.count(self.model.id).label('count')
        ).where(
            and_(
                self.model.school_id == school_id,
                self.model.deleted_at.is_(None)
            )
        ).group_by(self.model.department)

        result = await self.session.execute(query)
        rows = result.all()

        return {row.department or 'Unassigned': row.count for row in rows}

    async def get_statistics(
        self,
        school_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Get teacher statistics for a school

        Args:
            school_id: School UUID

        Returns:
            Dictionary of statistics
        """
        # Total teachers
        total_query = select(func.count(self.model.id)).where(
            and_(
                self.model.school_id == school_id,
                self.model.deleted_at.is_(None)
            )
        )
        total_result = await self.session.execute(total_query)
        total = total_result.scalar()

        # Active teachers
        active_query = select(func.count(self.model.id)).where(
            and_(
                self.model.school_id == school_id,
                self.model.status == 'active',
                self.model.is_active == True,
                self.model.deleted_at.is_(None)
            )
        )
        active_result = await self.session.execute(active_query)
        active = active_result.scalar()

        # By employment type
        employment_query = select(
            self.model.employment_type,
            func.count(self.model.id).label('count')
        ).where(
            and_(
                self.model.school_id == school_id,
                self.model.deleted_at.is_(None)
            )
        ).group_by(self.model.employment_type)
        employment_result = await self.session.execute(employment_query)
        by_employment_type = {row.employment_type: row.count for row in employment_result.all()}

        # By department
        department_counts = await self.count_by_department(school_id)

        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_employment_type': by_employment_type,
            'by_department': department_counts
        }
