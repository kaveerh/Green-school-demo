"""
Room Repository

Data access layer for Room operations.
"""

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple, Dict, Any
import uuid

from models.room import Room


class RoomRepository:
    """Repository for Room database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, room: Room) -> Room:
        """
        Create a new room

        Args:
            room: Room instance to create

        Returns:
            Created Room instance
        """
        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def get_by_id(self, room_id: uuid.UUID) -> Optional[Room]:
        """
        Get room by ID

        Args:
            room_id: Room UUID

        Returns:
            Room instance or None if not found
        """
        result = await self.db.execute(
            select(Room).where(
                and_(
                    Room.id == room_id,
                    Room.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, school_id: uuid.UUID, room_number: str) -> Optional[Room]:
        """
        Get room by room number within a school

        Args:
            school_id: School UUID
            room_number: Room number

        Returns:
            Room instance or None if not found
        """
        result = await self.db.execute(
            select(Room).where(
                and_(
                    Room.school_id == school_id,
                    Room.room_number == room_number.upper(),
                    Room.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 50,
        room_type: Optional[str] = None,
        building: Optional[str] = None,
        floor: Optional[int] = None,
        is_active: Optional[bool] = None,
        is_available: Optional[bool] = None,
        owner_id: Optional[uuid.UUID] = None
    ) -> Tuple[List[Room], int]:
        """
        Get rooms for a school with pagination and filters

        Args:
            school_id: School UUID
            page: Page number (starts at 1)
            limit: Results per page
            room_type: Filter by room type
            building: Filter by building
            floor: Filter by floor
            is_active: Filter by active status
            is_available: Filter by availability
            owner_id: Filter by owner

        Returns:
            Tuple of (list of rooms, total count)
        """
        # Build base query
        query = select(Room).where(
            and_(
                Room.school_id == school_id,
                Room.deleted_at.is_(None)
            )
        )

        # Apply filters
        if room_type:
            query = query.where(Room.room_type == room_type)

        if building:
            query = query.where(Room.building == building)

        if floor is not None:
            query = query.where(Room.floor == floor)

        if is_active is not None:
            query = query.where(Room.is_active == is_active)

        if is_available is not None:
            query = query.where(Room.is_available == is_available)

        if owner_id:
            query = query.where(Room.owner_id == owner_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination and sorting
        query = query.order_by(Room.display_order, Room.room_number)
        query = query.offset((page - 1) * limit).limit(limit)

        # Execute query
        result = await self.db.execute(query)
        rooms = result.scalars().all()

        return list(rooms), total

    async def get_by_type(self, school_id: uuid.UUID, room_type: str) -> List[Room]:
        """
        Get all rooms of a specific type

        Args:
            school_id: School UUID
            room_type: Room type

        Returns:
            List of Room instances
        """
        result = await self.db.execute(
            select(Room).where(
                and_(
                    Room.school_id == school_id,
                    Room.room_type == room_type,
                    Room.deleted_at.is_(None)
                )
            ).order_by(Room.room_number)
        )
        return list(result.scalars().all())

    async def get_by_building(self, school_id: uuid.UUID, building: str) -> List[Room]:
        """
        Get all rooms in a specific building

        Args:
            school_id: School UUID
            building: Building name

        Returns:
            List of Room instances
        """
        result = await self.db.execute(
            select(Room).where(
                and_(
                    Room.school_id == school_id,
                    Room.building == building,
                    Room.deleted_at.is_(None)
                )
            ).order_by(Room.floor, Room.room_number)
        )
        return list(result.scalars().all())

    async def search(
        self,
        school_id: uuid.UUID,
        search_query: str,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Room], int]:
        """
        Search rooms by room number, name, or description

        Args:
            school_id: School UUID
            search_query: Search query string
            page: Page number
            limit: Results per page

        Returns:
            Tuple of (list of rooms, total count)
        """
        search_pattern = f"%{search_query}%"

        query = select(Room).where(
            and_(
                Room.school_id == school_id,
                Room.deleted_at.is_(None),
                or_(
                    Room.room_number.ilike(search_pattern),
                    Room.room_name.ilike(search_pattern),
                    Room.description.ilike(search_pattern)
                )
            )
        )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination
        query = query.order_by(Room.room_number)
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        rooms = result.scalars().all()

        return list(rooms), total

    async def get_available_rooms(self, school_id: uuid.UUID) -> List[Room]:
        """
        Get all available rooms in a school

        Args:
            school_id: School UUID

        Returns:
            List of available Room instances
        """
        result = await self.db.execute(
            select(Room).where(
                and_(
                    Room.school_id == school_id,
                    Room.is_active == True,
                    Room.is_available == True,
                    Room.deleted_at.is_(None)
                )
            ).order_by(Room.room_type, Room.room_number)
        )
        return list(result.scalars().all())

    async def update(self, room: Room) -> Room:
        """
        Update room

        Args:
            room: Room instance with updated data

        Returns:
            Updated Room instance
        """
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def delete(self, room: Room) -> None:
        """
        Soft delete room

        Args:
            room: Room instance to delete
        """
        room.soft_delete()
        await self.db.commit()

    async def room_number_exists(
        self,
        school_id: uuid.UUID,
        room_number: str,
        exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if room number already exists in school

        Args:
            school_id: School UUID
            room_number: Room number to check
            exclude_id: Room ID to exclude (for updates)

        Returns:
            True if room number exists, False otherwise
        """
        query = select(Room).where(
            and_(
                Room.school_id == school_id,
                Room.room_number == room_number.upper(),
                Room.deleted_at.is_(None)
            )
        )

        if exclude_id:
            query = query.where(Room.id != exclude_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_statistics(self, school_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """
        Get room statistics

        Args:
            school_id: Optional school UUID to filter by

        Returns:
            Dictionary with room statistics
        """
        # Base query
        base_query = select(Room).where(Room.deleted_at.is_(None))

        if school_id:
            base_query = base_query.where(Room.school_id == school_id)

        # Total rooms
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(total_query)
        total_rooms = total_result.scalar()

        # Active rooms
        active_query = select(func.count()).select_from(
            base_query.where(Room.is_active == True).subquery()
        )
        active_result = await self.db.execute(active_query)
        active_rooms = active_result.scalar()

        # Available rooms
        available_query = select(func.count()).select_from(
            base_query.where(
                and_(
                    Room.is_active == True,
                    Room.is_available == True
                )
            ).subquery()
        )
        available_result = await self.db.execute(available_query)
        available_rooms = available_result.scalar()

        # Rooms by type
        type_query = select(
            Room.room_type,
            func.count(Room.id).label('count')
        ).select_from(base_query.subquery()).group_by(Room.room_type)
        type_result = await self.db.execute(type_query)
        by_type = {row[0]: row[1] for row in type_result}

        # Rooms by building
        building_query = select(
            Room.building,
            func.count(Room.id).label('count')
        ).select_from(
            base_query.where(Room.building.isnot(None)).subquery()
        ).group_by(Room.building)
        building_result = await self.db.execute(building_query)
        by_building = {row[0]: row[1] for row in building_result}

        # Capacity statistics
        capacity_query = select(
            func.sum(Room.capacity).label('total_capacity'),
            func.avg(Room.capacity).label('average_capacity')
        ).select_from(base_query.subquery())
        capacity_result = await self.db.execute(capacity_query)
        capacity_row = capacity_result.first()

        # Equipment count (total number of equipment items across all rooms)
        equipment_query = select(Room).select_from(base_query.subquery())
        equipment_result = await self.db.execute(equipment_query)
        equipment_count = sum(
            len(room.equipment) if room.equipment else 0
            for room in equipment_result.scalars()
        )

        return {
            'total_rooms': total_rooms,
            'active_rooms': active_rooms,
            'inactive_rooms': total_rooms - active_rooms,
            'available_rooms': available_rooms,
            'unavailable_rooms': active_rooms - available_rooms,
            'by_type': by_type,
            'by_building': by_building,
            'total_capacity': int(capacity_row[0]) if capacity_row[0] else 0,
            'average_capacity': float(capacity_row[1]) if capacity_row[1] else 0.0,
            'equipment_count': equipment_count
        }

    async def get_rooms_with_equipment(
        self,
        school_id: uuid.UUID,
        equipment_name: str
    ) -> List[Room]:
        """
        Get rooms that have specific equipment

        Args:
            school_id: School UUID
            equipment_name: Equipment name to search for

        Returns:
            List of Room instances
        """
        result = await self.db.execute(
            select(Room).where(
                and_(
                    Room.school_id == school_id,
                    Room.equipment.contains([equipment_name]),
                    Room.deleted_at.is_(None)
                )
            ).order_by(Room.room_number)
        )
        return list(result.scalars().all())

    async def get_large_capacity_rooms(
        self,
        school_id: uuid.UUID,
        min_capacity: int = 50
    ) -> List[Room]:
        """
        Get rooms with capacity above threshold

        Args:
            school_id: School UUID
            min_capacity: Minimum capacity threshold

        Returns:
            List of Room instances
        """
        result = await self.db.execute(
            select(Room).where(
                and_(
                    Room.school_id == school_id,
                    Room.capacity >= min_capacity,
                    Room.deleted_at.is_(None)
                )
            ).order_by(Room.capacity.desc())
        )
        return list(result.scalars().all())
