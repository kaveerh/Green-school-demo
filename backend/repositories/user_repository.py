"""
User Repository
Data access layer for User model
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from repositories.base_repository import BaseRepository
from models.user import User
import uuid


class UserRepository(BaseRepository[User]):
    """Repository for User model with specific user operations"""

    def __init__(self, session: AsyncSession):
        """Initialize user repository"""
        super().__init__(User, session)

    async def find_by_email(
        self,
        email: str,
        school_id: Optional[uuid.UUID] = None,
        include_deleted: bool = False
    ) -> Optional[User]:
        """
        Find a user by email

        Args:
            email: User email address
            school_id: Optional school ID for multi-tenant filtering
            include_deleted: Whether to include soft-deleted users

        Returns:
            User instance or None
        """
        query = select(User).where(User.email == email)

        if school_id:
            query = query.where(User.school_id == school_id)

        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_by_keycloak_id(
        self,
        keycloak_id: str,
        include_deleted: bool = False
    ) -> Optional[User]:
        """
        Find a user by Keycloak ID

        Args:
            keycloak_id: Keycloak user ID
            include_deleted: Whether to include soft-deleted users

        Returns:
            User instance or None
        """
        query = select(User).where(User.keycloak_id == keycloak_id)

        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_by_school(
        self,
        school_id: uuid.UUID,
        persona: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        include_deleted: bool = False
    ) -> tuple[List[User], int]:
        """
        Find users by school with optional filtering

        Args:
            school_id: School UUID
            persona: Optional persona filter
            status: Optional status filter
            page: Page number (1-indexed)
            limit: Items per page
            include_deleted: Whether to include soft-deleted users

        Returns:
            Tuple of (users list, total count)
        """
        filters = {"school_id": school_id}

        if persona:
            filters["persona"] = persona

        if status:
            filters["status"] = status

        return await self.find_all(
            filters=filters,
            page=page,
            limit=limit,
            include_deleted=include_deleted
        )

    async def search_users(
        self,
        school_id: uuid.UUID,
        search_term: Optional[str] = None,
        persona: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> tuple[List[User], int]:
        """
        Search users with multiple filters

        Args:
            school_id: School UUID (required for multi-tenant)
            search_term: Search in first_name, last_name, and email
            persona: Filter by persona
            status: Filter by status
            page: Page number (1-indexed)
            limit: Items per page
            order_by: Field to order by
            order_direction: 'asc' or 'desc'

        Returns:
            Tuple of (users list, total count)
        """
        query = select(User).where(User.school_id == school_id)

        # Exclude soft-deleted
        query = query.where(User.deleted_at.is_(None))

        # Apply search term
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.where(
                or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            )

        # Apply persona filter
        if persona:
            query = query.where(User.persona == persona)

        # Apply status filter
        if status:
            query = query.where(User.status == status)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Apply ordering
        if order_by and hasattr(User, order_by):
            order_column = getattr(User, order_by)
            if order_direction.lower() == "asc":
                query = query.order_by(order_column.asc())
            else:
                query = query.order_by(order_column.desc())
        else:
            query = query.order_by(User.created_at.desc())

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # Execute query
        result = await self.session.execute(query)
        users = result.scalars().all()

        return list(users), total

    async def count_by_persona(
        self,
        school_id: uuid.UUID,
        persona: str
    ) -> int:
        """
        Count users by persona in a school

        Args:
            school_id: School UUID
            persona: User persona

        Returns:
            Count of users
        """
        query = select(func.count()).select_from(User).where(
            User.school_id == school_id,
            User.persona == persona,
            User.deleted_at.is_(None)
        )

        result = await self.session.execute(query)
        return result.scalar()

    async def count_by_status(
        self,
        school_id: uuid.UUID,
        status: str
    ) -> int:
        """
        Count users by status in a school

        Args:
            school_id: School UUID
            status: User status

        Returns:
            Count of users
        """
        query = select(func.count()).select_from(User).where(
            User.school_id == school_id,
            User.status == status,
            User.deleted_at.is_(None)
        )

        result = await self.session.execute(query)
        return result.scalar()

    async def get_statistics(self, school_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get user statistics for a school

        Args:
            school_id: School UUID

        Returns:
            Dictionary with statistics
        """
        base_query = select(func.count()).select_from(User).where(
            User.school_id == school_id,
            User.deleted_at.is_(None)
        )

        # Total users
        total_result = await self.session.execute(base_query)
        total = total_result.scalar()

        # By persona
        administrators = await self.count_by_persona(school_id, "administrator")
        teachers = await self.count_by_persona(school_id, "teacher")
        students = await self.count_by_persona(school_id, "student")
        parents = await self.count_by_persona(school_id, "parent")
        vendors = await self.count_by_persona(school_id, "vendor")

        # By status
        active = await self.count_by_status(school_id, "active")
        inactive = await self.count_by_status(school_id, "inactive")
        suspended = await self.count_by_status(school_id, "suspended")

        return {
            "total": total,
            "by_persona": {
                "administrators": administrators,
                "teachers": teachers,
                "students": students,
                "parents": parents,
                "vendors": vendors
            },
            "by_status": {
                "active": active,
                "inactive": inactive,
                "suspended": suspended
            }
        }

    async def email_exists(
        self,
        email: str,
        exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if an email already exists

        Args:
            email: Email to check
            exclude_id: Optional user ID to exclude (for updates)

        Returns:
            True if email exists, False otherwise
        """
        query = select(func.count()).select_from(User).where(
            User.email == email,
            User.deleted_at.is_(None)
        )

        if exclude_id:
            query = query.where(User.id != exclude_id)

        result = await self.session.execute(query)
        count = result.scalar()
        return count > 0

    async def update_last_login(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Update user's last login timestamp

        Args:
            user_id: User UUID

        Returns:
            Updated user or None
        """
        from datetime import datetime

        user = await self.find_by_id(user_id)
        if not user:
            return None

        user.last_login = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def change_status(
        self,
        user_id: uuid.UUID,
        new_status: str,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[User]:
        """
        Change user status

        Args:
            user_id: User UUID
            new_status: New status value
            updated_by_id: UUID of user making the change

        Returns:
            Updated user or None
        """
        valid_statuses = ["active", "inactive", "suspended"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        return await self.update(user_id, {"status": new_status}, updated_by_id)

    async def change_persona(
        self,
        user_id: uuid.UUID,
        new_persona: str,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[User]:
        """
        Change user persona

        Args:
            user_id: User UUID
            new_persona: New persona value
            updated_by_id: UUID of user making the change

        Returns:
            Updated user or None
        """
        valid_personas = ["administrator", "teacher", "student", "parent", "vendor"]
        if new_persona not in valid_personas:
            raise ValueError(f"Invalid persona. Must be one of: {valid_personas}")

        return await self.update(user_id, {"persona": new_persona}, updated_by_id)
