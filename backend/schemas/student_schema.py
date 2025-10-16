"""
Student Schemas
Pydantic schemas for student request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from enum import Enum
import uuid


class StudentStatusEnum(str, Enum):
    """Valid student statuses"""
    ENROLLED = "enrolled"
    GRADUATED = "graduated"
    TRANSFERRED = "transferred"
    WITHDRAWN = "withdrawn"
    SUSPENDED = "suspended"


class GenderEnum(str, Enum):
    """Valid gender values"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class RelationshipTypeEnum(str, Enum):
    """Valid parent-student relationship types"""
    MOTHER = "mother"
    FATHER = "father"
    GUARDIAN = "guardian"
    GRANDPARENT = "grandparent"
    OTHER = "other"


# Student Schemas
class StudentCreateSchema(BaseModel):
    """Schema for creating a new student"""
    school_id: uuid.UUID
    user_id: uuid.UUID
    student_id: str = Field(..., min_length=1, max_length=50)
    grade_level: int = Field(..., ge=1, le=7)
    date_of_birth: date
    gender: Optional[GenderEnum] = None
    enrollment_date: date
    graduation_date: Optional[date] = None
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relation: Optional[str] = Field(None, max_length=50)
    photo_url: Optional[str] = Field(None, max_length=500)
    status: Optional[StudentStatusEnum] = StudentStatusEnum.ENROLLED

    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v: date) -> date:
        """Validate date of birth is in the past"""
        if v >= date.today():
            raise ValueError('Date of birth must be in the past')
        return v

    @field_validator('enrollment_date')
    @classmethod
    def validate_enrollment_date(cls, v: date) -> date:
        """Validate enrollment date is reasonable"""
        if v > date.today():
            raise ValueError('Enrollment date cannot be in the future')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "school_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "student_id": "STU001",
                "grade_level": 3,
                "date_of_birth": "2015-06-15",
                "gender": "male",
                "enrollment_date": "2023-09-01",
                "emergency_contact_name": "Jane Doe",
                "emergency_contact_phone": "+1234567890",
                "emergency_contact_relation": "mother"
            }
        }


class StudentUpdateSchema(BaseModel):
    """Schema for updating a student"""
    grade_level: Optional[int] = Field(None, ge=1, le=7)
    gender: Optional[GenderEnum] = None
    graduation_date: Optional[date] = None
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relation: Optional[str] = Field(None, max_length=50)
    photo_url: Optional[str] = Field(None, max_length=500)
    status: Optional[StudentStatusEnum] = None

    class Config:
        json_schema_extra = {
            "example": {
                "grade_level": 4,
                "emergency_contact_phone": "+1234567891"
            }
        }


class StudentSearchSchema(BaseModel):
    """Schema for searching students"""
    search: Optional[str] = None
    grade_level: Optional[int] = Field(None, ge=1, le=7)
    status: Optional[StudentStatusEnum] = None
    gender: Optional[GenderEnum] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    sort: str = Field("created_at")
    order: str = Field("desc", pattern="^(asc|desc)$")


class StudentStatusChangeSchema(BaseModel):
    """Schema for changing student status"""
    status: StudentStatusEnum

    class Config:
        json_schema_extra = {
            "example": {
                "status": "graduated"
            }
        }


class StudentResponseSchema(BaseModel):
    """Schema for student response"""
    id: uuid.UUID
    school_id: uuid.UUID
    user_id: uuid.UUID
    student_id: str
    grade_level: int
    date_of_birth: date
    gender: Optional[str]
    enrollment_date: date
    graduation_date: Optional[date]
    allergies: Optional[str]
    medical_notes: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relation: Optional[str]
    photo_url: Optional[str]
    status: str
    is_currently_enrolled: Optional[bool]
    age: Optional[int]
    years_enrolled: Optional[int]
    can_promote: Optional[bool]
    created_at: str
    updated_at: str
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]

    class Config:
        from_attributes = True


class StudentListResponseSchema(BaseModel):
    """Schema for paginated student list response"""
    data: List[StudentResponseSchema]
    pagination: dict


class StudentStatisticsSchema(BaseModel):
    """Schema for student statistics"""
    total: int
    by_status: dict
    by_grade_level: dict
    by_gender: dict
    currently_enrolled: int
    average_age: float


# Parent-Student Relationship Schemas
class ParentStudentLinkSchema(BaseModel):
    """Schema for linking parent to student"""
    parent_id: uuid.UUID
    student_id: uuid.UUID
    relationship_type: RelationshipTypeEnum
    is_primary_contact: bool = False
    has_pickup_permission: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "parent_id": "123e4567-e89b-12d3-a456-426614174002",
                "student_id": "123e4567-e89b-12d3-a456-426614174003",
                "relationship_type": "mother",
                "is_primary_contact": True,
                "has_pickup_permission": True
            }
        }


class ParentStudentRelationshipResponseSchema(BaseModel):
    """Schema for parent-student relationship response"""
    id: uuid.UUID
    parent_id: uuid.UUID
    student_id: uuid.UUID
    relationship_type: str
    is_primary_contact: bool
    has_pickup_permission: bool
    created_at: str

    class Config:
        from_attributes = True


class ParentStudentRelationshipListSchema(BaseModel):
    """Schema for list of parent-student relationships"""
    data: List[ParentStudentRelationshipResponseSchema]
