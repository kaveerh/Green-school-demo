"""
Class Schemas

Pydantic schemas for Class API validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import uuid


# Schedule Schema
class ScheduleSchema(BaseModel):
    """Schema for class schedule"""
    days: List[str] = Field(..., min_items=1, description="List of days (e.g., ['Monday', 'Wednesday', 'Friday'])")
    start_time: str = Field(..., pattern=r'^([01]\d|2[0-3]):([0-5]\d)$', description="Start time in HH:MM format")
    end_time: str = Field(..., pattern=r'^([01]\d|2[0-3]):([0-5]\d)$', description="End time in HH:MM format")

    @validator('days')
    def validate_days(cls, v):
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in v:
            if day not in valid_days:
                raise ValueError(f"Invalid day: {day}. Must be one of: {', '.join(valid_days)}")
        return v

    @validator('end_time')
    def validate_end_after_start(cls, v, values):
        if 'start_time' in values:
            start_hours, start_mins = map(int, values['start_time'].split(':'))
            end_hours, end_mins = map(int, v.split(':'))
            start_total = start_hours * 60 + start_mins
            end_total = end_hours * 60 + end_mins
            if end_total <= start_total:
                raise ValueError('end_time must be after start_time')
        return v


# Class Schemas
class ClassCreateSchema(BaseModel):
    """Schema for creating a class"""
    code: str = Field(..., min_length=3, max_length=50, description="Class code (e.g., MATH-5-Q1-A)")
    name: str = Field(..., min_length=1, max_length=200, description="Class name")
    subject_id: uuid.UUID = Field(..., description="Subject ID")
    teacher_id: uuid.UUID = Field(..., description="Teacher ID")
    room_id: Optional[uuid.UUID] = Field(None, description="Room ID")
    grade_level: int = Field(..., ge=1, le=7, description="Grade level (1-7)")
    quarter: str = Field(..., pattern=r'^Q[1-4]$', description="Quarter (Q1, Q2, Q3, or Q4)")
    academic_year: str = Field(..., pattern=r'^\d{4}-\d{4}$', description="Academic year (e.g., 2024-2025)")
    max_students: int = Field(..., gt=0, le=100, description="Maximum number of students")
    description: Optional[str] = Field(None, description="Class description")
    schedule: Optional[ScheduleSchema] = Field(None, description="Class schedule")
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Display color (hex)")
    display_order: int = Field(0, ge=0, description="Display order")

    @validator('code')
    def validate_code_format(cls, v):
        v = v.strip().upper()
        # Expected format: SUBJECT-GRADE-QUARTER-SECTION
        parts = v.split('-')
        if len(parts) != 4:
            raise ValueError('Code must follow format: SUBJECT-GRADE-QUARTER-SECTION (e.g., MATH-5-Q1-A)')
        return v

    @validator('quarter')
    def validate_quarter_format(cls, v):
        return v.upper()

    @validator('academic_year')
    def validate_academic_year_logic(cls, v):
        start_year, end_year = v.split('-')
        if int(end_year) != int(start_year) + 1:
            raise ValueError('Academic year end must be start year + 1 (e.g., 2024-2025)')
        return v


class ClassUpdateSchema(BaseModel):
    """Schema for updating a class"""
    code: Optional[str] = Field(None, min_length=3, max_length=50, description="Class code")
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Class name")
    subject_id: Optional[uuid.UUID] = Field(None, description="Subject ID")
    teacher_id: Optional[uuid.UUID] = Field(None, description="Teacher ID")
    room_id: Optional[uuid.UUID] = Field(None, description="Room ID")
    grade_level: Optional[int] = Field(None, ge=1, le=7, description="Grade level (1-7)")
    quarter: Optional[str] = Field(None, pattern=r'^Q[1-4]$', description="Quarter")
    academic_year: Optional[str] = Field(None, pattern=r'^\d{4}-\d{4}$', description="Academic year")
    max_students: Optional[int] = Field(None, gt=0, le=100, description="Maximum students")
    description: Optional[str] = Field(None, description="Class description")
    schedule: Optional[ScheduleSchema] = Field(None, description="Class schedule")
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Display color")
    display_order: Optional[int] = Field(None, ge=0, description="Display order")

    @validator('code')
    def validate_code_format(cls, v):
        if v is not None:
            v = v.strip().upper()
            parts = v.split('-')
            if len(parts) != 4:
                raise ValueError('Code must follow format: SUBJECT-GRADE-QUARTER-SECTION')
        return v

    @validator('quarter')
    def validate_quarter_format(cls, v):
        return v.upper() if v else v

    @validator('academic_year')
    def validate_academic_year_logic(cls, v):
        if v is not None:
            start_year, end_year = v.split('-')
            if int(end_year) != int(start_year) + 1:
                raise ValueError('Academic year end must be start year + 1')
        return v


class ClassResponseSchema(BaseModel):
    """Schema for class response"""
    id: uuid.UUID
    school_id: uuid.UUID
    code: str
    name: str
    subject_id: uuid.UUID
    teacher_id: uuid.UUID
    room_id: Optional[uuid.UUID]
    grade_level: int
    quarter: str
    academic_year: str
    max_students: int
    current_enrollment: int
    description: Optional[str]
    schedule: Optional[Dict[str, Any]]
    is_active: bool
    color: Optional[str]
    display_order: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    # Computed fields (added by to_dict())
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    teacher_name: Optional[str] = None
    room_number: Optional[str] = None
    is_full: Optional[bool] = None
    capacity_percent: Optional[float] = None
    available_seats: Optional[int] = None

    class Config:
        from_attributes = True


class ClassListResponseSchema(BaseModel):
    """Schema for paginated class list"""
    classes: List[ClassResponseSchema]
    total: int
    page: int
    limit: int
    total_pages: int


class ClassStatisticsSchema(BaseModel):
    """Schema for class statistics"""
    total_classes: int
    active_classes: int
    inactive_classes: int
    by_grade: Dict[str, int]
    by_quarter: Dict[str, int]
    by_subject: Dict[str, int]
    total_enrollment: int
    average_class_size: float
    capacity_utilization: float


# StudentClass Schemas
class StudentClassEnrollSchema(BaseModel):
    """Schema for enrolling a student in a class"""
    student_id: uuid.UUID = Field(..., description="Student ID")
    class_id: uuid.UUID = Field(..., description="Class ID")
    enrollment_date: Optional[date] = Field(None, description="Enrollment date (defaults to today)")


class StudentClassUpdateGradesSchema(BaseModel):
    """Schema for updating student grades"""
    final_grade: Optional[str] = Field(None, max_length=5, description="Final letter grade")
    final_score: Optional[float] = Field(None, ge=0, le=100, description="Final score (0-100)")


class StudentClassCompleteSchema(BaseModel):
    """Schema for completing an enrollment"""
    final_grade: Optional[str] = Field(None, max_length=5, description="Final letter grade")
    final_score: Optional[float] = Field(None, ge=0, le=100, description="Final score (0-100)")


class StudentClassResponseSchema(BaseModel):
    """Schema for student class response"""
    id: uuid.UUID
    student_id: uuid.UUID
    class_id: uuid.UUID
    enrollment_date: date
    drop_date: Optional[date]
    status: str
    final_grade: Optional[str]
    final_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    # Computed field (added by to_dict())
    student_name: Optional[str] = None

    class Config:
        from_attributes = True


class StudentClassListResponseSchema(BaseModel):
    """Schema for list of student enrollments"""
    enrollments: List[StudentClassResponseSchema]
    total: int


# Query Parameter Schemas
class ClassFilterParams(BaseModel):
    """Schema for class filter parameters"""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(50, ge=1, le=100, description="Items per page")
    subject_id: Optional[uuid.UUID] = Field(None, description="Filter by subject")
    teacher_id: Optional[uuid.UUID] = Field(None, description="Filter by teacher")
    room_id: Optional[uuid.UUID] = Field(None, description="Filter by room")
    grade_level: Optional[int] = Field(None, ge=1, le=7, description="Filter by grade")
    quarter: Optional[str] = Field(None, pattern=r'^Q[1-4]$', description="Filter by quarter")
    academic_year: Optional[str] = Field(None, pattern=r'^\d{4}-\d{4}$', description="Filter by year")
    is_active: Optional[bool] = Field(None, description="Filter by active status")

    @validator('quarter')
    def validate_quarter_format(cls, v):
        return v.upper() if v else v


class ClassSearchParams(BaseModel):
    """Schema for class search parameters"""
    query: str = Field(..., min_length=2, description="Search query (code, name, description)")
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(50, ge=1, le=100, description="Items per page")
