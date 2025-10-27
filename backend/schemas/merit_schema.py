"""
Merit Schemas

Pydantic schemas for Merit request/response validation.
"""

from pydantic import BaseModel, field_validator, Field
from typing import Optional, List
from datetime import date
from enum import Enum
import uuid


class MeritCategory(str, Enum):
    """Merit category enum"""
    ACADEMIC = "academic"
    BEHAVIOR = "behavior"
    PARTICIPATION = "participation"
    LEADERSHIP = "leadership"
    ATTENDANCE = "attendance"
    OTHER = "other"


class Quarter(str, Enum):
    """Academic quarter enum"""
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"


class MeritCreateSchema(BaseModel):
    """Schema for creating a merit"""
    school_id: uuid.UUID
    student_id: uuid.UUID
    class_id: Optional[uuid.UUID] = None
    subject_id: Optional[uuid.UUID] = None

    # Merit Details
    category: MeritCategory
    points: int = Field(..., ge=1, le=10)
    reason: str = Field(..., min_length=10)

    # Context
    quarter: Optional[Quarter] = None
    academic_year: Optional[str] = Field(None, max_length=20)
    awarded_date: Optional[date] = None

    @field_validator('points')
    @classmethod
    def validate_points(cls, v):
        if not (1 <= v <= 10):
            raise ValueError('Points must be between 1 and 10')
        return v

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Reason must be at least 10 characters')
        return v.strip()


class MeritBatchCreateSchema(BaseModel):
    """Schema for creating batch merits (class award)"""
    school_id: uuid.UUID
    student_ids: List[uuid.UUID] = Field(..., min_length=1)
    class_id: Optional[uuid.UUID] = None
    subject_id: Optional[uuid.UUID] = None

    # Merit Details
    category: MeritCategory
    points: int = Field(..., ge=1, le=10)
    reason: str = Field(..., min_length=10)

    # Context
    quarter: Optional[Quarter] = None
    academic_year: Optional[str] = Field(None, max_length=20)
    awarded_date: Optional[date] = None

    @field_validator('student_ids')
    @classmethod
    def validate_student_ids(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one student_id is required')
        return v

    @field_validator('points')
    @classmethod
    def validate_points(cls, v):
        if not (1 <= v <= 10):
            raise ValueError('Points must be between 1 and 10')
        return v


class MeritUpdateSchema(BaseModel):
    """Schema for updating a merit"""
    category: Optional[MeritCategory] = None
    points: Optional[int] = Field(None, ge=1, le=10)
    reason: Optional[str] = Field(None, min_length=10)
    quarter: Optional[Quarter] = None
    academic_year: Optional[str] = Field(None, max_length=20)

    @field_validator('points')
    @classmethod
    def validate_points(cls, v):
        if v is not None and not (1 <= v <= 10):
            raise ValueError('Points must be between 1 and 10')
        return v

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError('Reason must be at least 10 characters')
        return v.strip() if v else v


class MeritResponseSchema(BaseModel):
    """Schema for merit response"""
    id: uuid.UUID
    school_id: uuid.UUID
    student_id: uuid.UUID
    awarded_by_id: uuid.UUID
    class_id: Optional[uuid.UUID]
    subject_id: Optional[uuid.UUID]

    # Merit Details
    category: str
    points: int
    reason: str

    # Context
    quarter: Optional[str]
    academic_year: Optional[str]
    awarded_date: str

    # Metadata
    is_class_award: bool
    batch_id: Optional[uuid.UUID]

    # Audit
    created_at: str
    updated_at: str
    deleted_at: Optional[str]

    # Computed Properties
    category_display: str
    points_tier: str
    is_recent: bool

    # Optional relationships
    student: Optional[dict] = None
    awarded_by: Optional[dict] = None
    class_obj: Optional[dict] = Field(None, alias="class")
    subject: Optional[dict] = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class MeritListResponseSchema(BaseModel):
    """Schema for paginated merit list response"""
    merits: List[MeritResponseSchema]
    total: int
    page: int
    limit: int
    pages: int


class MeritSummarySchema(BaseModel):
    """Schema for student merit summary"""
    total_points: int
    by_category: dict
    by_quarter: dict
    recent_merits: List[dict]
    merit_count: int


class ClassMeritSummarySchema(BaseModel):
    """Schema for class merit summary"""
    total_points: int
    average_per_student: float
    by_category: dict
    top_students: List[dict]


class LeaderboardEntrySchema(BaseModel):
    """Schema for leaderboard entry"""
    student_id: str
    total_points: int
    merit_count: int
    rank: int


class MeritStatisticsSchema(BaseModel):
    """Schema for merit statistics"""
    total_merits: int
    total_points: int
    by_category: dict
    by_quarter: dict
    unique_students: int
    average_per_student: float
