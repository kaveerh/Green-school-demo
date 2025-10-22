"""
Room Service

Business logic for Room operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple, Dict, Any
import uuid
import re

from models.room import Room
from repositories.room_repository import RoomRepository


class RoomService:
    """Service for Room business logic"""

    VALID_ROOM_TYPES = ['classroom', 'lab', 'gym', 'library', 'office', 'cafeteria']

    def __init__(self, db: AsyncSession):
        self.repository = RoomRepository(db)

    async def create_room(
        self,
        school_id: uuid.UUID,
        room_number: str,
        room_type: str,
        capacity: int,
        building: Optional[str] = None,
        floor: Optional[int] = None,
        room_name: Optional[str] = None,
        description: Optional[str] = None,
        area_sqft: Optional[float] = None,
        equipment: Optional[List[str]] = None,
        features: Optional[List[str]] = None,
        owner_id: Optional[uuid.UUID] = None,
        is_active: bool = True,
        is_available: bool = True,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        display_order: int = 0
    ) -> Room:
        """
        Create a new room with validation

        Args:
            school_id: School UUID
            room_number: Room number (required, will be uppercased)
            room_type: Room type (required, must be valid enum)
            capacity: Room capacity (required, must be positive)
            building: Building name
            floor: Floor number (-2 to 10)
            room_name: Descriptive room name
            description: Room description
            area_sqft: Area in square feet
            equipment: List of equipment items
            features: List of room features
            owner_id: Owner user ID
            is_active: Active status
            is_available: Availability status
            color: Hex color code
            icon: Icon/emoji
            display_order: Display order

        Returns:
            Created Room instance

        Raises:
            ValueError: If validation fails
        """
        # Validate and format room number
        room_number = self._validate_room_number(room_number)

        # Check for duplicate room number
        if await self.repository.room_number_exists(school_id, room_number):
            raise ValueError(f"Room number '{room_number}' already exists in this school")

        # Validate room type
        if room_type not in self.VALID_ROOM_TYPES:
            raise ValueError(
                f"Invalid room type '{room_type}'. "
                f"Must be one of: {', '.join(self.VALID_ROOM_TYPES)}"
            )

        # Validate capacity
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer")

        # Validate floor range
        if floor is not None and (floor < -2 or floor > 10):
            raise ValueError("Floor must be between -2 and 10")

        # Validate color format
        if color and not self._is_valid_hex_color(color):
            raise ValueError("Color must be in hex format (#RRGGBB)")

        # Set default color and icon if not provided
        if not color:
            color = self._get_default_color(room_type)

        if not icon:
            icon = self._get_default_icon(room_type)

        # Create room instance
        room = Room(
            school_id=school_id,
            room_number=room_number,
            building=building,
            floor=floor,
            room_type=room_type,
            room_name=room_name,
            description=description,
            capacity=capacity,
            area_sqft=area_sqft,
            equipment=equipment or [],
            features=features or [],
            owner_id=owner_id,
            is_active=is_active,
            is_available=is_available,
            color=color,
            icon=icon,
            display_order=display_order
        )

        return await self.repository.create(room)

    async def get_room_by_id(self, room_id: uuid.UUID) -> Optional[Room]:
        """
        Get room by ID

        Args:
            room_id: Room UUID

        Returns:
            Room instance or None
        """
        return await self.repository.get_by_id(room_id)

    async def get_room_by_number(
        self,
        school_id: uuid.UUID,
        room_number: str
    ) -> Optional[Room]:
        """
        Get room by room number

        Args:
            school_id: School UUID
            room_number: Room number

        Returns:
            Room instance or None
        """
        room_number = room_number.upper().strip()
        return await self.repository.get_by_number(school_id, room_number)

    async def get_rooms(
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
        Get rooms with pagination and filters

        Args:
            school_id: School UUID
            page: Page number
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
        return await self.repository.get_by_school(
            school_id=school_id,
            page=page,
            limit=limit,
            room_type=room_type,
            building=building,
            floor=floor,
            is_active=is_active,
            is_available=is_available,
            owner_id=owner_id
        )

    async def get_rooms_by_type(
        self,
        school_id: uuid.UUID,
        room_type: str
    ) -> List[Room]:
        """
        Get all rooms of a specific type

        Args:
            school_id: School UUID
            room_type: Room type

        Returns:
            List of rooms

        Raises:
            ValueError: If room type is invalid
        """
        if room_type not in self.VALID_ROOM_TYPES:
            raise ValueError(f"Invalid room type: {room_type}")

        return await self.repository.get_by_type(school_id, room_type)

    async def get_rooms_by_building(
        self,
        school_id: uuid.UUID,
        building: str
    ) -> List[Room]:
        """
        Get all rooms in a building

        Args:
            school_id: School UUID
            building: Building name

        Returns:
            List of rooms
        """
        return await self.repository.get_by_building(school_id, building)

    async def search_rooms(
        self,
        school_id: uuid.UUID,
        search_query: str,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Room], int]:
        """
        Search rooms by number, name, or description

        Args:
            school_id: School UUID
            search_query: Search query
            page: Page number
            limit: Results per page

        Returns:
            Tuple of (list of rooms, total count)
        """
        return await self.repository.search(school_id, search_query, page, limit)

    async def update_room(
        self,
        room_id: uuid.UUID,
        room_name: Optional[str] = None,
        building: Optional[str] = None,
        floor: Optional[int] = None,
        room_type: Optional[str] = None,
        description: Optional[str] = None,
        capacity: Optional[int] = None,
        area_sqft: Optional[float] = None,
        equipment: Optional[List[str]] = None,
        features: Optional[List[str]] = None,
        owner_id: Optional[uuid.UUID] = None,
        is_active: Optional[bool] = None,
        is_available: Optional[bool] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        display_order: Optional[int] = None
    ) -> Optional[Room]:
        """
        Update room

        Args:
            room_id: Room UUID
            (other fields): Optional fields to update

        Returns:
            Updated Room instance or None if not found

        Raises:
            ValueError: If validation fails
        """
        room = await self.repository.get_by_id(room_id)
        if not room:
            return None

        # Validate room type if provided
        if room_type is not None and room_type not in self.VALID_ROOM_TYPES:
            raise ValueError(f"Invalid room type: {room_type}")

        # Validate capacity if provided
        if capacity is not None and capacity <= 0:
            raise ValueError("Capacity must be a positive integer")

        # Validate floor if provided
        if floor is not None and (floor < -2 or floor > 10):
            raise ValueError("Floor must be between -2 and 10")

        # Validate color if provided
        if color is not None and not self._is_valid_hex_color(color):
            raise ValueError("Color must be in hex format (#RRGGBB)")

        # Update fields
        if room_name is not None:
            room.room_name = room_name

        if building is not None:
            room.building = building

        if floor is not None:
            room.floor = floor

        if room_type is not None:
            room.room_type = room_type

        if description is not None:
            room.description = description

        if capacity is not None:
            room.capacity = capacity

        if area_sqft is not None:
            room.area_sqft = area_sqft

        if equipment is not None:
            room.equipment = equipment

        if features is not None:
            room.features = features

        if owner_id is not None:
            room.owner_id = owner_id

        if is_active is not None:
            room.is_active = is_active

        if is_available is not None:
            room.is_available = is_available

        if color is not None:
            room.color = color

        if icon is not None:
            room.icon = icon

        if display_order is not None:
            room.display_order = display_order

        return await self.repository.update(room)

    async def delete_room(self, room_id: uuid.UUID) -> bool:
        """
        Delete room (soft delete)

        Args:
            room_id: Room UUID

        Returns:
            True if deleted, False if not found
        """
        room = await self.repository.get_by_id(room_id)
        if not room:
            return False

        await self.repository.delete(room)
        return True

    async def toggle_status(self, room_id: uuid.UUID) -> Optional[Room]:
        """
        Toggle room active status

        Args:
            room_id: Room UUID

        Returns:
            Updated Room instance or None if not found
        """
        room = await self.repository.get_by_id(room_id)
        if not room:
            return None

        room.is_active = not room.is_active
        return await self.repository.update(room)

    async def toggle_availability(self, room_id: uuid.UUID) -> Optional[Room]:
        """
        Toggle room availability

        Args:
            room_id: Room UUID

        Returns:
            Updated Room instance or None if not found
        """
        room = await self.repository.get_by_id(room_id)
        if not room:
            return None

        room.is_available = not room.is_available
        return await self.repository.update(room)

    async def get_available_rooms(self, school_id: uuid.UUID) -> List[Room]:
        """
        Get all available rooms

        Args:
            school_id: School UUID

        Returns:
            List of available rooms
        """
        return await self.repository.get_available_rooms(school_id)

    async def get_statistics(self, school_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """
        Get room statistics

        Args:
            school_id: Optional school UUID

        Returns:
            Dictionary of statistics
        """
        return await self.repository.get_statistics(school_id)

    async def get_rooms_with_equipment(
        self,
        school_id: uuid.UUID,
        equipment_name: str
    ) -> List[Room]:
        """
        Get rooms with specific equipment

        Args:
            school_id: School UUID
            equipment_name: Equipment name

        Returns:
            List of rooms
        """
        return await self.repository.get_rooms_with_equipment(school_id, equipment_name)

    async def get_large_capacity_rooms(
        self,
        school_id: uuid.UUID,
        min_capacity: int = 50
    ) -> List[Room]:
        """
        Get rooms with large capacity

        Args:
            school_id: School UUID
            min_capacity: Minimum capacity

        Returns:
            List of rooms
        """
        return await self.repository.get_large_capacity_rooms(school_id, min_capacity)

    # Helper methods

    def _validate_room_number(self, room_number: str) -> str:
        """
        Validate and format room number

        Args:
            room_number: Raw room number

        Returns:
            Formatted room number (uppercase, trimmed)

        Raises:
            ValueError: If room number is invalid
        """
        if not room_number or not room_number.strip():
            raise ValueError("Room number is required")

        room_number = room_number.strip().upper()

        if len(room_number) < 1 or len(room_number) > 50:
            raise ValueError("Room number must be between 1 and 50 characters")

        # Allow alphanumeric, hyphens, and spaces
        if not re.match(r'^[A-Z0-9\s\-]+$', room_number):
            raise ValueError("Room number can only contain letters, numbers, spaces, and hyphens")

        return room_number

    def _is_valid_hex_color(self, color: str) -> bool:
        """
        Validate hex color format

        Args:
            color: Color string

        Returns:
            True if valid hex color
        """
        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))

    def _get_default_icon(self, room_type: str) -> str:
        """
        Get default icon for room type

        Args:
            room_type: Room type

        Returns:
            Default icon emoji
        """
        icons = {
            'classroom': '🏫',
            'lab': '🔬',
            'gym': '⚽',
            'library': '📚',
            'office': '💼',
            'cafeteria': '🍽️'
        }
        return icons.get(room_type, '🏫')

    def _get_default_color(self, room_type: str) -> str:
        """
        Get default color for room type

        Args:
            room_type: Room type

        Returns:
            Default hex color
        """
        colors = {
            'classroom': '#4CAF50',
            'lab': '#9C27B0',
            'gym': '#F44336',
            'library': '#795548',
            'office': '#607D8B',
            'cafeteria': '#FF9800'
        }
        return colors.get(room_type, '#757575')
