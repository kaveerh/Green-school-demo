"""
Subject Service

Business logic layer for Subject operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.subject_repository import SubjectRepository
from models.subject import Subject
import uuid
from datetime import datetime


class SubjectService:
    """Service layer for Subject business logic."""

    def __init__(self, session: AsyncSession):
        self.repository = SubjectRepository(session)

    async def create_subject(
        self,
        school_id: uuid.UUID,
        code: str,
        name: str,
        created_by_id: uuid.UUID,
        description: Optional[str] = None,
        category: str = "core",
        subject_type: Optional[str] = None,
        grade_levels: Optional[List[int]] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        display_order: int = 0,
        credits: Optional[float] = None,
        is_required: bool = True,
        is_active: bool = True
    ) -> Subject:
        """
        Create a new subject.

        Args:
            school_id: School UUID
            code: Subject code (unique per school)
            name: Subject name
            created_by_id: User ID of creator
            description: Subject description
            category: Subject category
            subject_type: Subject type
            grade_levels: List of grade levels (1-7)
            color: Hex color code
            icon: Icon/emoji
            display_order: Display order
            credits: Credit hours
            is_required: Required flag
            is_active: Active flag

        Returns:
            Created Subject

        Raises:
            ValueError: If validation fails
        """
        # Validate code format (uppercase, alphanumeric + underscore)
        code = code.upper().strip()
        if not code or len(code) < 2 or len(code) > 50:
            raise ValueError("Subject code must be 2-50 characters")

        # Check if code already exists
        existing = await self.repository.code_exists(school_id, code)
        if existing:
            raise ValueError(f"Subject code '{code}' already exists for this school")

        # Validate grade levels
        if grade_levels:
            invalid_grades = [g for g in grade_levels if g < 1 or g > 7]
            if invalid_grades:
                raise ValueError(f"Invalid grade levels: {invalid_grades}. Must be 1-7")
        else:
            grade_levels = [1, 2, 3, 4, 5, 6, 7]  # Default to all grades

        # Validate color format
        if color:
            if not self._is_valid_hex_color(color):
                raise ValueError(f"Invalid color format: {color}. Must be hex format like #FF5733")

        # Validate category
        valid_categories = ['core', 'elective', 'enrichment', 'remedial', 'other']
        if category not in valid_categories:
            raise ValueError(f"Invalid category: {category}. Must be one of {valid_categories}")

        # Validate subject type if provided
        if subject_type:
            valid_types = ['academic', 'arts', 'physical', 'technical', 'other']
            if subject_type not in valid_types:
                raise ValueError(f"Invalid subject type: {subject_type}. Must be one of {valid_types}")

        # Create subject
        subject = Subject(
            school_id=school_id,
            code=code,
            name=name.strip(),
            description=description,
            category=category,
            subject_type=subject_type,
            grade_levels=grade_levels,
            color=color,
            icon=icon,
            display_order=display_order,
            credits=credits,
            is_required=is_required,
            is_active=is_active,
            created_by=created_by_id,
            updated_by=created_by_id
        )

        return await self.repository.create(subject)

    async def get_subject_by_id(self, subject_id: uuid.UUID) -> Optional[Subject]:
        """Get subject by ID with relationships."""
        return await self.repository.get_with_relationships(subject_id)

    async def get_subject_by_code(self, school_id: uuid.UUID, code: str) -> Optional[Subject]:
        """Get subject by code."""
        return await self.repository.get_by_code(school_id, code.upper())

    async def get_subjects_by_school(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 50,
        category: Optional[str] = None,
        subject_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_required: Optional[bool] = None
    ) -> Tuple[List[Subject], int]:
        """Get subjects for a school with pagination and filters."""
        return await self.repository.get_by_school(
            school_id, page, limit, category, subject_type, is_active, is_required
        )

    async def get_subjects_by_category(self, school_id: uuid.UUID, category: str) -> List[Subject]:
        """Get subjects by category."""
        return await self.repository.get_by_category(school_id, category)

    async def get_subjects_by_grade(self, school_id: uuid.UUID, grade: int) -> List[Subject]:
        """Get subjects for a specific grade level."""
        if grade < 1 or grade > 7:
            raise ValueError(f"Invalid grade level: {grade}. Must be 1-7")
        return await self.repository.get_by_grade(school_id, grade)

    async def get_active_subjects(self, school_id: uuid.UUID) -> List[Subject]:
        """Get all active subjects."""
        return await self.repository.get_active(school_id)

    async def get_required_subjects(self, school_id: uuid.UUID) -> List[Subject]:
        """Get all required subjects."""
        return await self.repository.get_required(school_id)

    async def search_subjects(
        self,
        school_id: uuid.UUID,
        query: str,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Subject], int]:
        """Search subjects by code, name, or description."""
        if len(query) < 2:
            raise ValueError("Search query must be at least 2 characters")

        return await self.repository.search(school_id, query, page, limit)

    async def update_subject(
        self,
        subject_id: uuid.UUID,
        updated_by_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        subject_type: Optional[str] = None,
        grade_levels: Optional[List[int]] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        display_order: Optional[int] = None,
        credits: Optional[float] = None,
        is_required: Optional[bool] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Subject]:
        """
        Update subject.

        Args:
            subject_id: Subject UUID
            updated_by_id: User ID of updater
            (other fields): Optional fields to update

        Returns:
            Updated Subject or None if not found

        Raises:
            ValueError: If validation fails
        """
        subject = await self.repository.get_by_id(subject_id)
        if not subject:
            return None

        # Validate and update fields
        if name is not None:
            subject.name = name.strip()

        if description is not None:
            subject.description = description

        if category is not None:
            valid_categories = ['core', 'elective', 'enrichment', 'remedial', 'other']
            if category not in valid_categories:
                raise ValueError(f"Invalid category: {category}")
            subject.category = category

        if subject_type is not None:
            valid_types = ['academic', 'arts', 'physical', 'technical', 'other']
            if subject_type not in valid_types:
                raise ValueError(f"Invalid subject type: {subject_type}")
            subject.subject_type = subject_type

        if grade_levels is not None:
            invalid_grades = [g for g in grade_levels if g < 1 or g > 7]
            if invalid_grades:
                raise ValueError(f"Invalid grade levels: {invalid_grades}")
            if not grade_levels:
                raise ValueError("At least one grade level must be selected")
            subject.grade_levels = grade_levels

        if color is not None:
            if color and not self._is_valid_hex_color(color):
                raise ValueError(f"Invalid color format: {color}")
            subject.color = color

        if icon is not None:
            subject.icon = icon

        if display_order is not None:
            subject.display_order = display_order

        if credits is not None:
            if credits < 0:
                raise ValueError("Credits cannot be negative")
            subject.credits = credits

        if is_required is not None:
            subject.is_required = is_required

        if is_active is not None:
            subject.is_active = is_active

        subject.updated_by = updated_by_id
        subject.updated_at = datetime.utcnow()

        return await self.repository.update(subject)

    async def delete_subject(self, subject_id: uuid.UUID, deleted_by_id: uuid.UUID) -> bool:
        """
        Soft delete subject.

        Args:
            subject_id: Subject UUID
            deleted_by_id: User ID of deleter

        Returns:
            True if successful, False if not found

        Raises:
            ValueError: If subject has dependencies (classes, etc.)
        """
        subject = await self.repository.get_by_id(subject_id)
        if not subject:
            return False

        # TODO: Check for dependencies (classes, assessments, lessons)
        # For now, proceed with delete
        # In future: Add checks like:
        # if await self._has_active_classes(subject_id):
        #     raise ValueError("Cannot delete subject with active classes")

        return await self.repository.delete(subject, deleted_by_id)

    async def toggle_status(self, subject_id: uuid.UUID) -> Optional[Subject]:
        """Toggle active status of a subject."""
        return await self.repository.toggle_status(subject_id)

    async def get_statistics(self, school_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive statistics for subjects."""
        return await self.repository.get_statistics(school_id)

    @staticmethod
    def _is_valid_hex_color(color: str) -> bool:
        """Validate hex color format (#RRGGBB)."""
        if not color:
            return True

        import re
        pattern = r'^#[0-9A-Fa-f]{6}$'
        return bool(re.match(pattern, color))
