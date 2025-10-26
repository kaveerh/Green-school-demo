"""
Event Model

School calendar events including assemblies, exams, holidays, meetings, and more.
"""

from sqlalchemy import Column, String, Date, Time, Boolean, Integer, Text, CheckConstraint, Index, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from models.base import BaseModel
from datetime import date as date_type, time as time_type, datetime
import uuid


class Event(BaseModel):
    """Event model for school calendar management"""
    __tablename__ = "events"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(PG_UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    organizer_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Event Details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(50), nullable=False)

    # Scheduling
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    is_all_day = Column(Boolean, default=False, nullable=True)

    # Location
    location = Column(String(255), nullable=True)

    # Participants
    target_audience = Column(String(50), nullable=True)  # all_school, grade_level, class, custom
    grade_levels = Column(ARRAY(Integer), nullable=True)  # Array of grade levels
    class_ids = Column(ARRAY(PG_UUID(as_uuid=True)), nullable=True)  # Array of class IDs

    # Organization
    organizer_name = Column(String(255), nullable=True)

    # Settings
    status = Column(String(20), default="scheduled", nullable=True)
    is_recurring = Column(Boolean, default=False, nullable=True)
    recurrence_pattern = Column(String(50), nullable=True)
    recurrence_end_date = Column(Date, nullable=True)

    # Attendance Tracking
    requires_rsvp = Column(Boolean, default=False, nullable=True)
    max_attendees = Column(Integer, nullable=True)
    current_attendees = Column(Integer, default=0, nullable=True)

    # Additional Info
    color = Column(String(7), nullable=True)  # Hex color
    reminder_sent = Column(Boolean, default=False, nullable=True)
    attachments = Column(JSONB, nullable=True)

    # Relationships
    school = relationship("School", foreign_keys=[school_id])
    room = relationship("Room", foreign_keys=[room_id])
    organizer = relationship("User", foreign_keys=[organizer_id])

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "end_date >= start_date",
            name="chk_events_end_after_start"
        ),
        CheckConstraint(
            "status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'postponed')",
            name="chk_events_status"
        ),
        CheckConstraint(
            "event_type IN ('assembly', 'exam', 'holiday', 'meeting', 'parent_conference', 'field_trip', 'sports', 'performance', 'workshop', 'other')",
            name="chk_events_type"
        ),
        CheckConstraint(
            "target_audience IN ('all_school', 'grade_level', 'class', 'custom')",
            name="chk_events_target_audience"
        ),
        CheckConstraint(
            "recurrence_pattern IS NULL OR recurrence_pattern IN ('daily', 'weekly', 'monthly', 'yearly')",
            name="chk_events_recurrence_pattern"
        ),
        Index('idx_events_school_id', 'school_id'),
        Index('idx_events_start_date', 'start_date'),
        Index('idx_events_end_date', 'end_date'),
        Index('idx_events_event_type', 'event_type'),
        Index('idx_events_status', 'status'),
        Index('idx_events_target_audience', 'target_audience'),
        Index('idx_events_organizer_id', 'organizer_id'),
        Index('idx_events_room_id', 'room_id'),
        Index('idx_events_deleted_at', 'deleted_at'),
        Index('idx_events_date_range', 'school_id', 'start_date', 'end_date'),
    )

    def __repr__(self):
        return f"<Event(id={self.id}, title={self.title}, type={self.event_type}, date={self.start_date})>"

    @property
    def is_upcoming(self) -> bool:
        """Check if event is in the future"""
        if not self.start_date:
            return False
        return self.start_date > date_type.today() and self.status == 'scheduled'

    @property
    def is_ongoing(self) -> bool:
        """Check if event is currently happening"""
        if not self.start_date or not self.end_date:
            return False
        today = date_type.today()
        return self.start_date <= today <= self.end_date and self.status in ('scheduled', 'in_progress')

    @property
    def is_past(self) -> bool:
        """Check if event has ended"""
        if not self.end_date:
            return False
        return self.end_date < date_type.today() or self.status == 'completed'

    @property
    def duration_days(self) -> int:
        """Calculate event duration in days"""
        if not self.start_date or not self.end_date:
            return 0
        return (self.end_date - self.start_date).days + 1

    @property
    def has_capacity(self) -> bool:
        """Check if event has available capacity"""
        if not self.requires_rsvp or not self.max_attendees:
            return True
        return self.current_attendees < self.max_attendees

    @property
    def attendance_percentage(self) -> float:
        """Calculate attendance percentage if RSVP is required"""
        if not self.requires_rsvp or not self.max_attendees or self.max_attendees == 0:
            return 0.0
        return (self.current_attendees / self.max_attendees) * 100

    def to_dict(self, include_relationships: bool = False):
        """Convert event to dictionary"""
        data = super().to_dict()

        # Convert date/time/datetime objects to strings
        if self.start_date:
            data['start_date'] = self.start_date.isoformat()
        if self.end_date:
            data['end_date'] = self.end_date.isoformat()
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        if self.recurrence_end_date:
            data['recurrence_end_date'] = self.recurrence_end_date.isoformat()
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()

        # Add computed properties
        data['is_upcoming'] = self.is_upcoming
        data['is_ongoing'] = self.is_ongoing
        data['is_past'] = self.is_past
        data['duration_days'] = self.duration_days
        data['has_capacity'] = self.has_capacity
        data['attendance_percentage'] = self.attendance_percentage

        # Convert arrays to lists
        if self.grade_levels:
            data['grade_levels'] = list(self.grade_levels)
        if self.class_ids:
            data['class_ids'] = [str(cid) for cid in self.class_ids]

        if include_relationships:
            # Only include relationships if already loaded
            try:
                if self.room:
                    data["room"] = {
                        "id": str(self.room.id),
                        "name": self.room.name,
                        "code": self.room.code if hasattr(self.room, 'code') else None
                    }
            except:
                pass

            try:
                if self.organizer:
                    data["organizer"] = {
                        "id": str(self.organizer.id),
                        "name": f"{self.organizer.first_name} {self.organizer.last_name}",
                        "email": self.organizer.email
                    }
            except:
                pass

        return data
