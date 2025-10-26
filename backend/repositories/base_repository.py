"""
Base Repository
Abstract repository with common CRUD operations
"""
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.sql import Select
from models.base import BaseModel
import uuid
from datetime import datetime


ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Initialize repository

        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session

    async def create(self, data: Dict[str, Any], created_by_id: Optional[uuid.UUID] = None) -> ModelType:
        """
        Create a new record

        Args:
            data: Dictionary of field values
            created_by_id: UUID of user creating the record

        Returns:
            Created model instance
        """
        if created_by_id:
            data['created_by'] = created_by_id

        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(
        self,
        id: uuid.UUID,
        include_deleted: bool = False
    ) -> Optional[ModelType]:
        """
        Get a record by ID

        Args:
            id: Record UUID
            include_deleted: Whether to include soft-deleted records

        Returns:
            Model instance or None
        """
        query = select(self.model).where(self.model.id == id)

        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 20,
        order_by: Optional[str] = None,
        order_direction: str = "desc",
        include_deleted: bool = False
    ) -> tuple[List[ModelType], int]:
        """
        Find all records with filtering and pagination

        Args:
            filters: Dictionary of field filters
            page: Page number (1-indexed)
            limit: Items per page
            order_by: Field to order by
            order_direction: 'asc' or 'desc'
            include_deleted: Whether to include soft-deleted records

        Returns:
            Tuple of (records list, total count)
        """
        query = select(self.model)

        # Apply filters
        if filters:
            query = self._apply_filters(query, filters)

        # Exclude soft-deleted records
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            if order_direction.lower() == "asc":
                query = query.order_by(order_column.asc())
            else:
                query = query.order_by(order_column.desc())
        else:
            # Default ordering by created_at descending
            query = query.order_by(self.model.created_at.desc())

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # Execute query
        result = await self.session.execute(query)
        records = result.scalars().all()

        return list(records), total

    async def update(
        self,
        id: uuid.UUID,
        data: Dict[str, Any],
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[ModelType]:
        """
        Update a record

        Args:
            id: Record UUID
            data: Dictionary of fields to update
            updated_by_id: UUID of user updating the record

        Returns:
            Updated model instance or None
        """
        instance = await self.get_by_id(id)
        if not instance:
            return None

        # Update fields
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        # Set audit fields
        instance.updated_at = datetime.utcnow()
        if updated_by_id:
            instance.updated_by = updated_by_id

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(
        self,
        id: uuid.UUID,
        deleted_by_id: Optional[uuid.UUID] = None,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete a record (soft delete by default)

        Args:
            id: Record UUID
            deleted_by_id: UUID of user deleting the record
            hard_delete: If True, permanently delete the record

        Returns:
            True if deleted, False if not found
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False

        if hard_delete:
            await self.session.delete(instance)
        else:
            instance.soft_delete(deleted_by_id)
            await self.session.flush()

        return True

    async def exists(self, id: uuid.UUID) -> bool:
        """
        Check if a record exists

        Args:
            id: Record UUID

        Returns:
            True if exists, False otherwise
        """
        result = await self.get_by_id(id)
        return result is not None

    def _apply_filters(self, query: Select, filters: Dict[str, Any]) -> Select:
        """
        Apply filters to query

        Args:
            query: SQLAlchemy query
            filters: Dictionary of filters

        Returns:
            Modified query
        """
        for key, value in filters.items():
            if hasattr(self.model, key):
                if value is None:
                    query = query.where(getattr(self.model, key).is_(None))
                elif isinstance(value, list):
                    query = query.where(getattr(self.model, key).in_(value))
                else:
                    query = query.where(getattr(self.model, key) == value)

        return query
