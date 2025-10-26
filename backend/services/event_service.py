"""
Event Service

Business logic layer for Event operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.event_repository import EventRepository
from repositories.room_repository import RoomRepository
from repositories.user_repository import UserRepository
from models.event import Event
from datetime import date, time
import uuid


class EventService:
    """Service layer for Event business logic"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = EventRepository(session)
        self.room_repository = RoomRepository(session)
        self.user_repository = UserRepository(session)

    async def create_event(
        self,
        school_id: uuid.UUID,
        title: str,
        event_type: str,
        start_date: date,
        end_date: date,
        created_by_id: uuid.UUID,
        description: Optional[str] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        is_all_day: bool = False,
        location: Optional[str] = None,
        room_id: Optional[uuid.UUID] = None,
        target_audience: Optional[str] = None,
        grade_levels: Optional[List[int]] = None,
        class_ids: Optional[List[uuid.UUID]] = None,
        organizer_id: Optional[uuid.UUID] = None,
        organizer_name: Optional[str] = None,
        status: str = "scheduled",
        is_recurring: bool = False,
        recurrence_pattern: Optional[str] = None,
        recurrence_end_date: Optional[date] = None,
        requires_rsvp: bool = False,
        max_attendees: Optional[int] = None,
        color: Optional[str] = None,
        attachments: Optional[Dict] = None
    ) -> Event:
        """Create a new event"""

        # Validate dates
        if end_date < start_date:
            raise ValueError("End date must be on or after start date")

        # Validate room if provided
        if room_id:
            room = await self.room_repository.get_by_id(room_id)
            if not room:
                raise ValueError("Room not found")

            # Check for room conflicts
            conflict = await self.repository.check_room_conflict(
                room_id=room_id,
                start_date=start_date,
                end_date=end_date,
                start_time=start_time,
                end_time=end_time
            )
            if conflict:
                raise ValueError(f"Room is already booked for event '{conflict.title}' during this time")

        # Validate organizer if provided
        if organizer_id:
            organizer = await self.user_repository.get_by_id(organizer_id)
            if not organizer:
                raise ValueError("Organizer user not found")

        # Validate event type
        valid_types = ['assembly', 'exam', 'holiday', 'meeting', 'parent_conference',
                      'field_trip', 'sports', 'performance', 'workshop', 'other']
        if event_type not in valid_types:
            raise ValueError(f"Invalid event type. Must be one of: {', '.join(valid_types)}")

        # Validate status
        valid_statuses = ['scheduled', 'in_progress', 'completed', 'cancelled', 'postponed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        # Validate target audience
        if target_audience:
            valid_audiences = ['all_school', 'grade_level', 'class', 'custom']
            if target_audience not in valid_audiences:
                raise ValueError(f"Invalid target audience. Must be one of: {', '.join(valid_audiences)}")

        event_data = {
            'school_id': school_id,
            'title': title,
            'description': description,
            'event_type': event_type,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
            'is_all_day': is_all_day,
            'location': location,
            'room_id': room_id,
            'target_audience': target_audience,
            'grade_levels': grade_levels,
            'class_ids': class_ids,
            'organizer_id': organizer_id,
            'organizer_name': organizer_name,
            'status': status,
            'is_recurring': is_recurring,
            'recurrence_pattern': recurrence_pattern,
            'recurrence_end_date': recurrence_end_date,
            'requires_rsvp': requires_rsvp,
            'max_attendees': max_attendees,
            'current_attendees': 0,
            'color': color,
            'reminder_sent': False,
            'attachments': attachments
        }

        return await self.repository.create(event_data, created_by_id)

    async def update_event(
        self,
        event_id: uuid.UUID,
        updated_by_id: uuid.UUID,
        **updates
    ) -> Optional[Event]:
        """Update an event"""
        event = await self.repository.get_by_id(event_id)
        if not event:
            return None

        # Validate dates if being updated
        start_date = updates.get('start_date', event.start_date)
        end_date = updates.get('end_date', event.end_date)

        if end_date < start_date:
            raise ValueError("End date must be on or after start date")

        # Check room conflicts if room or dates are being updated
        if 'room_id' in updates or 'start_date' in updates or 'end_date' in updates:
            room_id = updates.get('room_id', event.room_id)
            if room_id:
                start_time = updates.get('start_time', event.start_time)
                end_time = updates.get('end_time', event.end_time)

                conflict = await self.repository.check_room_conflict(
                    room_id=room_id,
                    start_date=start_date,
                    end_date=end_date,
                    start_time=start_time,
                    end_time=end_time,
                    exclude_event_id=event_id
                )
                if conflict:
                    raise ValueError(f"Room is already booked for event '{conflict.title}' during this time")

        return await self.repository.update(event_id, updates, updated_by_id)

    async def cancel_event(
        self,
        event_id: uuid.UUID,
        updated_by_id: uuid.UUID
    ) -> Optional[Event]:
        """Cancel an event"""
        return await self.repository.update(
            event_id,
            {'status': 'cancelled'},
            updated_by_id
        )

    async def postpone_event(
        self,
        event_id: uuid.UUID,
        new_start_date: date,
        new_end_date: date,
        updated_by_id: uuid.UUID
    ) -> Optional[Event]:
        """Postpone an event to new dates"""
        event = await self.repository.get_by_id(event_id)
        if not event:
            return None

        if new_end_date < new_start_date:
            raise ValueError("End date must be on or after start date")

        # Check room conflicts for new dates
        if event.room_id:
            conflict = await self.repository.check_room_conflict(
                room_id=event.room_id,
                start_date=new_start_date,
                end_date=new_end_date,
                start_time=event.start_time,
                end_time=event.end_time,
                exclude_event_id=event.id
            )
            if conflict:
                raise ValueError(f"Room is already booked for event '{conflict.title}' during the new dates")

        return await self.repository.update(
            event.id,
            {
                'start_date': new_start_date,
                'end_date': new_end_date,
                'status': 'postponed'
            },
            updated_by_id
        )

    async def increment_attendees(
        self,
        event_id: uuid.UUID,
        count: int = 1
    ) -> Optional[Event]:
        """Increment the attendee count for an RSVP event"""
        event = await self.repository.get_by_id(event_id)
        if not event:
            return None

        if not event.requires_rsvp:
            raise ValueError("This event does not require RSVP")

        if event.max_attendees and (event.current_attendees + count) > event.max_attendees:
            raise ValueError("Event is at capacity")

        new_count = event.current_attendees + count
        return await self.repository.update(
            event_id,
            {'current_attendees': new_count},
            None  # No user update needed for count increment
        )

    async def decrement_attendees(
        self,
        event_id: uuid.UUID,
        count: int = 1
    ) -> Optional[Event]:
        """Decrement the attendee count for an RSVP event"""
        event = await self.repository.get_by_id(event_id)
        if not event:
            return None

        if not event.requires_rsvp:
            raise ValueError("This event does not require RSVP")

        new_count = max(0, event.current_attendees - count)
        return await self.repository.update(
            event_id,
            {'current_attendees': new_count},
            None
        )

    async def get_upcoming_events(
        self,
        school_id: uuid.UUID,
        days_ahead: int = 30,
        limit: int = 10
    ) -> List[Event]:
        """Get upcoming events"""
        return await self.repository.get_upcoming_events(school_id, days_ahead, limit)

    async def get_events_by_date_range(
        self,
        school_id: uuid.UUID,
        start_date: date,
        end_date: date
    ) -> List[Event]:
        """Get events within a date range"""
        return await self.repository.get_by_date_range(school_id, start_date, end_date)

    async def get_events_by_type(
        self,
        school_id: uuid.UUID,
        event_type: str,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Event], int]:
        """Get events by type"""
        return await self.repository.get_by_type(school_id, event_type, page, limit)

    async def delete_event(
        self,
        event_id: uuid.UUID,
        deleted_by_id: uuid.UUID
    ) -> bool:
        """Soft delete an event"""
        return await self.repository.delete(event_id, deleted_by_id)

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get event statistics"""
        return await self.repository.get_statistics(school_id, start_date, end_date)
