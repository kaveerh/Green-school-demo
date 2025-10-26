"""
School Service
Business logic layer for school operations
"""
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.school_repository import SchoolRepository
from repositories.user_repository import UserRepository
from models.school import School
from schemas.school_schema import (
    SchoolCreateSchema,
    SchoolUpdateSchema,
    SchoolResponseSchema,
    SchoolSearchSchema,
    SchoolStatisticsSchema,
)
import uuid
import logging
import re

logger = logging.getLogger(__name__)


class SchoolService:
    """Service layer for school business logic"""

    def __init__(self, session: AsyncSession):
        """
        Initialize school service

        Args:
            session: Database session
        """
        self.session = session
        self.repository = SchoolRepository(session)
        self.user_repository = UserRepository(session)

    def _generate_slug(self, name: str) -> str:
        """
        Generate URL-friendly slug from school name

        Args:
            name: School name

        Returns:
            URL-friendly slug
        """
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        return slug.strip('-')

    async def create_school(
        self,
        school_data: SchoolCreateSchema,
        created_by_id: Optional[uuid.UUID] = None
    ) -> SchoolResponseSchema:
        """
        Create a new school

        Args:
            school_data: School creation data
            created_by_id: UUID of user creating this school

        Returns:
            Created school response schema

        Raises:
            ValueError: If validation fails
        """
        # Generate slug if not provided
        school_dict = school_data.model_dump()
        if not school_dict.get('slug'):
            school_dict['slug'] = self._generate_slug(school_data.name)

        # Check if name already exists
        if await self.repository.name_exists(school_dict['name']):
            raise ValueError(f"School name '{school_dict['name']}' already exists")

        # Check if slug already exists
        if await self.repository.slug_exists(school_dict['slug']):
            raise ValueError(f"School slug '{school_dict['slug']}' already exists")

        # Validate principal_id if provided
        if school_dict.get('principal_id'):
            principal = await self.user_repository.get_by_id(school_dict['principal_id'])
            if not principal:
                raise ValueError("Principal user not found")
            if principal.persona != "administrator":
                raise ValueError("Principal must have administrator persona")

        # Validate hod_id if provided
        if school_dict.get('hod_id'):
            hod = await self.user_repository.get_by_id(school_dict['hod_id'])
            if not hod:
                raise ValueError("HOD user not found")
            if hod.persona not in ["teacher", "administrator"]:
                raise ValueError("HOD must have teacher or administrator persona")

        # Create school
        school = await self.repository.create(school_dict, created_by_id)
        await self.session.commit()

        logger.info(f"School created: {school.name} (ID: {school.id})")

        return self._to_response_schema(school)

    async def get_school(
        self,
        school_id: uuid.UUID
    ) -> Optional[SchoolResponseSchema]:
        """
        Get a school by ID

        Args:
            school_id: School UUID

        Returns:
            School response schema or None
        """
        school = await self.repository.get_by_id(school_id)
        if not school:
            return None

        return self._to_response_schema(school)

    async def get_school_by_slug(
        self,
        slug: str
    ) -> Optional[SchoolResponseSchema]:
        """
        Get a school by slug

        Args:
            slug: School URL slug

        Returns:
            School response schema or None
        """
        school = await self.repository.find_by_slug(slug)
        if not school:
            return None

        return self._to_response_schema(school)

    async def search_schools(
        self,
        search_params: SchoolSearchSchema
    ) -> Tuple[List[SchoolResponseSchema], Dict[str, Any]]:
        """
        Search schools with filters and pagination

        Args:
            search_params: Search parameters

        Returns:
            Tuple of (school list, pagination info)
        """
        # Build filters
        filters = {}
        if search_params.status:
            filters['status'] = search_params.status.value
        if search_params.city:
            filters['city'] = search_params.city
        if search_params.state:
            filters['state'] = search_params.state

        # Execute search with filters or search term
        if search_params.search:
            schools, total = await self.repository.search_schools(
                search_term=search_params.search,
                page=search_params.page,
                limit=search_params.limit
            )
        else:
            schools, total = await self.repository.find_all(
                filters=filters if filters else None,
                page=search_params.page,
                limit=search_params.limit,
                order_by=search_params.sort,
                order_direction=search_params.order
            )

        # Convert to response schemas
        school_responses = [self._to_response_schema(school) for school in schools]

        # Build pagination info
        pagination = {
            "page": search_params.page,
            "limit": search_params.limit,
            "total": total,
            "pages": (total + search_params.limit - 1) // search_params.limit
        }

        return school_responses, pagination

    async def update_school(
        self,
        school_id: uuid.UUID,
        school_data: SchoolUpdateSchema,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[SchoolResponseSchema]:
        """
        Update a school

        Args:
            school_id: School UUID
            school_data: Update data
            updated_by_id: UUID of user making the update

        Returns:
            Updated school response schema or None

        Raises:
            ValueError: If validation fails
        """
        # Check if school exists
        existing_school = await self.repository.get_by_id(school_id)
        if not existing_school:
            return None

        # Prepare update data (exclude None values)
        update_dict = school_data.model_dump(exclude_none=True)

        # Validate name uniqueness if changing name
        if 'name' in update_dict:
            if await self.repository.name_exists(update_dict['name'], exclude_id=school_id):
                raise ValueError(f"School name '{update_dict['name']}' already exists")

        # Validate slug uniqueness if changing slug
        if 'slug' in update_dict:
            if await self.repository.slug_exists(update_dict['slug'], exclude_id=school_id):
                raise ValueError(f"School slug '{update_dict['slug']}' already exists")

        # Validate principal_id if provided
        if 'principal_id' in update_dict and update_dict['principal_id']:
            principal = await self.user_repository.get_by_id(update_dict['principal_id'])
            if not principal:
                raise ValueError("Principal user not found")
            if principal.persona != "administrator":
                raise ValueError("Principal must have administrator persona")

        # Validate hod_id if provided
        if 'hod_id' in update_dict and update_dict['hod_id']:
            hod = await self.user_repository.get_by_id(update_dict['hod_id'])
            if not hod:
                raise ValueError("HOD user not found")
            if hod.persona not in ["teacher", "administrator"]:
                raise ValueError("HOD must have teacher or administrator persona")

        # Update school
        updated_school = await self.repository.update(school_id, update_dict, updated_by_id)
        await self.session.commit()

        logger.info(f"School updated: {updated_school.name} (ID: {updated_school.id})")

        return self._to_response_schema(updated_school)

    async def delete_school(
        self,
        school_id: uuid.UUID,
        deleted_by_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Soft delete a school

        Args:
            school_id: School UUID
            deleted_by_id: UUID of user performing deletion

        Returns:
            True if deleted, False if not found
        """
        # Perform soft delete
        success = await self.repository.delete(school_id, deleted_by_id)
        if success:
            await self.session.commit()
            logger.info(f"School deleted: ID {school_id}")

        return success

    async def change_school_status(
        self,
        school_id: uuid.UUID,
        new_status: str,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[SchoolResponseSchema]:
        """
        Change school status

        Args:
            school_id: School UUID
            new_status: New status value
            updated_by_id: UUID of user making the change

        Returns:
            Updated school or None
        """
        updated_school = await self.repository.update_status(school_id, new_status, updated_by_id)
        if updated_school:
            await self.session.commit()
            logger.info(f"School status changed: {updated_school.name} -> {new_status}")

        return self._to_response_schema(updated_school) if updated_school else None

    async def update_school_settings(
        self,
        school_id: uuid.UUID,
        settings: Dict[str, Any],
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[SchoolResponseSchema]:
        """
        Update school settings

        Args:
            school_id: School UUID
            settings: Settings dictionary to merge
            updated_by_id: UUID of user making the update

        Returns:
            Updated school or None
        """
        updated_school = await self.repository.update_settings(school_id, settings, updated_by_id)
        if updated_school:
            await self.session.commit()
            logger.info(f"School settings updated: {updated_school.name}")

        return self._to_response_schema(updated_school) if updated_school else None

    async def assign_principal(
        self,
        school_id: uuid.UUID,
        principal_id: uuid.UUID,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[SchoolResponseSchema]:
        """
        Assign principal to school

        Args:
            school_id: School UUID
            principal_id: Principal user UUID
            updated_by_id: UUID of user making the assignment

        Returns:
            Updated school or None

        Raises:
            ValueError: If principal validation fails
        """
        # Validate principal
        principal = await self.user_repository.get_by_id(principal_id)
        if not principal:
            raise ValueError("Principal user not found")
        if principal.persona != "administrator":
            raise ValueError("Principal must have administrator persona")

        updated_school = await self.repository.assign_principal(school_id, principal_id, updated_by_id)
        if updated_school:
            await self.session.commit()
            logger.info(f"Principal assigned to school {updated_school.name}")

        return self._to_response_schema(updated_school) if updated_school else None

    async def assign_hod(
        self,
        school_id: uuid.UUID,
        hod_id: uuid.UUID,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[SchoolResponseSchema]:
        """
        Assign Head of Department to school

        Args:
            school_id: School UUID
            hod_id: HOD user UUID
            updated_by_id: UUID of user making the assignment

        Returns:
            Updated school or None

        Raises:
            ValueError: If HOD validation fails
        """
        # Validate HOD
        hod = await self.user_repository.get_by_id(hod_id)
        if not hod:
            raise ValueError("HOD user not found")
        if hod.persona not in ["teacher", "administrator"]:
            raise ValueError("HOD must have teacher or administrator persona")

        updated_school = await self.repository.assign_hod(school_id, hod_id, updated_by_id)
        if updated_school:
            await self.session.commit()
            logger.info(f"HOD assigned to school {updated_school.name}")

        return self._to_response_schema(updated_school) if updated_school else None

    async def get_statistics(self) -> SchoolStatisticsSchema:
        """
        Get school statistics

        Returns:
            School statistics
        """
        # Get all schools
        schools, total = await self.repository.find_all(limit=1000, include_deleted=False)

        # Calculate statistics
        by_status = {}
        by_state = {}
        active_count = 0
        inactive_count = 0

        for school in schools:
            # Count by status
            status = school.status
            by_status[status] = by_status.get(status, 0) + 1

            if status == "active":
                active_count += 1
            elif status == "inactive":
                inactive_count += 1

            # Count by state
            if school.state:
                state = school.state
                by_state[state] = by_state.get(state, 0) + 1

        return SchoolStatisticsSchema(
            total=total,
            by_status=by_status,
            by_state=by_state,
            active_count=active_count,
            inactive_count=inactive_count
        )

    def _to_response_schema(self, school: School) -> SchoolResponseSchema:
        """
        Convert School model to response schema

        Args:
            school: School model instance

        Returns:
            SchoolResponseSchema
        """
        school_dict = school.to_dict(include_sensitive=False)

        # Add computed fields
        school_dict['is_active'] = school.is_active()
        school_dict['full_address'] = school.get_full_address()

        return SchoolResponseSchema(**school_dict)
