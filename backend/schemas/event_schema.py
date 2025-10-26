"""
Event Schemas

Pydantic schemas for Event request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, time, datetime
from enum import Enum
import uuid


class EventTypeEnum(str, Enum):
    """Valid event types"""
    ASSEMBLY = "assembly"
    EXAM = "exam"
    HOLIDAY = "holiday"
    MEETING = "meeting"
    PARENT_CONFERENCE = "parent_conference"
    FIELD_TRIP = "field_trip"
    SPORTS = "sports"
    PERFORMANCE = "performance"
    WORKSHOP = "workshop"
    OTHER = "other"


class EventStatusEnum(str, Enum):
    """Valid event statuses"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class TargetAudienceEnum(str, Enum):
    """Valid target audiences"""
    ALL_SCHOOL = "all_school"
    GRADE_LEVEL = "grade_level"
    CLASS = "class"
    CUSTOM = "custom"


class RecurrencePatternEnum(str, Enum):
    """Valid recurrence patterns"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


# Nested schemas for relationships
class EventRoomSchema(BaseModel):
    """Room information in event response"""
    id: str
    name: str
    code: Optional[str] = None

    class Config:
        from_attributes = True


class EventOrganizerSchema(BaseModel):
    """Organizer information in event response"""
    id: str
    name: str
    email: str

    class Config:
        from_attributes = True


class EventSchoolSchema(BaseModel):
    """School information in event response"""
    id: str
    name: str

    class Config:
        from_attributes = True


# Request schemas
class EventCreateSchema(BaseModel):
    """Schema for creating a new event"""
    school_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: EventTypeEnum

    # Scheduling
    start_date: date
    end_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_all_day: bool = False

    # Location
    location: Optional[str] = Field(None, max_length=255)
    room_id: Optional[uuid.UUID] = None

    # Participants
    target_audience: Optional[TargetAudienceEnum] = None
    grade_levels: Optional[List[int]] = Field(None, description="Array of grade levels (1-7)")
    class_ids: Optional[List[uuid.UUID]] = Field(None, description="Array of class IDs")

    # Organization
    organizer_id: Optional[uuid.UUID] = None
    organizer_name: Optional[str] = Field(None, max_length=255)

    # Settings
    status: EventStatusEnum = EventStatusEnum.SCHEDULED
    is_recurring: bool = False
    recurrence_pattern: Optional[RecurrencePatternEnum] = None
    recurrence_end_date: Optional[date] = None

    # RSVP
    requires_rsvp: bool = False
    max_attendees: Optional[int] = Field(None, gt=0)

    # Additional
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code")
    attachments: Optional[Dict[str, Any]] = None

    @field_validator('grade_levels')
    @classmethod
    def validate_grade_levels(cls, v):
        """Validate grade levels are between 1 and 7"""
        if v:
            for grade in v:
                if grade < 1 or grade > 7:
                    raise ValueError("Grade levels must be between 1 and 7")
        return v

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Validate end_date is after or equal to start_date"""
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("end_date must be on or after start_date")
        return v

    @field_validator('recurrence_end_date')
    @classmethod
    def validate_recurrence_end_date(cls, v, info):
        """Validate recurrence_end_date is after start_date"""
        if v and 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("recurrence_end_date must be after start_date")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "school_id": "60da2256-81fc-4ca5-bf6b-467b8d371c61",
                "title": "Fall Assembly",
                "description": "Welcoming students back for the fall semester",
                "event_type": "assembly",
                "start_date": "2025-09-15",
                "end_date": "2025-09-15",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "is_all_day": False,
                "location": "Main Auditorium",
                "target_audience": "all_school",
                "status": "scheduled",
                "color": "#FF5733"
            }
        }


class EventUpdateSchema(BaseModel):
    """Schema for updating an event"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: Optional[EventTypeEnum] = None

    # Scheduling
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_all_day: Optional[bool] = None

    # Location
    location: Optional[str] = Field(None, max_length=255)
    room_id: Optional[uuid.UUID] = None

    # Participants
    target_audience: Optional[TargetAudienceEnum] = None
    grade_levels: Optional[List[int]] = None
    class_ids: Optional[List[uuid.UUID]] = None

    # Organization
    organizer_id: Optional[uuid.UUID] = None
    organizer_name: Optional[str] = Field(None, max_length=255)

    # Settings
    status: Optional[EventStatusEnum] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[RecurrencePatternEnum] = None
    recurrence_end_date: Optional[date] = None

    # RSVP
    requires_rsvp: Optional[bool] = None
    max_attendees: Optional[int] = Field(None, gt=0)

    # Additional
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    attachments: Optional[Dict[str, Any]] = None

    @field_validator('grade_levels')
    @classmethod
    def validate_grade_levels(cls, v):
        """Validate grade levels are between 1 and 7"""
        if v:
            for grade in v:
                if grade < 1 or grade > 7:
                    raise ValueError("Grade levels must be between 1 and 7")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Fall Assembly (Updated)",
                "start_time": "10:00:00",
                "end_time": "11:00:00"
            }
        }


class EventStatusUpdateSchema(BaseModel):
    """Schema for updating event status"""
    status: EventStatusEnum

    class Config:
        json_schema_extra = {
            "example": {
                "status": "cancelled"
            }
        }


class EventPostponeSchema(BaseModel):
    """Schema for postponing an event"""
    new_start_date: date
    new_end_date: date

    @field_validator('new_end_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Validate new_end_date is after or equal to new_start_date"""
        if 'new_start_date' in info.data and v < info.data['new_start_date']:
            raise ValueError("new_end_date must be on or after new_start_date")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "new_start_date": "2025-10-15",
                "new_end_date": "2025-10-15"
            }
        }


class EventRSVPUpdateSchema(BaseModel):
    """Schema for updating RSVP count"""
    count: int = Field(1, ge=1, description="Number of attendees to add/remove")

    class Config:
        json_schema_extra = {
            "example": {
                "count": 1
            }
        }


# Response schemas
class EventResponseSchema(BaseModel):
    """Schema for event response"""
    id: str
    school_id: str

    # Event details
    title: str
    description: Optional[str] = None
    event_type: str

    # Scheduling
    start_date: str
    end_date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_all_day: bool

    # Location
    location: Optional[str] = None
    room_id: Optional[str] = None

    # Participants
    target_audience: Optional[str] = None
    grade_levels: Optional[List[int]] = None
    class_ids: Optional[List[str]] = None

    # Organization
    organizer_id: Optional[str] = None
    organizer_name: Optional[str] = None

    # Settings
    status: str
    is_recurring: bool
    recurrence_pattern: Optional[str] = None
    recurrence_end_date: Optional[str] = None

    # RSVP
    requires_rsvp: bool
    max_attendees: Optional[int] = None
    current_attendees: int

    # Additional
    color: Optional[str] = None
    reminder_sent: bool
    attachments: Optional[Dict[str, Any]] = None

    # Computed properties
    is_upcoming: bool
    is_ongoing: bool
    is_past: bool
    duration_days: int
    has_capacity: bool
    attendance_percentage: float

    # Relationships (optional)
    room: Optional[EventRoomSchema] = None
    organizer: Optional[EventOrganizerSchema] = None
    school: Optional[EventSchoolSchema] = None

    # Audit fields
    created_at: str
    updated_at: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "school_id": "60da2256-81fc-4ca5-bf6b-467b8d371c61",
                "title": "Fall Assembly",
                "description": "Welcoming students back",
                "event_type": "assembly",
                "start_date": "2025-09-15",
                "end_date": "2025-09-15",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "is_all_day": False,
                "location": "Main Auditorium",
                "target_audience": "all_school",
                "status": "scheduled",
                "is_recurring": False,
                "requires_rsvp": False,
                "current_attendees": 0,
                "color": "#FF5733",
                "reminder_sent": False,
                "is_upcoming": True,
                "is_ongoing": False,
                "is_past": False,
                "duration_days": 1,
                "has_capacity": True,
                "attendance_percentage": 0.0,
                "created_at": "2025-10-25T10:00:00",
                "updated_at": "2025-10-25T10:00:00"
            }
        }


class EventListResponseSchema(BaseModel):
    """Schema for paginated event list response"""
    events: List[EventResponseSchema]
    total: int
    page: int
    limit: int
    pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "events": [],
                "total": 100,
                "page": 1,
                "limit": 50,
                "pages": 2
            }
        }


class EventStatisticsSchema(BaseModel):
    """Schema for event statistics"""
    total_events: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    rsvp_events: int
    recurring_events: int

    class Config:
        json_schema_extra = {
            "example": {
                "total_events": 150,
                "by_type": {
                    "assembly": 10,
                    "exam": 25,
                    "holiday": 15,
                    "meeting": 40,
                    "parent_conference": 20,
                    "field_trip": 10,
                    "sports": 15,
                    "performance": 5,
                    "workshop": 8,
                    "other": 2
                },
                "by_status": {
                    "scheduled": 50,
                    "in_progress": 5,
                    "completed": 90,
                    "cancelled": 3,
                    "postponed": 2
                },
                "rsvp_events": 30,
                "recurring_events": 20
            }
        }
