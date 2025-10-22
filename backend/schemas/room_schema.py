"""
Room Pydantic Schemas

Request/Response validation schemas for Room API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime
import uuid


class RoomBaseSchema(BaseModel):
    """Base schema for room data"""

    room_number: str = Field(..., min_length=1, max_length=50, description="Room number (required)")
    building: Optional[str] = Field(None, max_length=100, description="Building name")
    floor: Optional[int] = Field(None, ge=-2, le=10, description="Floor number (-2 to 10)")
    room_type: str = Field(..., description="Room type (classroom, lab, gym, library, office, cafeteria)")
    room_name: Optional[str] = Field(None, max_length=200, description="Descriptive room name")
    description: Optional[str] = Field(None, description="Room description")
    capacity: int = Field(..., gt=0, description="Room capacity (must be positive)")
    area_sqft: Optional[float] = Field(None, gt=0, description="Area in square feet")
    equipment: Optional[List[str]] = Field(default_factory=list, description="List of equipment items")
    features: Optional[List[str]] = Field(default_factory=list, description="List of room features")
    owner_id: Optional[uuid.UUID] = Field(None, description="Owner user ID")
    is_active: bool = Field(default=True, description="Active status")
    is_available: bool = Field(default=True, description="Availability status")
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code (#RRGGBB)")
    icon: Optional[str] = Field(None, max_length=50, description="Icon or emoji")
    display_order: int = Field(default=0, description="Display order")

    @field_validator('room_type')
    @classmethod
    def validate_room_type(cls, v):
        """Validate room type"""
        valid_types = ['classroom', 'lab', 'gym', 'library', 'office', 'cafeteria']
        if v not in valid_types:
            raise ValueError(f'room_type must be one of: {", ".join(valid_types)}')
        return v

    @field_validator('room_number')
    @classmethod
    def validate_room_number(cls, v):
        """Validate and format room number"""
        import re
        v = v.strip().upper()
        if not re.match(r'^[A-Z0-9\s\-]+$', v):
            raise ValueError('room_number can only contain letters, numbers, spaces, and hyphens')
        return v

    class Config:
        from_attributes = True


class RoomCreateSchema(RoomBaseSchema):
    """Schema for creating a room"""

    school_id: uuid.UUID = Field(..., description="School ID (required)")


class RoomUpdateSchema(BaseModel):
    """Schema for updating a room (all fields optional)"""

    room_name: Optional[str] = Field(None, max_length=200)
    building: Optional[str] = Field(None, max_length=100)
    floor: Optional[int] = Field(None, ge=-2, le=10)
    room_type: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    area_sqft: Optional[float] = Field(None, gt=0)
    equipment: Optional[List[str]] = None
    features: Optional[List[str]] = None
    owner_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None
    is_available: Optional[bool] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    display_order: Optional[int] = None

    @field_validator('room_type')
    @classmethod
    def validate_room_type(cls, v):
        """Validate room type if provided"""
        if v is not None:
            valid_types = ['classroom', 'lab', 'gym', 'library', 'office', 'cafeteria']
            if v not in valid_types:
                raise ValueError(f'room_type must be one of: {", ".join(valid_types)}')
        return v

    class Config:
        from_attributes = True


class RoomStatusUpdateSchema(BaseModel):
    """Schema for updating room status"""

    is_active: bool = Field(..., description="Active status")


class RoomAvailabilityUpdateSchema(BaseModel):
    """Schema for updating room availability"""

    is_available: bool = Field(..., description="Availability status")


class RoomResponseSchema(BaseModel):
    """Schema for room response"""

    id: uuid.UUID
    school_id: uuid.UUID

    # Identification
    room_number: str
    building: Optional[str] = None
    floor: Optional[int] = None

    # Classification
    room_type: str
    room_name: Optional[str] = None
    description: Optional[str] = None

    # Capacity
    capacity: int
    area_sqft: Optional[float] = None
    equipment: List[str] = []
    features: List[str] = []

    # Assignment
    owner_id: Optional[uuid.UUID] = None
    owner_name: Optional[str] = None

    # Status
    is_active: bool
    is_available: bool

    # Display
    color: Optional[str] = None
    icon: Optional[str] = None
    display_order: int

    # Audit
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Computed fields
    location: Optional[str] = None
    capacity_label: Optional[str] = None
    equipment_count: Optional[int] = None

    class Config:
        from_attributes = True


class RoomListResponseSchema(BaseModel):
    """Schema for paginated room list response"""

    rooms: List[RoomResponseSchema]
    total: int
    page: int
    limit: int


class RoomStatisticsSchema(BaseModel):
    """Schema for room statistics"""

    total_rooms: int
    active_rooms: int
    inactive_rooms: int
    available_rooms: int
    unavailable_rooms: int
    by_type: Dict[str, int]
    by_building: Dict[str, int]
    total_capacity: int
    average_capacity: float
    equipment_count: int

    class Config:
        from_attributes = True


# Type aliases for clarity
RoomCreate = RoomCreateSchema
RoomUpdate = RoomUpdateSchema
RoomStatusUpdate = RoomStatusUpdateSchema
RoomAvailabilityUpdate = RoomAvailabilityUpdateSchema
RoomResponse = RoomResponseSchema
RoomListResponse = RoomListResponseSchema
RoomStatistics = RoomStatisticsSchema
