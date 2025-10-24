"""
Assessment Schemas

Pydantic schemas for Assessment request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import uuid


# Enums
class QuarterEnum(str, Enum):
    """Valid academic quarters"""
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"


class AssessmentTypeEnum(str, Enum):
    """Valid assessment types"""
    TEST = "test"
    QUIZ = "quiz"
    PROJECT = "project"
    ASSIGNMENT = "assignment"
    EXAM = "exam"
    PRESENTATION = "presentation"
    HOMEWORK = "homework"
    LAB = "lab"
    OTHER = "other"


class AssessmentStatusEnum(str, Enum):
    """Valid assessment statuses"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    GRADED = "graded"
    RETURNED = "returned"
    LATE = "late"
    MISSING = "missing"
    EXCUSED = "excused"


class LetterGradeEnum(str, Enum):
    """Valid letter grades"""
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    C_PLUS = "C+"
    C = "C"
    C_MINUS = "C-"
    D_PLUS = "D+"
    D = "D"
    D_MINUS = "D-"
    F = "F"


# Create Schema
class AssessmentCreateSchema(BaseModel):
    """Schema for creating an assessment"""
    school_id: uuid.UUID
    student_id: uuid.UUID
    class_id: uuid.UUID
    subject_id: uuid.UUID
    teacher_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assessment_type: AssessmentTypeEnum
    quarter: QuarterEnum
    assessment_date: date
    due_date: Optional[date] = None
    total_points: Decimal = Field(..., gt=0)
    points_earned: Optional[Decimal] = Field(None, ge=0)
    status: Optional[AssessmentStatusEnum] = AssessmentStatusEnum.PENDING
    weight: Optional[Decimal] = Field(Decimal("1.0"), ge=0, le=10)
    is_extra_credit: Optional[bool] = False
    is_makeup: Optional[bool] = False

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[date], info) -> Optional[date]:
        """Validate due date is after assessment date"""
        if v and 'assessment_date' in info.data:
            assessment_date = info.data['assessment_date']
            if v < assessment_date:
                raise ValueError('Due date must be on or after assessment date')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "school_id": "60da2256-81fc-4ca5-bf6b-467b8d371c61",
                "student_id": "c7d715a4-cca0-4133-9a6d-172d585a10e6",
                "class_id": "2e008ff4-dc05-4c6b-8059-ca92fceb3f9a",
                "subject_id": "94473bd5-c1de-4e8c-9ef3-bde10cacc143",
                "teacher_id": "fa4a570e-6ced-42e8-ab2f-beaf59b11a89",
                "title": "Chapter 5 Test",
                "description": "Test covering fractions and decimals",
                "assessment_type": "test",
                "quarter": "Q2",
                "assessment_date": "2025-11-15",
                "due_date": "2025-11-15",
                "total_points": 100.0,
                "weight": 3.0
            }
        }


# Grade Schema
class AssessmentGradeSchema(BaseModel):
    """Schema for grading an assessment"""
    points_earned: Decimal = Field(..., ge=0)
    feedback: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "points_earned": 85.5,
                "feedback": "Good work! Just review the order of operations."
            }
        }


# Update Schema
class AssessmentUpdateSchema(BaseModel):
    """Schema for updating an assessment"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    assessment_type: Optional[AssessmentTypeEnum] = None
    assessment_date: Optional[date] = None
    due_date: Optional[date] = None
    total_points: Optional[Decimal] = Field(None, gt=0)
    weight: Optional[Decimal] = Field(None, ge=0, le=10)
    status: Optional[AssessmentStatusEnum] = None
    is_extra_credit: Optional[bool] = None
    is_makeup: Optional[bool] = None


# Response Schemas
class StudentBasicSchema(BaseModel):
    """Basic student info for nested responses"""
    id: str
    student_id: str
    grade_level: int
    name: Optional[str] = None

    class Config:
        from_attributes = True


class TeacherBasicSchema(BaseModel):
    """Basic teacher info for nested responses"""
    id: str
    name: Optional[str] = None

    class Config:
        from_attributes = True


class SubjectBasicSchema(BaseModel):
    """Basic subject info for nested responses"""
    id: str
    code: str
    name: str

    class Config:
        from_attributes = True


class ClassBasicSchema(BaseModel):
    """Basic class info for nested responses"""
    id: str
    name: str
    code: str

    class Config:
        from_attributes = True


class AssessmentResponseSchema(BaseModel):
    """Schema for assessment response"""
    id: str
    school_id: str
    student_id: str
    class_id: str
    subject_id: str
    teacher_id: str
    title: str
    description: Optional[str]
    assessment_type: str
    quarter: str
    assessment_date: date
    due_date: Optional[date]
    total_points: float
    points_earned: Optional[float]
    percentage: Optional[float]
    letter_grade: Optional[str]
    status: str
    feedback: Optional[str]
    graded_at: Optional[datetime]
    returned_at: Optional[datetime]
    weight: float
    is_extra_credit: bool
    is_makeup: bool
    is_graded: bool
    is_passing: bool
    is_overdue: bool
    grade_display: str
    created_at: datetime
    updated_at: datetime

    # Nested relationships (optional)
    student: Optional[StudentBasicSchema] = None
    teacher: Optional[TeacherBasicSchema] = None
    subject: Optional[SubjectBasicSchema] = None
    class_obj: Optional[ClassBasicSchema] = Field(None, alias="class")

    class Config:
        from_attributes = True
        populate_by_name = True


class AssessmentListResponseSchema(BaseModel):
    """Schema for paginated assessment list"""
    assessments: List[AssessmentResponseSchema]
    total: int
    page: int
    limit: int


class AssessmentStatisticsSchema(BaseModel):
    """Schema for assessment statistics"""
    total_assessments: int
    graded_assessments: int
    pending_assessments: int
    average_score: float
    by_type: dict
