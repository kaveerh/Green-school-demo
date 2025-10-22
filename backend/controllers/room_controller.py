"""
Room Controller

REST API endpoints for Room operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid

from config.database import get_db
from services.room_service import RoomService
from schemas.room_schema import (
    RoomCreate,
    RoomUpdate,
    RoomStatusUpdate,
    RoomAvailabilityUpdate,
    RoomResponse,
    RoomListResponse,
    RoomStatistics
)

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("", response_model=RoomResponse, status_code=201)
async def create_room(
    room_data: RoomCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new room

    - **school_id**: School UUID (required)
    - **room_number**: Room number (required, 1-50 chars, unique per school)
    - **room_type**: Room type (required, valid enum)
    - **capacity**: Room capacity (required, positive integer)
    - **building**: Building name (optional)
    - **floor**: Floor number (optional, -2 to 10)
    - **room_name**: Descriptive name (optional)
    - **description**: Description (optional)
    - **area_sqft**: Area in square feet (optional)
    - **equipment**: Equipment list (optional)
    - **features**: Features list (optional)
    - **owner_id**: Owner user ID (optional)
    - **is_active**: Active status (default: true)
    - **is_available**: Availability (default: true)
    - **color**: Hex color (optional, #RRGGBB)
    - **icon**: Icon/emoji (optional)
    - **display_order**: Display order (default: 0)
    """
    service = RoomService(db)

    try:
        room = await service.create_room(
            school_id=room_data.school_id,
            room_number=room_data.room_number,
            building=room_data.building,
            floor=room_data.floor,
            room_type=room_data.room_type,
            room_name=room_data.room_name,
            description=room_data.description,
            capacity=room_data.capacity,
            area_sqft=room_data.area_sqft,
            equipment=room_data.equipment,
            features=room_data.features,
            owner_id=room_data.owner_id,
            is_active=room_data.is_active,
            is_available=room_data.is_available,
            color=room_data.color,
            icon=room_data.icon,
            display_order=room_data.display_order
        )

        return room.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")


@router.get("", response_model=RoomListResponse)
async def list_rooms(
    school_id: uuid.UUID = Query(..., description="School ID (required)"),
    room_type: Optional[str] = Query(None, description="Filter by room type"),
    building: Optional[str] = Query(None, description="Filter by building"),
    floor: Optional[int] = Query(None, description="Filter by floor"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    owner_id: Optional[uuid.UUID] = Query(None, description="Filter by owner"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Results per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of rooms with pagination and filters

    Returns paginated list of rooms for a school with optional filters.
    """
    service = RoomService(db)

    try:
        rooms, total = await service.get_rooms(
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

        return {
            "rooms": [room.to_dict() for room in rooms],
            "total": total,
            "page": page,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rooms: {str(e)}")


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get room by ID

    Returns a single room by its UUID.
    """
    service = RoomService(db)

    room = await service.get_room_by_id(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    return room.to_dict()


@router.get("/number/{room_number}", response_model=RoomResponse)
async def get_room_by_number(
    room_number: str,
    school_id: uuid.UUID = Query(..., description="School ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get room by room number within a school

    Returns a single room by its room number.
    Room numbers are unique within each school.
    """
    service = RoomService(db)

    room = await service.get_room_by_number(school_id, room_number)

    if not room:
        raise HTTPException(status_code=404, detail=f"Room '{room_number}' not found")

    return room.to_dict()


@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: uuid.UUID,
    room_data: RoomUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update room

    Updates an existing room. All fields are optional.
    Note: room_number cannot be changed after creation.
    """
    service = RoomService(db)

    try:
        room = await service.update_room(
            room_id=room_id,
            room_name=room_data.room_name,
            building=room_data.building,
            floor=room_data.floor,
            room_type=room_data.room_type,
            description=room_data.description,
            capacity=room_data.capacity,
            area_sqft=room_data.area_sqft,
            equipment=room_data.equipment,
            features=room_data.features,
            owner_id=room_data.owner_id,
            is_active=room_data.is_active,
            is_available=room_data.is_available,
            color=room_data.color,
            icon=room_data.icon,
            display_order=room_data.display_order
        )

        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        return room.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update room: {str(e)}")


@router.delete("/{room_id}", status_code=200)
async def delete_room(
    room_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete room (soft delete)

    Performs a soft delete by setting deleted_at timestamp.
    Room can potentially be restored by clearing deleted_at.
    """
    service = RoomService(db)

    deleted = await service.delete_room(room_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Room not found")

    return {"message": "Room deleted successfully"}


@router.patch("/{room_id}/status", response_model=RoomResponse)
async def toggle_room_status(
    room_id: uuid.UUID,
    status_data: RoomStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update room active status

    Sets the room's is_active flag.
    """
    service = RoomService(db)

    room = await service.get_room_by_id(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    try:
        room = await service.update_room(
            room_id=room_id,
            is_active=status_data.is_active
        )

        return room.to_dict()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


@router.patch("/{room_id}/availability", response_model=RoomResponse)
async def toggle_room_availability(
    room_id: uuid.UUID,
    availability_data: RoomAvailabilityUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update room availability

    Sets the room's is_available flag.
    """
    service = RoomService(db)

    room = await service.get_room_by_id(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    try:
        room = await service.update_room(
            room_id=room_id,
            is_available=availability_data.is_available
        )

        return room.to_dict()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update availability: {str(e)}")


@router.get("/type/{room_type}", response_model=List[RoomResponse])
async def get_rooms_by_type(
    room_type: str,
    school_id: uuid.UUID = Query(..., description="School ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get rooms by type

    Returns all rooms of a specific type for a school.
    Valid types: classroom, lab, gym, library, office, cafeteria
    """
    service = RoomService(db)

    try:
        rooms = await service.get_rooms_by_type(school_id, room_type)
        return [room.to_dict() for room in rooms]

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rooms: {str(e)}")


@router.get("/building/{building}", response_model=List[RoomResponse])
async def get_rooms_by_building(
    building: str,
    school_id: uuid.UUID = Query(..., description="School ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get rooms by building

    Returns all rooms in a specific building for a school.
    """
    service = RoomService(db)

    try:
        rooms = await service.get_rooms_by_building(school_id, building)
        return [room.to_dict() for room in rooms]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rooms: {str(e)}")


@router.get("/search/query", response_model=RoomListResponse)
async def search_rooms(
    q: str = Query(..., description="Search query"),
    school_id: uuid.UUID = Query(..., description="School ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Results per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search rooms

    Search rooms by room number, name, or description.
    Returns paginated results.
    """
    service = RoomService(db)

    try:
        rooms, total = await service.search_rooms(school_id, q, page, limit)

        return {
            "rooms": [room.to_dict() for room in rooms],
            "total": total,
            "page": page,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/statistics/summary", response_model=RoomStatistics)
async def get_room_statistics(
    school_id: Optional[uuid.UUID] = Query(None, description="School ID (optional)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get room statistics

    Returns comprehensive statistics about rooms.
    If school_id is provided, returns stats for that school only.
    Otherwise, returns system-wide statistics.
    """
    service = RoomService(db)

    try:
        stats = await service.get_statistics(school_id)
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")


# Additional helper endpoints

@router.get("/available/list", response_model=List[RoomResponse])
async def get_available_rooms(
    school_id: uuid.UUID = Query(..., description="School ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available rooms

    Returns all rooms that are both active and available.
    """
    service = RoomService(db)

    try:
        rooms = await service.get_available_rooms(school_id)
        return [room.to_dict() for room in rooms]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch available rooms: {str(e)}")
