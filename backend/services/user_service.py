"""
User Service
Business logic layer for user operations
"""
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.user_repository import UserRepository
from models.user import User
from schemas.user_schema import (
    UserCreateSchema,
    UserUpdateSchema,
    UserResponseSchema,
    UserSearchSchema,
    UserStatisticsSchema,
)
from utils.security import hash_password, verify_password
import uuid
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service layer for user business logic"""

    def __init__(self, session: AsyncSession):
        """
        Initialize user service

        Args:
            session: Database session
        """
        self.session = session
        self.repository = UserRepository(session)

    async def create_user(
        self,
        user_data: UserCreateSchema,
        created_by_id: Optional[uuid.UUID] = None
    ) -> UserResponseSchema:
        """
        Create a new user

        Args:
            user_data: User creation data
            created_by_id: UUID of user creating this user

        Returns:
            Created user response schema

        Raises:
            ValueError: If email already exists or validation fails
        """
        # Check if email already exists
        if await self.repository.email_exists(user_data.email):
            raise ValueError(f"Email {user_data.email} already exists")

        # Prepare user data
        user_dict = user_data.model_dump()

        # Hash password if provided
        if user_dict.get('password'):
            user_dict['password_hash'] = hash_password(user_dict.pop('password'))
        else:
            user_dict.pop('password', None)

        # Create user
        user = await self.repository.create(user_dict, created_by_id)
        await self.session.commit()

        logger.info(f"User created: {user.email} (ID: {user.id})")

        # Convert to response schema
        return self._to_response_schema(user)

    async def get_user(
        self,
        user_id: uuid.UUID,
        requesting_user_id: Optional[uuid.UUID] = None,
        requesting_user_persona: Optional[str] = None
    ) -> Optional[UserResponseSchema]:
        """
        Get a user by ID

        Args:
            user_id: User UUID
            requesting_user_id: UUID of user making the request
            requesting_user_persona: Persona of requesting user

        Returns:
            User response schema or None

        Raises:
            PermissionError: If user not authorized to view
        """
        user = await self.repository.find_by_id(user_id)
        if not user:
            return None

        # Authorization check: Admin can view all, others can only view self
        if requesting_user_persona != "administrator" and requesting_user_id != user_id:
            raise PermissionError("Not authorized to view this user")

        return self._to_response_schema(user)

    async def get_user_by_email(
        self,
        email: str,
        school_id: Optional[uuid.UUID] = None
    ) -> Optional[UserResponseSchema]:
        """
        Get a user by email

        Args:
            email: User email
            school_id: Optional school ID for multi-tenant filtering

        Returns:
            User response schema or None
        """
        user = await self.repository.find_by_email(email, school_id)
        if not user:
            return None

        return self._to_response_schema(user)

    async def search_users(
        self,
        school_id: uuid.UUID,
        search_params: UserSearchSchema,
        requesting_user_persona: str
    ) -> Tuple[List[UserResponseSchema], Dict[str, Any]]:
        """
        Search users with filters and pagination

        Args:
            school_id: School UUID
            search_params: Search parameters
            requesting_user_persona: Persona of requesting user

        Returns:
            Tuple of (user list, pagination info)

        Raises:
            PermissionError: If user not authorized to search
        """
        # Only administrators can search all users
        if requesting_user_persona != "administrator":
            raise PermissionError("Only administrators can search users")

        # Execute search
        users, total = await self.repository.search_users(
            school_id=school_id,
            search_term=search_params.search,
            persona=search_params.persona.value if search_params.persona else None,
            status=search_params.status.value if search_params.status else None,
            page=search_params.page,
            limit=search_params.limit,
            order_by=search_params.sort,
            order_direction=search_params.order
        )

        # Convert to response schemas
        user_responses = [self._to_response_schema(user) for user in users]

        # Build pagination info
        pagination = {
            "page": search_params.page,
            "limit": search_params.limit,
            "total": total,
            "pages": (total + search_params.limit - 1) // search_params.limit
        }

        return user_responses, pagination

    async def update_user(
        self,
        user_id: uuid.UUID,
        user_data: UserUpdateSchema,
        updated_by_id: Optional[uuid.UUID] = None,
        requesting_user_persona: Optional[str] = None
    ) -> Optional[UserResponseSchema]:
        """
        Update a user

        Args:
            user_id: User UUID
            user_data: Update data
            updated_by_id: UUID of user making the update
            requesting_user_persona: Persona of requesting user

        Returns:
            Updated user response schema or None

        Raises:
            PermissionError: If user not authorized to update
        """
        # Check if user exists
        existing_user = await self.repository.find_by_id(user_id)
        if not existing_user:
            return None

        # Authorization: Admin can update all, users can update self (limited fields)
        if requesting_user_persona != "administrator" and updated_by_id != user_id:
            raise PermissionError("Not authorized to update this user")

        # Prepare update data (exclude None values)
        update_dict = user_data.model_dump(exclude_none=True)

        # Update user
        updated_user = await self.repository.update(user_id, update_dict, updated_by_id)
        await self.session.commit()

        logger.info(f"User updated: {updated_user.email} (ID: {updated_user.id})")

        return self._to_response_schema(updated_user)

    async def delete_user(
        self,
        user_id: uuid.UUID,
        deleted_by_id: Optional[uuid.UUID] = None,
        requesting_user_persona: Optional[str] = None
    ) -> bool:
        """
        Soft delete a user

        Args:
            user_id: User UUID
            deleted_by_id: UUID of user performing deletion
            requesting_user_persona: Persona of requesting user

        Returns:
            True if deleted, False if not found

        Raises:
            PermissionError: If user not authorized to delete
        """
        # Only administrators can delete users
        if requesting_user_persona != "administrator":
            raise PermissionError("Only administrators can delete users")

        # Perform soft delete
        success = await self.repository.delete(user_id, deleted_by_id)
        if success:
            await self.session.commit()
            logger.info(f"User deleted: ID {user_id}")

        return success

    async def change_user_status(
        self,
        user_id: uuid.UUID,
        new_status: str,
        updated_by_id: Optional[uuid.UUID] = None,
        requesting_user_persona: Optional[str] = None
    ) -> Optional[UserResponseSchema]:
        """
        Change user status

        Args:
            user_id: User UUID
            new_status: New status value
            updated_by_id: UUID of user making the change
            requesting_user_persona: Persona of requesting user

        Returns:
            Updated user or None

        Raises:
            PermissionError: If user not authorized
        """
        # Only administrators can change status
        if requesting_user_persona != "administrator":
            raise PermissionError("Only administrators can change user status")

        updated_user = await self.repository.change_status(user_id, new_status, updated_by_id)
        if updated_user:
            await self.session.commit()
            logger.info(f"User status changed: {updated_user.email} -> {new_status}")

        return self._to_response_schema(updated_user) if updated_user else None

    async def change_user_persona(
        self,
        user_id: uuid.UUID,
        new_persona: str,
        updated_by_id: Optional[uuid.UUID] = None,
        requesting_user_persona: Optional[str] = None
    ) -> Optional[UserResponseSchema]:
        """
        Change user persona

        Args:
            user_id: User UUID
            new_persona: New persona value
            updated_by_id: UUID of user making the change
            requesting_user_persona: Persona of requesting user

        Returns:
            Updated user or None

        Raises:
            PermissionError: If user not authorized
        """
        # Only administrators can change persona
        if requesting_user_persona != "administrator":
            raise PermissionError("Only administrators can change user persona")

        updated_user = await self.repository.change_persona(user_id, new_persona, updated_by_id)
        if updated_user:
            await self.session.commit()
            logger.info(f"User persona changed: {updated_user.email} -> {new_persona}")

        return self._to_response_schema(updated_user) if updated_user else None

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        requesting_user_persona: str
    ) -> UserStatisticsSchema:
        """
        Get user statistics for a school

        Args:
            school_id: School UUID
            requesting_user_persona: Persona of requesting user

        Returns:
            User statistics

        Raises:
            PermissionError: If user not authorized
        """
        # Only administrators can view statistics
        if requesting_user_persona != "administrator":
            raise PermissionError("Only administrators can view user statistics")

        stats = await self.repository.get_statistics(school_id)
        return UserStatisticsSchema(**stats)

    async def verify_password(
        self,
        user_id: uuid.UUID,
        password: str
    ) -> bool:
        """
        Verify a user's password

        Args:
            user_id: User UUID
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise
        """
        user = await self.repository.find_by_id(user_id)
        if not user or not user.password_hash:
            return False

        return verify_password(password, user.password_hash)

    async def update_last_login(self, user_id: uuid.UUID) -> Optional[UserResponseSchema]:
        """
        Update user's last login timestamp

        Args:
            user_id: User UUID

        Returns:
            Updated user or None
        """
        user = await self.repository.update_last_login(user_id)
        if user:
            await self.session.commit()

        return self._to_response_schema(user) if user else None

    def _to_response_schema(self, user: User) -> UserResponseSchema:
        """
        Convert User model to response schema

        Args:
            user: User model instance

        Returns:
            UserResponseSchema
        """
        user_dict = user.to_dict(include_sensitive=False)

        # Add computed fields
        user_dict['full_name'] = user.get_full_name()
        user_dict['is_active'] = user.is_active()

        return UserResponseSchema(**user_dict)
