"""
Lesson Schemas

Pydantic models for lesson request/response validation.
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID


# Base lesson fields shared across schemas
class LessonBase(BaseModel):
    """Base lesson fields"""
    title: str = Field(..., min_length=1, max_length=200, description="Lesson title")
    description: Optional[str] = Field(None, description="Lesson description")
    scheduled_date: date = Field(..., description="Date lesson is scheduled")
    duration_minutes: int = Field(default=45, ge=1, le=240, description="Lesson duration in minutes")

    # Content
    learning_objectives: Optional[List[str]] = Field(default=[], description="Learning objectives")
    materials_needed: Optional[List[str]] = Field(default=[], description="Materials needed")
    curriculum_standards: Optional[List[str]] = Field(default=[], description="Curriculum standards")

    # Lesson plan sections
    introduction: Optional[str] = Field(None, description="Introduction section")
    main_activity: Optional[str] = Field(None, description="Main activity section")
    assessment: Optional[str] = Field(None, description="Assessment section")
    homework: Optional[str] = Field(None, description="Homework section")
    notes: Optional[str] = Field(None, description="Additional notes")

    # Resources
    links: Optional[List[str]] = Field(default=[], description="Resource links")

    # Display
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Color code (#RRGGBB)")

    @validator('scheduled_date')
    def validate_scheduled_date(cls, v):
        """Validate scheduled date is reasonable"""
        if v < date(2020, 1, 1):
            raise ValueError("Scheduled date must be after 2020-01-01")
        if v > date(2099, 12, 31):
            raise ValueError("Scheduled date must be before 2100-01-01")
        return v


# Request schemas
class LessonCreateRequest(LessonBase):
    """Request schema for creating a lesson"""
    class_id: UUID = Field(..., description="Class UUID")
    teacher_id: UUID = Field(..., description="Teacher UUID")
    subject_id: UUID = Field(..., description="Subject UUID")
    lesson_number: Optional[int] = Field(None, ge=1, description="Lesson number (auto-generated if not provided)")
    is_template: bool = Field(default=False, description="Whether this is a template")
    template_id: Optional[UUID] = Field(None, description="Template this lesson was created from")

    model_config = ConfigDict(from_attributes=True)


class LessonUpdateRequest(BaseModel):
    """Request schema for updating a lesson"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=240)
    lesson_number: Optional[int] = Field(None, ge=1)

    # Content
    learning_objectives: Optional[List[str]] = None
    materials_needed: Optional[List[str]] = None
    curriculum_standards: Optional[List[str]] = None

    # Lesson plan
    introduction: Optional[str] = None
    main_activity: Optional[str] = None
    assessment: Optional[str] = None
    homework: Optional[str] = None
    notes: Optional[str] = None

    # Resources
    links: Optional[List[str]] = None

    # Display
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')

    # Relationships
    class_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    subject_id: Optional[UUID] = None

    @validator('scheduled_date')
    def validate_scheduled_date(cls, v):
        """Validate scheduled date if provided"""
        if v and v < date(2020, 1, 1):
            raise ValueError("Scheduled date must be after 2020-01-01")
        if v and v > date(2099, 12, 31):
            raise ValueError("Scheduled date must be before 2100-01-01")
        return v

    model_config = ConfigDict(from_attributes=True)


class LessonStatusUpdateRequest(BaseModel):
    """Request schema for updating lesson status"""
    status: str = Field(..., description="New status")

    @validator('status')
    def validate_status(cls, v):
        """Validate status value"""
        valid_statuses = ['draft', 'scheduled', 'in_progress', 'completed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    model_config = ConfigDict(from_attributes=True)


class LessonCompleteRequest(BaseModel):
    """Request schema for completing a lesson"""
    completion_percentage: int = Field(default=100, ge=0, le=100, description="Completion percentage")
    actual_duration_minutes: Optional[int] = Field(None, ge=1, le=240, description="Actual duration in minutes")
    reflection: Optional[str] = Field(None, description="Overall reflection")
    what_went_well: Optional[str] = Field(None, description="What went well")
    what_to_improve: Optional[str] = Field(None, description="What to improve")
    modifications_needed: Optional[str] = Field(None, description="Modifications needed for next time")

    model_config = ConfigDict(from_attributes=True)


class LessonFromTemplateRequest(BaseModel):
    """Request schema for creating lesson from template"""
    template_id: UUID = Field(..., description="Template UUID")
    class_id: UUID = Field(..., description="Class UUID")
    scheduled_date: date = Field(..., description="Date to schedule the lesson")
    lesson_number: Optional[int] = Field(None, ge=1, description="Lesson number (auto-generated if not provided)")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Override title")
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Override color")

    @validator('scheduled_date')
    def validate_scheduled_date(cls, v):
        """Validate scheduled date"""
        if v < date(2020, 1, 1):
            raise ValueError("Scheduled date must be after 2020-01-01")
        if v > date(2099, 12, 31):
            raise ValueError("Scheduled date must be before 2100-01-01")
        return v

    model_config = ConfigDict(from_attributes=True)


class LessonDuplicateRequest(BaseModel):
    """Request schema for duplicating a lesson"""
    new_scheduled_date: date = Field(..., description="New scheduled date")
    new_class_id: Optional[UUID] = Field(None, description="New class (uses original if not provided)")
    new_lesson_number: Optional[int] = Field(None, ge=1, description="New lesson number (auto-generated if not provided)")

    @validator('new_scheduled_date')
    def validate_scheduled_date(cls, v):
        """Validate new scheduled date"""
        if v < date(2020, 1, 1):
            raise ValueError("Scheduled date must be after 2020-01-01")
        if v > date(2099, 12, 31):
            raise ValueError("Scheduled date must be before 2100-01-01")
        return v

    model_config = ConfigDict(from_attributes=True)


# Response schemas
class LessonResponse(LessonBase):
    """Response schema for a single lesson"""
    id: UUID
    school_id: UUID
    class_id: UUID
    teacher_id: UUID
    subject_id: UUID
    lesson_number: int

    # Status & progress
    status: str
    completion_percentage: int
    actual_duration_minutes: Optional[int] = None

    # Reflection
    reflection: Optional[str] = None
    what_went_well: Optional[str] = None
    what_to_improve: Optional[str] = None
    modifications_needed: Optional[str] = None

    # Template
    is_template: bool
    template_id: Optional[UUID] = None

    # Attachments
    attachments: List[Dict[str, Any]] = []

    # Computed fields
    is_past_due: Optional[bool] = None
    is_upcoming: Optional[bool] = None
    is_completed: Optional[bool] = None
    duration_display: Optional[str] = None

    # Relationship data (if loaded)
    class_name: Optional[str] = None
    class_code: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    teacher_name: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LessonListResponse(BaseModel):
    """Response schema for lesson list with pagination"""
    lessons: List[LessonResponse]
    total: int
    page: int
    limit: int
    pages: int

    model_config = ConfigDict(from_attributes=True)


class LessonStatisticsResponse(BaseModel):
    """Response schema for lesson statistics"""
    total_lessons: int
    by_status: Dict[str, int] = Field(default_factory=dict, description="Lesson count by status")
    by_subject: Dict[str, int] = Field(default_factory=dict, description="Lesson count by subject")
    average_duration: Optional[float] = Field(None, description="Average planned duration in minutes")
    average_actual_duration: Optional[float] = Field(None, description="Average actual duration in minutes")
    total_teaching_minutes: int = Field(default=0, description="Total teaching minutes")
    completion_rate: Optional[float] = Field(None, description="Completion rate percentage")
    average_completion_percentage: Optional[float] = Field(None, description="Average completion percentage")

    model_config = ConfigDict(from_attributes=True)


# Query parameter schemas
class LessonQueryParams(BaseModel):
    """Query parameters for lesson list endpoint"""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=50, ge=1, le=100, description="Items per page")
    class_id: Optional[UUID] = Field(None, description="Filter by class")
    teacher_id: Optional[UUID] = Field(None, description="Filter by teacher")
    subject_id: Optional[UUID] = Field(None, description="Filter by subject")
    status: Optional[str] = Field(None, description="Filter by status")
    start_date: Optional[date] = Field(None, description="Filter by start date")
    end_date: Optional[date] = Field(None, description="Filter by end date")
    is_template: Optional[bool] = Field(None, description="Filter templates")

    @validator('status')
    def validate_status(cls, v):
        """Validate status if provided"""
        if v:
            valid_statuses = ['draft', 'scheduled', 'in_progress', 'completed', 'cancelled']
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    model_config = ConfigDict(from_attributes=True)


class LessonSearchParams(BaseModel):
    """Query parameters for lesson search endpoint"""
    query: str = Field(..., min_length=1, description="Search query")
    teacher_id: Optional[UUID] = Field(None, description="Filter by teacher")
    subject_id: Optional[UUID] = Field(None, description="Filter by subject")
    limit: int = Field(default=50, ge=1, le=100, description="Max results")

    model_config = ConfigDict(from_attributes=True)


class LessonDateRangeParams(BaseModel):
    """Query parameters for date range endpoint"""
    start_date: date = Field(..., description="Start date")
    end_date: date = Field(..., description="End date")
    teacher_id: Optional[UUID] = Field(None, description="Filter by teacher")
    class_id: Optional[UUID] = Field(None, description="Filter by class")
    subject_id: Optional[UUID] = Field(None, description="Filter by subject")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate end_date is after start_date"""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError("end_date must be after start_date")
        return v

    model_config = ConfigDict(from_attributes=True)


class LessonUpcomingParams(BaseModel):
    """Query parameters for upcoming lessons endpoint"""
    teacher_id: Optional[UUID] = Field(None, description="Filter by teacher")
    days: int = Field(default=7, ge=1, le=90, description="Number of days ahead to look")
    limit: int = Field(default=50, ge=1, le=100, description="Max results")

    model_config = ConfigDict(from_attributes=True)


class LessonTemplateParams(BaseModel):
    """Query parameters for templates endpoint"""
    teacher_id: Optional[UUID] = Field(None, description="Filter by teacher")
    subject_id: Optional[UUID] = Field(None, description="Filter by subject")

    model_config = ConfigDict(from_attributes=True)


class LessonStatisticsParams(BaseModel):
    """Query parameters for statistics endpoint"""
    teacher_id: Optional[UUID] = Field(None, description="Filter by teacher")
    start_date: Optional[date] = Field(None, description="Start date for statistics")
    end_date: Optional[date] = Field(None, description="End date for statistics")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate end_date is after start_date if both provided"""
        if v and 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError("end_date must be after start_date")
        return v

    model_config = ConfigDict(from_attributes=True)
