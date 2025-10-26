"""
Event Controller

HTTP request handlers for Event operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date
import uuid

from config.database import get_db
from services.event_service import EventService
from schemas.event_schema import (
    EventCreateSchema,
    EventUpdateSchema,
    EventResponseSchema,
    EventListResponseSchema,
    EventStatusUpdateSchema,
    EventPostponeSchema,
    EventRSVPUpdateSchema,
    EventStatisticsSchema
)

router = APIRouter(prefix="/events", tags=["events"])


def get_event_service(db: AsyncSession = Depends(get_db)) -> EventService:
    """Dependency to get EventService instance"""
    return EventService(db)


@router.post("", response_model=EventResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreateSchema,
    created_by_id: uuid.UUID = Query(..., description="ID of user creating the event"),
    service: EventService = Depends(get_event_service)
):
    """
    Create a new event

    - **school_id**: School ID (required)
    - **title**: Event title (required)
    - **event_type**: Type of event (required)
    - **start_date**: Start date (required)
    - **end_date**: End date (required)
    - **start_time**: Start time (optional)
    - **end_time**: End time (optional)
    - **location**: Event location (optional)
    - **room_id**: Room ID if in a specific room (optional)
    - **target_audience**: Who the event is for (optional)
    - **organizer_id**: Organizer user ID (optional)
    - **status**: Event status (default: scheduled)
    - **is_recurring**: Whether event recurs (default: false)
    - **requires_rsvp**: Whether RSVP is required (default: false)
    - **color**: Hex color for calendar display (optional)
    """
    try:
        event = await service.create_event(
            school_id=event_data.school_id,
            title=event_data.title,
            event_type=event_data.event_type.value,
            start_date=event_data.start_date,
            end_date=event_data.end_date,
            created_by_id=created_by_id,
            description=event_data.description,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            is_all_day=event_data.is_all_day,
            location=event_data.location,
            room_id=event_data.room_id,
            target_audience=event_data.target_audience.value if event_data.target_audience else None,
            grade_levels=event_data.grade_levels,
            class_ids=event_data.class_ids,
            organizer_id=event_data.organizer_id,
            organizer_name=event_data.organizer_name,
            status=event_data.status.value,
            is_recurring=event_data.is_recurring,
            recurrence_pattern=event_data.recurrence_pattern.value if event_data.recurrence_pattern else None,
            recurrence_end_date=event_data.recurrence_end_date,
            requires_rsvp=event_data.requires_rsvp,
            max_attendees=event_data.max_attendees,
            color=event_data.color,
            attachments=event_data.attachments
        )
        return EventResponseSchema.model_validate(event.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=EventListResponseSchema)
async def get_events(
    school_id: uuid.UUID = Query(..., description="School ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date (events ending on or after this date)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (events starting on or before this date)"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: EventService = Depends(get_event_service)
):
    """
    Get all events for a school with optional filters

    Supports filtering by:
    - Date range (start_date, end_date)
    - Event type (assembly, exam, holiday, etc.)
    - Status (scheduled, in_progress, completed, etc.)

    Returns paginated results.
    """
    try:
        events, total = await service.repository.get_by_school(
            school_id=school_id,
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            status=status,
            page=page,
            limit=limit
        )

        pages = (total + limit - 1) // limit

        return EventListResponseSchema(
            events=[EventResponseSchema.model_validate(e.to_dict(include_relationships=True)) for e in events],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/upcoming", response_model=List[EventResponseSchema])
async def get_upcoming_events(
    school_id: uuid.UUID = Query(..., description="School ID"),
    days_ahead: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of events to return"),
    service: EventService = Depends(get_event_service)
):
    """
    Get upcoming events for a school

    Returns scheduled events starting within the specified number of days.
    """
    try:
        events = await service.get_upcoming_events(school_id, days_ahead, limit)
        return [EventResponseSchema.model_validate(e.to_dict(include_relationships=True)) for e in events]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/date-range", response_model=List[EventResponseSchema])
async def get_events_by_date_range(
    school_id: uuid.UUID = Query(..., description="School ID"),
    start_date: date = Query(..., description="Start date of range"),
    end_date: date = Query(..., description="End date of range"),
    service: EventService = Depends(get_event_service)
):
    """
    Get all events within a specific date range

    Returns all events that overlap with the specified date range.
    """
    try:
        events = await service.get_events_by_date_range(school_id, start_date, end_date)
        return [EventResponseSchema.model_validate(e.to_dict(include_relationships=True)) for e in events]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/type/{event_type}", response_model=EventListResponseSchema)
async def get_events_by_type(
    event_type: str,
    school_id: uuid.UUID = Query(..., description="School ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: EventService = Depends(get_event_service)
):
    """
    Get events by type

    Valid event types: assembly, exam, holiday, meeting, parent_conference,
    field_trip, sports, performance, workshop, other
    """
    try:
        events, total = await service.get_events_by_type(school_id, event_type, page, limit)
        pages = (total + limit - 1) // limit

        return EventListResponseSchema(
            events=[EventResponseSchema.model_validate(e.to_dict(include_relationships=True)) for e in events],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/organizer/{organizer_id}", response_model=EventListResponseSchema)
async def get_events_by_organizer(
    organizer_id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: EventService = Depends(get_event_service)
):
    """
    Get events organized by a specific user

    Returns all events where the specified user is the organizer.
    """
    try:
        events, total = await service.repository.get_by_organizer(organizer_id, page, limit)
        pages = (total + limit - 1) // limit

        return EventListResponseSchema(
            events=[EventResponseSchema.model_validate(e.to_dict(include_relationships=True)) for e in events],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/room/{room_id}", response_model=List[EventResponseSchema])
async def get_events_by_room(
    room_id: uuid.UUID,
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    service: EventService = Depends(get_event_service)
):
    """
    Get events scheduled in a specific room

    Returns all events in the specified room, optionally filtered by date range.
    """
    try:
        events = await service.repository.get_by_room(room_id, start_date, end_date)
        return [EventResponseSchema.model_validate(e.to_dict(include_relationships=True)) for e in events]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/rsvp", response_model=List[EventResponseSchema])
async def get_rsvp_events(
    school_id: uuid.UUID = Query(..., description="School ID"),
    upcoming_only: bool = Query(True, description="Only return upcoming events"),
    service: EventService = Depends(get_event_service)
):
    """
    Get events that require RSVP

    Returns all events where RSVP is required, optionally filtered to only upcoming events.
    """
    try:
        events = await service.repository.get_requiring_rsvp(school_id, upcoming_only)
        return [EventResponseSchema.model_validate(e.to_dict(include_relationships=True)) for e in events]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/recurring", response_model=List[EventResponseSchema])
async def get_recurring_events(
    school_id: uuid.UUID = Query(..., description="School ID"),
    service: EventService = Depends(get_event_service)
):
    """
    Get all recurring events for a school

    Returns events that have a recurrence pattern defined.
    """
    try:
        events = await service.repository.get_recurring_events(school_id)
        return [EventResponseSchema.model_validate(e.to_dict(include_relationships=True)) for e in events]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/summary", response_model=EventStatisticsSchema)
async def get_event_statistics(
    school_id: uuid.UUID = Query(..., description="School ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    service: EventService = Depends(get_event_service)
):
    """
    Get event statistics for a school

    Returns counts by type, status, RSVP events, and recurring events.
    Optionally filtered by date range.
    """
    try:
        stats = await service.get_statistics(school_id, start_date, end_date)
        return EventStatisticsSchema(**stats)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{event_id}", response_model=EventResponseSchema)
async def get_event(
    event_id: uuid.UUID,
    service: EventService = Depends(get_event_service)
):
    """
    Get a specific event by ID

    Returns event details with all relationships loaded (room, organizer, school).
    """
    try:
        event = await service.repository.get_with_relationships(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return EventResponseSchema.model_validate(event.to_dict(include_relationships=True))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{event_id}", response_model=EventResponseSchema)
async def update_event(
    event_id: uuid.UUID,
    event_data: EventUpdateSchema,
    updated_by_id: uuid.UUID = Query(..., description="ID of user updating the event"),
    service: EventService = Depends(get_event_service)
):
    """
    Update an event

    All fields are optional. Only provided fields will be updated.
    Validates dates and checks for room conflicts if relevant fields are changed.
    """
    try:
        # Convert enums to values
        updates = event_data.model_dump(exclude_unset=True)
        if 'event_type' in updates and updates['event_type']:
            updates['event_type'] = updates['event_type'].value if hasattr(updates['event_type'], 'value') else updates['event_type']
        if 'status' in updates and updates['status']:
            updates['status'] = updates['status'].value if hasattr(updates['status'], 'value') else updates['status']
        if 'target_audience' in updates and updates['target_audience']:
            updates['target_audience'] = updates['target_audience'].value if hasattr(updates['target_audience'], 'value') else updates['target_audience']
        if 'recurrence_pattern' in updates and updates['recurrence_pattern']:
            updates['recurrence_pattern'] = updates['recurrence_pattern'].value if hasattr(updates['recurrence_pattern'], 'value') else updates['recurrence_pattern']

        event = await service.update_event(event_id, updated_by_id, **updates)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return EventResponseSchema.model_validate(event.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{event_id}/status", response_model=EventResponseSchema)
async def update_event_status(
    event_id: uuid.UUID,
    status_data: EventStatusUpdateSchema,
    updated_by_id: uuid.UUID = Query(..., description="ID of user updating the status"),
    service: EventService = Depends(get_event_service)
):
    """
    Update event status

    Valid statuses: scheduled, in_progress, completed, cancelled, postponed
    """
    try:
        event = await service.repository.update(
            event_id,
            {'status': status_data.status.value},
            updated_by_id
        )
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return EventResponseSchema.model_validate(event.to_dict(include_relationships=True))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{event_id}/postpone", response_model=EventResponseSchema)
async def postpone_event(
    event_id: uuid.UUID,
    postpone_data: EventPostponeSchema,
    updated_by_id: uuid.UUID = Query(..., description="ID of user postponing the event"),
    service: EventService = Depends(get_event_service)
):
    """
    Postpone an event to new dates

    Updates start_date and end_date, sets status to 'postponed'.
    Checks for room conflicts on the new dates.
    """
    try:
        event = await service.postpone_event(
            event_id,
            postpone_data.new_start_date,
            postpone_data.new_end_date,
            updated_by_id
        )
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return EventResponseSchema.model_validate(event.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{event_id}/rsvp/increment", response_model=EventResponseSchema)
async def increment_rsvp(
    event_id: uuid.UUID,
    rsvp_data: EventRSVPUpdateSchema,
    service: EventService = Depends(get_event_service)
):
    """
    Increment RSVP attendee count

    Only works for events that require RSVP.
    Checks capacity limits before incrementing.
    """
    try:
        event = await service.increment_attendees(event_id, rsvp_data.count)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return EventResponseSchema.model_validate(event.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{event_id}/rsvp/decrement", response_model=EventResponseSchema)
async def decrement_rsvp(
    event_id: uuid.UUID,
    rsvp_data: EventRSVPUpdateSchema,
    service: EventService = Depends(get_event_service)
):
    """
    Decrement RSVP attendee count

    Only works for events that require RSVP.
    Count will not go below 0.
    """
    try:
        event = await service.decrement_attendees(event_id, rsvp_data.count)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        return EventResponseSchema.model_validate(event.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: uuid.UUID,
    deleted_by_id: uuid.UUID = Query(..., description="ID of user deleting the event"),
    service: EventService = Depends(get_event_service)
):
    """
    Delete an event (soft delete)

    Sets deleted_at timestamp and deleted_by user ID.
    Event will no longer appear in queries.
    """
    try:
        success = await service.delete_event(event_id, deleted_by_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
