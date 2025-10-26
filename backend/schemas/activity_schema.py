"""
Activity Schemas

Pydantic schemas for Activity and ActivityEnrollment request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum
from decimal import Decimal
import uuid


class ActivityTypeEnum(str, Enum):
    """Valid activity types"""
    SPORTS = "sports"
    CLUB = "club"
    ART = "art"
    MUSIC = "music"
    ACADEMIC = "academic"
    OTHER = "other"


class ActivityStatusEnum(str, Enum):
    """Valid activity statuses"""
    ACTIVE = "active"
    FULL = "full"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class EnrollmentStatusEnum(str, Enum):
    """Valid enrollment statuses"""
    ACTIVE = "active"
    WAITLISTED = "waitlisted"
    WITHDRAWN = "withdrawn"
    COMPLETED = "completed"


class PaymentStatusEnum(str, Enum):
    """Valid payment statuses"""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    WAIVED = "waived"


# Nested schemas for relationships
class ActivityCoordinatorSchema(BaseModel):
    """Coordinator information in activity response"""
    id: str
    name: str
    email: str

    class Config:
        from_attributes = True


class ActivityRoomSchema(BaseModel):
    """Room information in activity response"""
    id: str
    name: str
    room_number: Optional[str] = None

    class Config:
        from_attributes = True


class ActivityStudentSchema(BaseModel):
    """Student information in enrollment response"""
    id: str
    name: Optional[str] = None
    grade_level: Optional[int] = None

    class Config:
        from_attributes = True


# Activity Request Schemas
class ActivityCreateSchema(BaseModel):
    """Schema for creating a new activity"""
    school_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    activity_type: ActivityTypeEnum
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

    # Eligibility
    grade_levels: List[int] = Field(..., min_length=1, description="Array of eligible grades (1-7)")
    max_participants: Optional[int] = Field(None, gt=0)
    min_participants: Optional[int] = Field(None, gt=0)

    # Scheduling
    schedule: Optional[Dict[str, Any]] = Field(None, description="Days and times JSONB")
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    # Location
    location: Optional[str] = Field(None, max_length=255)
    room_id: Optional[uuid.UUID] = None

    # Financial
    cost: float = Field(0.00, ge=0)
    registration_fee: float = Field(0.00, ge=0)
    equipment_fee: float = Field(0.00, ge=0)

    # Requirements
    requirements: Optional[List[str]] = None
    equipment_needed: Optional[List[str]] = None
    uniform_required: bool = False

    # Contact
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    parent_info: Optional[str] = None

    # Settings
    coordinator_id: Optional[uuid.UUID] = None
    status: ActivityStatusEnum = ActivityStatusEnum.ACTIVE
    is_featured: bool = False
    registration_open: bool = True

    # Display
    photo_url: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code")

    @field_validator('grade_levels')
    @classmethod
    def validate_grade_levels(cls, v):
        """Validate grade levels are between 1 and 7"""
        for grade in v:
            if grade < 1 or grade > 7:
                raise ValueError("Grade levels must be between 1 and 7")
        return v

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        """Validate end_date is after or equal to start_date"""
        if v and 'start_date' in info.data and info.data['start_date'] and v < info.data['start_date']:
            raise ValueError("end_date must be on or after start_date")
        return v

    @field_validator('min_participants')
    @classmethod
    def validate_min_participants(cls, v, info):
        """Validate min_participants doesn't exceed max_participants"""
        if v and 'max_participants' in info.data and info.data['max_participants']:
            if v > info.data['max_participants']:
                raise ValueError("min_participants cannot exceed max_participants")
        return v


class ActivityUpdateSchema(BaseModel):
    """Schema for updating an activity"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    activity_type: Optional[ActivityTypeEnum] = None
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    grade_levels: Optional[List[int]] = None
    max_participants: Optional[int] = Field(None, gt=0)
    min_participants: Optional[int] = Field(None, gt=0)
    schedule: Optional[Dict[str, Any]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[str] = Field(None, max_length=255)
    room_id: Optional[uuid.UUID] = None
    cost: Optional[float] = Field(None, ge=0)
    registration_fee: Optional[float] = Field(None, ge=0)
    equipment_fee: Optional[float] = Field(None, ge=0)
    requirements: Optional[List[str]] = None
    equipment_needed: Optional[List[str]] = None
    uniform_required: Optional[bool] = None
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    parent_info: Optional[str] = None
    coordinator_id: Optional[uuid.UUID] = None
    status: Optional[ActivityStatusEnum] = None
    is_featured: Optional[bool] = None
    registration_open: Optional[bool] = None
    photo_url: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


# Activity Response Schema
class ActivityResponseSchema(BaseModel):
    """Schema for activity response"""
    id: str
    school_id: str
    coordinator_id: Optional[str] = None
    name: str
    code: Optional[str] = None
    activity_type: str
    category: Optional[str] = None
    description: Optional[str] = None
    grade_levels: List[int]
    max_participants: Optional[int] = None
    min_participants: Optional[int] = None
    schedule: Optional[Dict[str, Any]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    room_id: Optional[str] = None
    cost: float
    registration_fee: float
    equipment_fee: float
    requirements: Optional[List[str]] = None
    equipment_needed: Optional[List[str]] = None
    uniform_required: bool
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    parent_info: Optional[str] = None
    status: str
    is_featured: bool
    registration_open: bool
    photo_url: Optional[str] = None
    color: Optional[str] = None
    created_at: str
    updated_at: str

    # Computed fields
    total_cost: Optional[float] = None
    enrollment_count: Optional[int] = None
    available_slots: Optional[int] = None
    is_full: Optional[bool] = None
    is_active: Optional[bool] = None

    # Relationships
    coordinator: Optional[ActivityCoordinatorSchema] = None
    room: Optional[ActivityRoomSchema] = None

    class Config:
        from_attributes = True


class ActivityListResponseSchema(BaseModel):
    """Schema for paginated activity list response"""
    activities: List[ActivityResponseSchema]
    total: int
    page: int
    limit: int
    pages: int


# Enrollment Request Schemas
class EnrollmentCreateSchema(BaseModel):
    """Schema for enrolling a student in an activity"""
    student_id: uuid.UUID
    parent_consent: bool = False
    medical_clearance: bool = False
    emergency_contact_provided: bool = False


class EnrollmentWithdrawSchema(BaseModel):
    """Schema for withdrawing from an activity"""
    reason: Optional[str] = Field(None, max_length=500)


class PaymentRecordSchema(BaseModel):
    """Schema for recording a payment"""
    amount: float = Field(..., gt=0)
    payment_date: Optional[date] = None


class ConsentUpdateSchema(BaseModel):
    """Schema for updating parent consent"""
    parent_consent: bool


# Enrollment Response Schema
class EnrollmentResponseSchema(BaseModel):
    """Schema for enrollment response"""
    id: str
    activity_id: str
    student_id: str
    enrollment_date: str
    status: str
    payment_status: str
    amount_paid: float
    payment_date: Optional[str] = None
    attendance_count: int
    total_sessions: Optional[int] = None
    performance_notes: Optional[str] = None
    achievements: Optional[List[str]] = None
    parent_consent: bool
    parent_consent_date: Optional[str] = None
    medical_clearance: bool
    emergency_contact_provided: bool
    withdrawn_at: Optional[str] = None
    withdrawn_reason: Optional[str] = None
    created_at: str
    updated_at: str

    # Computed fields
    attendance_percentage: Optional[float] = None
    is_active: Optional[bool] = None
    payment_complete: Optional[bool] = None

    # Relationships
    activity: Optional[Dict[str, Any]] = None
    student: Optional[ActivityStudentSchema] = None

    class Config:
        from_attributes = True


# Roster Response Schema
class RosterResponseSchema(BaseModel):
    """Schema for activity roster response"""
    activity: ActivityResponseSchema
    active_enrollments: List[EnrollmentResponseSchema]
    waitlisted_enrollments: List[EnrollmentResponseSchema]
    total_enrolled: int
    total_waitlisted: int
    available_slots: int


# Payment Summary Schema
class PaymentSummarySchema(BaseModel):
    """Schema for activity payment summary"""
    activity_id: str
    activity_name: str
    total_expected: float
    total_collected: float
    total_outstanding: float
    payment_breakdown: Dict[str, int]


# Statistics Schemas
class ActivityStatisticsSchema(BaseModel):
    """Schema for activity statistics"""
    total_activities: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    total_enrollments: int
    average_enrollment_per_activity: float
    total_revenue: float
    total_outstanding: int
