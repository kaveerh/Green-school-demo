"""
School Repository
Data access layer for schools
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
import uuid

from repositories.base_repository import BaseRepository
from models.school import School


class SchoolRepository(BaseRepository[School]):
    """Repository for school data access"""

    def __init__(self, session: AsyncSession):
        """
        Initialize school repository

        Args:
            session: Async database session
        """
        super().__init__(School, session)

    async def find_by_slug(self, slug: str) -> Optional[School]:
        """
        Find a school by slug

        Args:
            slug: School URL slug

        Returns:
            School instance or None
        """
        query = select(School).where(
            School.slug == slug,
            School.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_by_name(self, name: str) -> Optional[School]:
        """
        Find a school by name

        Args:
            name: School name

        Returns:
            School instance or None
        """
        query = select(School).where(
            School.name == name,
            School.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_active_schools(
        self,
        page: int = 1,
        limit: int = 20
    ) -> tuple[List[School], int]:
        """
        Find all active schools

        Args:
            page: Page number
            limit: Items per page

        Returns:
            Tuple of (schools list, total count)
        """
        return await self.find_all(
            filters={"status": "active"},
            page=page,
            limit=limit
        )

    async def search_schools(
        self,
        search_term: str,
        page: int = 1,
        limit: int = 20
    ) -> tuple[List[School], int]:
        """
        Search schools by name, city, or email

        Args:
            search_term: Search text
            page: Page number
            limit: Items per page

        Returns:
            Tuple of (schools list, total count)
        """
        search_pattern = f"%{search_term}%"

        query = select(School).where(
            School.deleted_at.is_(None),
            or_(
                School.name.ilike(search_pattern),
                School.city.ilike(search_pattern),
                School.email.ilike(search_pattern),
                School.slug.ilike(search_pattern)
            )
        )

        # Get total count
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * limit
        query = query.order_by(School.name.asc()).offset(offset).limit(limit)

        result = await self.session.execute(query)
        schools = list(result.scalars().all())

        return schools, total

    async def update_status(
        self,
        school_id: uuid.UUID,
        status: str,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[School]:
        """
        Update school status

        Args:
            school_id: School UUID
            status: New status (active, inactive, suspended)
            updated_by_id: UUID of user updating the record

        Returns:
            Updated school or None
        """
        return await self.update(
            school_id,
            {"status": status},
            updated_by_id
        )

    async def update_settings(
        self,
        school_id: uuid.UUID,
        settings: Dict[str, Any],
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[School]:
        """
        Update school settings

        Args:
            school_id: School UUID
            settings: Settings dictionary
            updated_by_id: UUID of user updating the record

        Returns:
            Updated school or None
        """
        school = await self.find_by_id(school_id)
        if not school:
            return None

        # Merge settings instead of replacing
        current_settings = school.settings or {}
        updated_settings = {**current_settings, **settings}

        return await self.update(
            school_id,
            {"settings": updated_settings},
            updated_by_id
        )

    async def assign_principal(
        self,
        school_id: uuid.UUID,
        principal_id: uuid.UUID,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[School]:
        """
        Assign principal to school

        Args:
            school_id: School UUID
            principal_id: Principal user UUID
            updated_by_id: UUID of user making the assignment

        Returns:
            Updated school or None
        """
        return await self.update(
            school_id,
            {"principal_id": principal_id},
            updated_by_id
        )

    async def assign_hod(
        self,
        school_id: uuid.UUID,
        hod_id: uuid.UUID,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[School]:
        """
        Assign Head of Department to school

        Args:
            school_id: School UUID
            hod_id: HOD user UUID
            updated_by_id: UUID of user making the assignment

        Returns:
            Updated school or None
        """
        return await self.update(
            school_id,
            {"hod_id": hod_id},
            updated_by_id
        )

    async def slug_exists(self, slug: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
        """
        Check if slug already exists

        Args:
            slug: URL slug to check
            exclude_id: Exclude this school ID from check (for updates)

        Returns:
            True if exists, False otherwise
        """
        query = select(School).where(
            School.slug == slug,
            School.deleted_at.is_(None)
        )

        if exclude_id:
            query = query.where(School.id != exclude_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def name_exists(self, name: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
        """
        Check if name already exists

        Args:
            name: School name to check
            exclude_id: Exclude this school ID from check (for updates)

        Returns:
            True if exists, False otherwise
        """
        query = select(School).where(
            School.name == name,
            School.deleted_at.is_(None)
        )

        if exclude_id:
            query = query.where(School.id != exclude_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
