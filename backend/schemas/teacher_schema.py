"""
Teacher Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import uuid
import re


class TeacherStatusEnum(str, Enum):
    """Valid teacher statuses"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


class EmploymentTypeEnum(str, Enum):
    """Valid employment types"""
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    SUBSTITUTE = "substitute"


class EducationLevelEnum(str, Enum):
    """Valid education levels"""
    HIGH_SCHOOL = "High School"
    ASSOCIATE = "Associate"
    BACHELORS = "Bachelor's"
    MASTERS = "Master's"
    PHD = "PhD"
    OTHER = "Other"


class TeacherBaseSchema(BaseModel):
    """Base teacher schema with common fields"""
    employee_id: str = Field(..., min_length=1, max_length=50)
    hire_date: date
    department: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(default="Teacher", max_length=100)

    # Credentials
    certification_number: Optional[str] = Field(None, max_length=100)
    certification_expiry: Optional[date] = None
    education_level: Optional[EducationLevelEnum] = None
    university: Optional[str] = Field(None, max_length=200)

    # Teaching assignments
    grade_levels: List[int] = Field(default_factory=list)
    specializations: List[str] = Field(default_factory=list)

    # Employment
    employment_type: Optional[EmploymentTypeEnum] = Field(default=EmploymentTypeEnum.FULL_TIME)
    work_hours_per_week: Optional[int] = Field(default=40, ge=1, le=168)

    # Contact
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)

    # Profile
    bio: Optional[str] = None
    office_room: Optional[str] = Field(None, max_length=50)
    office_hours: Optional[Dict[str, Any]] = Field(default_factory=dict)
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator('grade_levels')
    @classmethod
    def validate_grade_levels(cls, v):
        """Validate grade levels are between 1 and 7"""
        if not v:
            return v
        for grade in v:
            if grade < 1 or grade > 7:
                raise ValueError('Grade levels must be between 1 and 7')
        return sorted(list(set(v)))  # Remove duplicates and sort

    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        """Validate employee ID format"""
        if not re.match(r'^[A-Za-z0-9-_]+$', v):
            raise ValueError('Employee ID must contain only letters, numbers, hyphens, and underscores')
        return v

    @field_validator('emergency_contact_phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Phone number must contain only digits and valid separators (+, -, spaces, parentheses)')
        return v


class TeacherCreateSchema(TeacherBaseSchema):
    """Schema for creating a new teacher"""
    user_id: uuid.UUID
    termination_date: Optional[date] = None
    salary: Optional[Decimal] = Field(None, ge=0)
    status: Optional[TeacherStatusEnum] = Field(default=TeacherStatusEnum.ACTIVE)
    is_active: Optional[bool] = Field(default=True)

    @field_validator('termination_date')
    @classmethod
    def validate_termination_date(cls, v, values):
        """Ensure termination date is after hire date"""
        if v and 'hire_date' in values.data:
            hire_date = values.data['hire_date']
            if v <= hire_date:
                raise ValueError('Termination date must be after hire date')
        return v

    @field_validator('certification_expiry')
    @classmethod
    def validate_certification_expiry(cls, v, values):
        """Ensure certification expiry is in the future"""
        if v and v < date.today():
            raise ValueError('Certification expiry must be in the future')
        return v


class TeacherUpdateSchema(BaseModel):
    """Schema for updating a teacher"""
    employee_id: Optional[str] = Field(None, min_length=1, max_length=50)
    hire_date: Optional[date] = None
    termination_date: Optional[date] = None
    department: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)

    # Credentials
    certification_number: Optional[str] = Field(None, max_length=100)
    certification_expiry: Optional[date] = None
    education_level: Optional[EducationLevelEnum] = None
    university: Optional[str] = Field(None, max_length=200)

    # Teaching assignments
    grade_levels: Optional[List[int]] = None
    specializations: Optional[List[str]] = None

    # Employment
    employment_type: Optional[EmploymentTypeEnum] = None
    salary: Optional[Decimal] = Field(None, ge=0)
    work_hours_per_week: Optional[int] = Field(None, ge=1, le=168)

    # Contact
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)

    # Profile
    bio: Optional[str] = None
    office_room: Optional[str] = Field(None, max_length=50)
    office_hours: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

    @field_validator('grade_levels')
    @classmethod
    def validate_grade_levels(cls, v):
        """Validate grade levels are between 1 and 7"""
        if v is None:
            return v
        for grade in v:
            if grade < 1 or grade > 7:
                raise ValueError('Grade levels must be between 1 and 7')
        return sorted(list(set(v)))

    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        """Validate employee ID format"""
        if v and not re.match(r'^[A-Za-z0-9-_]+$', v):
            raise ValueError('Employee ID must contain only letters, numbers, hyphens, and underscores')
        return v

    @field_validator('emergency_contact_phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Phone number must contain only digits and valid separators')
        return v


class TeacherStatusChangeSchema(BaseModel):
    """Schema for changing teacher status"""
    status: TeacherStatusEnum


class TeacherResponseSchema(TeacherBaseSchema):
    """Schema for teacher response"""
    id: uuid.UUID
    school_id: uuid.UUID
    user_id: uuid.UUID
    termination_date: Optional[date]
    salary: Optional[Decimal]
    status: TeacherStatusEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]

    # Computed fields
    is_currently_employed: Optional[bool] = None
    years_of_service: Optional[int] = None
    is_certification_valid: Optional[bool] = None
    is_full_time: Optional[bool] = None

    class Config:
        from_attributes = True


class TeacherListResponseSchema(BaseModel):
    """Schema for paginated teacher list response"""
    data: List[TeacherResponseSchema]
    pagination: Dict[str, Any]


class TeacherSearchSchema(BaseModel):
    """Schema for teacher search parameters"""
    search: Optional[str] = None
    status: Optional[TeacherStatusEnum] = None
    department: Optional[str] = None
    employment_type: Optional[EmploymentTypeEnum] = None
    grade: Optional[int] = Field(None, ge=1, le=7)
    specialization: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    sort: str = Field(default="created_at")
    order: str = Field(default="desc", pattern="^(asc|desc)$")


class TeacherStatisticsSchema(BaseModel):
    """Schema for teacher statistics"""
    total: int
    active: int
    inactive: int
    by_employment_type: Dict[str, int]
    by_department: Dict[str, int]


class TeacherGradeAssignmentSchema(BaseModel):
    """Schema for assigning grades to teacher"""
    grade_levels: List[int] = Field(..., min_items=1)

    @field_validator('grade_levels')
    @classmethod
    def validate_grade_levels(cls, v):
        """Validate grade levels are between 1 and 7"""
        for grade in v:
            if grade < 1 or grade > 7:
                raise ValueError('Grade levels must be between 1 and 7')
        return sorted(list(set(v)))


class TeacherSpecializationSchema(BaseModel):
    """Schema for managing teacher specializations"""
    specializations: List[str] = Field(..., min_items=1)

    @field_validator('specializations')
    @classmethod
    def validate_specializations(cls, v):
        """Ensure specializations are not empty"""
        return [s.strip().upper() for s in v if s.strip()]
