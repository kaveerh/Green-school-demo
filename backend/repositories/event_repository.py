"""
Event Repository

Data access layer for Event operations with specialized queries.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from models.event import Event
from models.room import Room
from models.user import User
from repositories.base_repository import BaseRepository
from datetime import date, timedelta
import uuid


class EventRepository(BaseRepository[Event]):
    """Repository for Event data access"""

    def __init__(self, session: AsyncSession):
        super().__init__(Event, session)

    async def get_with_relationships(self, event_id: uuid.UUID) -> Optional[Event]:
        """Get event with all relationships loaded"""
        query = select(Event).where(
            and_(
                Event.id == event_id,
                Event.deleted_at.is_(None)
            )
        ).options(
            selectinload(Event.room),
            selectinload(Event.organizer),
            selectinload(Event.school)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Event], int]:
        """Get events for a school with optional filters"""
        offset = (page - 1) * limit

        # Build base conditions
        conditions = [
            Event.school_id == school_id,
            Event.deleted_at.is_(None)
        ]

        if start_date:
            conditions.append(Event.end_date >= start_date)
        if end_date:
            conditions.append(Event.start_date <= end_date)
        if event_type:
            conditions.append(Event.event_type == event_type)
        if status:
            conditions.append(Event.status == status)

        # Count query
        count_query = select(func.count(Event.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Event).where(and_(*conditions)).options(
            selectinload(Event.room),
            selectinload(Event.organizer)
        ).offset(offset).limit(limit).order_by(asc(Event.start_date), asc(Event.start_time))

        result = await self.session.execute(query)
        events = result.scalars().all()

        return list(events), total

    async def get_upcoming_events(
        self,
        school_id: uuid.UUID,
        days_ahead: int = 30,
        limit: int = 10
    ) -> List[Event]:
        """Get upcoming events for a school"""
        today = date.today()
        end_date = today + timedelta(days=days_ahead)

        conditions = [
            Event.school_id == school_id,
            Event.start_date >= today,
            Event.start_date <= end_date,
            Event.status == 'scheduled',
            Event.deleted_at.is_(None)
        ]

        query = select(Event).where(and_(*conditions)).options(
            selectinload(Event.room),
            selectinload(Event.organizer)
        ).limit(limit).order_by(asc(Event.start_date), asc(Event.start_time))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_date_range(
        self,
        school_id: uuid.UUID,
        start_date: date,
        end_date: date
    ) -> List[Event]:
        """Get all events within a date range"""
        conditions = [
            Event.school_id == school_id,
            or_(
                and_(Event.start_date >= start_date, Event.start_date <= end_date),
                and_(Event.end_date >= start_date, Event.end_date <= end_date),
                and_(Event.start_date <= start_date, Event.end_date >= end_date)
            ),
            Event.deleted_at.is_(None)
        ]

        query = select(Event).where(and_(*conditions)).options(
            selectinload(Event.room),
            selectinload(Event.organizer)
        ).order_by(asc(Event.start_date), asc(Event.start_time))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_type(
        self,
        school_id: uuid.UUID,
        event_type: str,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Event], int]:
        """Get events by type"""
        offset = (page - 1) * limit

        conditions = [
            Event.school_id == school_id,
            Event.event_type == event_type,
            Event.deleted_at.is_(None)
        ]

        # Count query
        count_query = select(func.count(Event.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Event).where(and_(*conditions)).options(
            selectinload(Event.room),
            selectinload(Event.organizer)
        ).offset(offset).limit(limit).order_by(desc(Event.start_date))

        result = await self.session.execute(query)
        events = result.scalars().all()

        return list(events), total

    async def get_by_organizer(
        self,
        organizer_id: uuid.UUID,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Event], int]:
        """Get events organized by a specific user"""
        offset = (page - 1) * limit

        conditions = [
            Event.organizer_id == organizer_id,
            Event.deleted_at.is_(None)
        ]

        # Count query
        count_query = select(func.count(Event.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Event).where(and_(*conditions)).options(
            selectinload(Event.room),
            selectinload(Event.school)
        ).offset(offset).limit(limit).order_by(desc(Event.start_date))

        result = await self.session.execute(query)
        events = result.scalars().all()

        return list(events), total

    async def get_by_room(
        self,
        room_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Event]:
        """Get events scheduled in a specific room"""
        conditions = [
            Event.room_id == room_id,
            Event.deleted_at.is_(None)
        ]

        if start_date:
            conditions.append(Event.end_date >= start_date)
        if end_date:
            conditions.append(Event.start_date <= end_date)

        query = select(Event).where(and_(*conditions)).order_by(
            asc(Event.start_date), asc(Event.start_time)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_requiring_rsvp(
        self,
        school_id: uuid.UUID,
        upcoming_only: bool = True
    ) -> List[Event]:
        """Get events that require RSVP"""
        conditions = [
            Event.school_id == school_id,
            Event.requires_rsvp == True,
            Event.deleted_at.is_(None)
        ]

        if upcoming_only:
            conditions.append(Event.start_date >= date.today())
            conditions.append(Event.status == 'scheduled')

        query = select(Event).where(and_(*conditions)).options(
            selectinload(Event.room),
            selectinload(Event.organizer)
        ).order_by(asc(Event.start_date))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_recurring_events(
        self,
        school_id: uuid.UUID
    ) -> List[Event]:
        """Get all recurring events for a school"""
        conditions = [
            Event.school_id == school_id,
            Event.is_recurring == True,
            Event.deleted_at.is_(None)
        ]

        query = select(Event).where(and_(*conditions)).options(
            selectinload(Event.room),
            selectinload(Event.organizer)
        ).order_by(asc(Event.start_date))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def check_room_conflict(
        self,
        room_id: uuid.UUID,
        start_date: date,
        end_date: date,
        start_time: Optional[Any] = None,
        end_time: Optional[Any] = None,
        exclude_event_id: Optional[uuid.UUID] = None
    ) -> Optional[Event]:
        """Check if a room is already booked for the given time period"""
        conditions = [
            Event.room_id == room_id,
            or_(
                and_(Event.start_date >= start_date, Event.start_date <= end_date),
                and_(Event.end_date >= start_date, Event.end_date <= end_date),
                and_(Event.start_date <= start_date, Event.end_date >= end_date)
            ),
            Event.status.in_(['scheduled', 'in_progress']),
            Event.deleted_at.is_(None)
        ]

        if exclude_event_id:
            conditions.append(Event.id != exclude_event_id)

        # If specific times are provided, check time overlap
        if start_time and end_time:
            conditions.append(
                or_(
                    Event.is_all_day == True,
                    and_(
                        Event.start_time.isnot(None),
                        Event.end_time.isnot(None),
                        or_(
                            and_(Event.start_time >= start_time, Event.start_time < end_time),
                            and_(Event.end_time > start_time, Event.end_time <= end_time),
                            and_(Event.start_time <= start_time, Event.end_time >= end_time)
                        )
                    )
                )
            )

        query = select(Event).where(and_(*conditions)).limit(1)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get event statistics for a school"""
        conditions = [
            Event.school_id == school_id,
            Event.deleted_at.is_(None)
        ]

        if start_date:
            conditions.append(Event.end_date >= start_date)
        if end_date:
            conditions.append(Event.start_date <= end_date)

        # Total events
        total_query = select(func.count(Event.id)).where(and_(*conditions))
        total_result = await self.session.execute(total_query)
        total_events = total_result.scalar()

        # By type
        type_query = select(
            Event.event_type,
            func.count(Event.id).label('count')
        ).where(and_(*conditions)).group_by(Event.event_type)
        type_result = await self.session.execute(type_query)
        by_type = {row[0]: row[1] for row in type_result}

        # By status
        status_query = select(
            Event.status,
            func.count(Event.id).label('count')
        ).where(and_(*conditions)).group_by(Event.status)
        status_result = await self.session.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result}

        # RSVP events
        rsvp_query = select(func.count(Event.id)).where(
            and_(*conditions + [Event.requires_rsvp == True])
        )
        rsvp_result = await self.session.execute(rsvp_query)
        rsvp_events = rsvp_result.scalar()

        # Recurring events
        recurring_query = select(func.count(Event.id)).where(
            and_(*conditions + [Event.is_recurring == True])
        )
        recurring_result = await self.session.execute(recurring_query)
        recurring_events = recurring_result.scalar()

        return {
            "total_events": total_events,
            "by_type": by_type,
            "by_status": by_status,
            "rsvp_events": rsvp_events,
            "recurring_events": recurring_events
        }
