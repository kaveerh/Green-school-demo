"""
Merit Service

Business logic layer for Merit operations including validation and processing.
"""

from typing import Optional, List, Dict, Any
from datetime import date
import uuid

from repositories.merit_repository import MeritRepository
from models.merit import Merit


class MeritService:
    """Service for merit business logic"""

    def __init__(self, repository: MeritRepository):
        self.repository = repository

    async def award_merit(
        self,
        school_id: uuid.UUID,
        student_id: uuid.UUID,
        awarded_by_id: uuid.UUID,
        category: str,
        points: int,
        reason: str,
        **kwargs
    ) -> Merit:
        """
        Award a merit to a student with validation

        Args:
            school_id: School ID
            student_id: Student receiving the merit
            awarded_by_id: User awarding the merit
            category: Merit category
            points: Merit points (1-10)
            reason: Reason for awarding
            **kwargs: Additional merit fields

        Returns:
            Created merit

        Raises:
            ValueError: If validation fails
        """
        # Validate category
        valid_categories = ['academic', 'behavior', 'participation', 'leadership', 'attendance', 'other']
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")

        # Validate points
        if not (1 <= points <= 10):
            raise ValueError("Merit points must be between 1 and 10")

        # Validate reason
        if not reason or len(reason.strip()) < 10:
            raise ValueError("Reason must be at least 10 characters")

        # Validate quarter if provided
        if 'quarter' in kwargs and kwargs['quarter']:
            valid_quarters = ['Q1', 'Q2', 'Q3', 'Q4']
            if kwargs['quarter'] not in valid_quarters:
                raise ValueError(f"Invalid quarter. Must be one of: {', '.join(valid_quarters)}")

        # Create merit
        merit_data = {
            'school_id': school_id,
            'student_id': student_id,
            'awarded_by_id': awarded_by_id,
            'category': category,
            'points': points,
            'reason': reason.strip(),
            'created_by': awarded_by_id,
            **kwargs
        }

        merit = await self.repository.create(merit_data)
        return merit

    async def award_batch_merits(
        self,
        school_id: uuid.UUID,
        student_ids: List[uuid.UUID],
        awarded_by_id: uuid.UUID,
        category: str,
        points: int,
        reason: str,
        **kwargs
    ) -> List[Merit]:
        """
        Award merits to multiple students (class award)

        Args:
            school_id: School ID
            student_ids: List of student IDs
            awarded_by_id: User awarding the merits
            category: Merit category
            points: Merit points (1-10)
            reason: Reason for awarding
            **kwargs: Additional merit fields

        Returns:
            List of created merits

        Raises:
            ValueError: If validation fails
        """
        # Validate at least one student
        if not student_ids or len(student_ids) == 0:
            raise ValueError("At least one student ID is required for batch award")

        # Validate category
        valid_categories = ['academic', 'behavior', 'participation', 'leadership', 'attendance', 'other']
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")

        # Validate points
        if not (1 <= points <= 10):
            raise ValueError("Merit points must be between 1 and 10")

        # Validate reason
        if not reason or len(reason.strip()) < 10:
            raise ValueError("Reason must be at least 10 characters")

        # Generate batch ID
        batch_id = uuid.uuid4()

        # Create merit data for each student
        merits_data = []
        for student_id in student_ids:
            merit_data = {
                'school_id': school_id,
                'student_id': student_id,
                'awarded_by_id': awarded_by_id,
                'category': category,
                'points': points,
                'reason': reason.strip(),
                'created_by': awarded_by_id,
                **kwargs
            }
            merits_data.append(merit_data)

        # Create batch
        merits = await self.repository.create_batch(merits_data, batch_id)
        return merits

    async def update_merit(
        self,
        merit_id: uuid.UUID,
        updated_by_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> Merit:
        """
        Update merit with validation

        Args:
            merit_id: Merit ID
            updated_by_id: User updating the merit
            **kwargs: Fields to update

        Returns:
            Updated merit

        Raises:
            ValueError: If validation fails
        """
        merit = await self.repository.get_by_id(merit_id)
        if not merit:
            raise ValueError(f"Merit with ID {merit_id} not found")

        # Validate category if changing
        if 'category' in kwargs:
            valid_categories = ['academic', 'behavior', 'participation', 'leadership', 'attendance', 'other']
            if kwargs['category'] not in valid_categories:
                raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")

        # Validate points if changing
        if 'points' in kwargs:
            if not (1 <= kwargs['points'] <= 10):
                raise ValueError("Merit points must be between 1 and 10")

        # Validate reason if changing
        if 'reason' in kwargs:
            if not kwargs['reason'] or len(kwargs['reason'].strip()) < 10:
                raise ValueError("Reason must be at least 10 characters")
            kwargs['reason'] = kwargs['reason'].strip()

        # Validate quarter if changing
        if 'quarter' in kwargs and kwargs['quarter']:
            valid_quarters = ['Q1', 'Q2', 'Q3', 'Q4']
            if kwargs['quarter'] not in valid_quarters:
                raise ValueError(f"Invalid quarter. Must be one of: {', '.join(valid_quarters)}")

        kwargs['updated_by'] = updated_by_id
        updated_merit = await self.repository.update(merit_id, kwargs)
        return updated_merit

    async def revoke_merit(
        self,
        merit_id: uuid.UUID,
        deleted_by_id: Optional[uuid.UUID] = None
    ) -> None:
        """
        Revoke a merit (soft delete)

        Args:
            merit_id: Merit ID
            deleted_by_id: User revoking the merit
        """
        merit = await self.repository.get_by_id(merit_id)
        if not merit:
            raise ValueError(f"Merit with ID {merit_id} not found")

        await self.repository.delete(merit_id)

    async def get_student_summary(self, student_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get comprehensive merit summary for a student

        Args:
            student_id: Student ID

        Returns:
            Dictionary with student merit summary
        """
        summary = await self.repository.get_student_summary(student_id)
        return summary

    async def get_class_summary(
        self,
        class_id: uuid.UUID,
        quarter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get class merit statistics

        Args:
            class_id: Class ID
            quarter: Optional quarter filter

        Returns:
            Dictionary with class statistics
        """
        summary = await self.repository.get_class_summary(class_id, quarter)
        return summary

    async def get_leaderboard(
        self,
        school_id: uuid.UUID,
        grade_level: Optional[int] = None,
        quarter: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get merit leaderboard

        Args:
            school_id: School ID
            grade_level: Optional grade level filter
            quarter: Optional quarter filter
            limit: Number of top students to return

        Returns:
            List of student rankings
        """
        leaderboard = await self.repository.get_leaderboard(
            school_id=school_id,
            grade_level=grade_level,
            quarter=quarter,
            limit=limit
        )
        return leaderboard

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        quarter: Optional[str] = None,
        grade_level: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get school-wide merit statistics

        Args:
            school_id: School ID
            quarter: Optional quarter filter
            grade_level: Optional grade level filter

        Returns:
            Dictionary with comprehensive statistics
        """
        stats = await self.repository.get_statistics(
            school_id=school_id,
            quarter=quarter,
            grade_level=grade_level
        )
        return stats
