"""
Subject Repository

Data access layer for Subject operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from models.subject import Subject
from models.school import School
import uuid


class SubjectRepository:
    """Repository for Subject data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, subject: Subject) -> Subject:
        """Create a new subject."""
        self.session.add(subject)
        await self.session.commit()
        await self.session.refresh(subject)
        return subject

    async def get_by_id(self, subject_id: uuid.UUID) -> Optional[Subject]:
        """Get subject by ID."""
        query = select(Subject).where(
            and_(
                Subject.id == subject_id,
                Subject.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(self, school_id: uuid.UUID, code: str) -> Optional[Subject]:
        """Get subject by code within a school."""
        query = select(Subject).where(
            and_(
                Subject.school_id == school_id,
                Subject.code == code,
                Subject.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_relationships(self, subject_id: uuid.UUID) -> Optional[Subject]:
        """Get subject by ID with all relationships loaded."""
        query = select(Subject).where(
            and_(
                Subject.id == subject_id,
                Subject.deleted_at.is_(None)
            )
        ).options(
            selectinload(Subject.school)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 50,
        category: Optional[str] = None,
        subject_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_required: Optional[bool] = None
    ) -> Tuple[List[Subject], int]:
        """
        Get subjects for a school with pagination and filters.

        Args:
            school_id: School UUID
            page: Page number (1-indexed)
            limit: Items per page
            category: Filter by category
            subject_type: Filter by subject type
            is_active: Filter by active status
            is_required: Filter by required status

        Returns:
            Tuple of (subjects list, total count)
        """
        # Base query
        conditions = [
            Subject.school_id == school_id,
            Subject.deleted_at.is_(None)
        ]

        # Apply filters
        if category:
            conditions.append(Subject.category == category)
        if subject_type:
            conditions.append(Subject.subject_type == subject_type)
        if is_active is not None:
            conditions.append(Subject.is_active == is_active)
        if is_required is not None:
            conditions.append(Subject.is_required == is_required)

        # Count query
        count_query = select(func.count(Subject.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query with pagination
        offset = (page - 1) * limit
        data_query = (
            select(Subject)
            .where(and_(*conditions))
            .order_by(Subject.display_order, Subject.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(data_query)
        subjects = result.scalars().all()

        return subjects, total

    async def get_by_category(self, school_id: uuid.UUID, category: str) -> List[Subject]:
        """Get all subjects in a category."""
        query = select(Subject).where(
            and_(
                Subject.school_id == school_id,
                Subject.category == category,
                Subject.deleted_at.is_(None)
            )
        ).order_by(Subject.display_order, Subject.name)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_grade(self, school_id: uuid.UUID, grade: int) -> List[Subject]:
        """Get all subjects taught at a specific grade level."""
        query = select(Subject).where(
            and_(
                Subject.school_id == school_id,
                Subject.grade_levels.contains([grade]),
                Subject.deleted_at.is_(None)
            )
        ).order_by(Subject.display_order, Subject.name)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_active(self, school_id: uuid.UUID) -> List[Subject]:
        """Get all active subjects for a school."""
        query = select(Subject).where(
            and_(
                Subject.school_id == school_id,
                Subject.is_active == True,
                Subject.deleted_at.is_(None)
            )
        ).order_by(Subject.display_order, Subject.name)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_required(self, school_id: uuid.UUID) -> List[Subject]:
        """Get all required subjects for a school."""
        query = select(Subject).where(
            and_(
                Subject.school_id == school_id,
                Subject.is_required == True,
                Subject.deleted_at.is_(None)
            )
        ).order_by(Subject.display_order, Subject.name)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def search(
        self,
        school_id: uuid.UUID,
        search_query: str,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Subject], int]:
        """
        Search subjects by code, name, or description.

        Args:
            school_id: School UUID
            search_query: Search term
            page: Page number
            limit: Items per page

        Returns:
            Tuple of (subjects list, total count)
        """
        search_pattern = f"%{search_query}%"

        # Base conditions
        conditions = [
            Subject.school_id == school_id,
            Subject.deleted_at.is_(None),
            or_(
                Subject.code.ilike(search_pattern),
                Subject.name.ilike(search_pattern),
                Subject.description.ilike(search_pattern)
            )
        ]

        # Count query
        count_query = select(func.count(Subject.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        offset = (page - 1) * limit
        data_query = (
            select(Subject)
            .where(and_(*conditions))
            .order_by(Subject.display_order, Subject.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(data_query)
        subjects = result.scalars().all()

        return subjects, total

    async def update(self, subject: Subject) -> Subject:
        """Update subject."""
        await self.session.commit()
        await self.session.refresh(subject)
        return subject

    async def delete(self, subject: Subject, deleted_by_id: uuid.UUID) -> bool:
        """Soft delete subject."""
        from datetime import datetime

        subject.deleted_at = datetime.utcnow()
        subject.deleted_by = deleted_by_id
        await self.session.commit()
        return True

    async def toggle_status(self, subject_id: uuid.UUID) -> Optional[Subject]:
        """Toggle active status of a subject."""
        subject = await self.get_by_id(subject_id)
        if subject:
            subject.is_active = not subject.is_active
            await self.session.commit()
            await self.session.refresh(subject)
        return subject

    async def get_statistics(self, school_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get comprehensive statistics for subjects.

        Args:
            school_id: School UUID

        Returns:
            Dictionary with statistics
        """
        # Base query
        base_conditions = [
            Subject.school_id == school_id,
            Subject.deleted_at.is_(None)
        ]

        # Total subjects
        total_query = select(func.count(Subject.id)).where(and_(*base_conditions))
        total_result = await self.session.execute(total_query)
        total_subjects = total_result.scalar() or 0

        # Active subjects
        active_query = select(func.count(Subject.id)).where(
            and_(
                Subject.school_id == school_id,
                Subject.is_active == True,
                Subject.deleted_at.is_(None)
            )
        )
        active_result = await self.session.execute(active_query)
        active_subjects = active_result.scalar() or 0

        # Inactive subjects
        inactive_subjects = total_subjects - active_subjects

        # By category
        category_query = (
            select(Subject.category, func.count(Subject.id))
            .where(and_(*base_conditions))
            .group_by(Subject.category)
        )
        category_result = await self.session.execute(category_query)
        by_category = {row[0]: row[1] for row in category_result.all()}

        # By type
        type_query = (
            select(Subject.subject_type, func.count(Subject.id))
            .where(and_(*base_conditions, Subject.subject_type.isnot(None)))
            .group_by(Subject.subject_type)
        )
        type_result = await self.session.execute(type_query)
        by_type = {row[0]: row[1] for row in type_result.all()}

        # Required subjects
        required_query = select(func.count(Subject.id)).where(
            and_(
                Subject.school_id == school_id,
                Subject.is_required == True,
                Subject.deleted_at.is_(None)
            )
        )
        required_result = await self.session.execute(required_query)
        required_subjects = required_result.scalar() or 0

        # Elective subjects
        elective_subjects = total_subjects - required_subjects

        return {
            "total_subjects": total_subjects,
            "active_subjects": active_subjects,
            "inactive_subjects": inactive_subjects,
            "by_category": by_category,
            "by_type": by_type,
            "required_subjects": required_subjects,
            "elective_subjects": elective_subjects,
        }

    async def code_exists(self, school_id: uuid.UUID, code: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if a subject code already exists for the school."""
        conditions = [
            Subject.school_id == school_id,
            Subject.code == code,
            Subject.deleted_at.is_(None)
        ]

        if exclude_id:
            conditions.append(Subject.id != exclude_id)

        query = select(func.count(Subject.id)).where(and_(*conditions))
        result = await self.session.execute(query)
        count = result.scalar()
        return count > 0
