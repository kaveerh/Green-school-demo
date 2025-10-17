"""
Parent Validation Schemas

Pydantic schemas for validating Parent API requests and responses.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import uuid
import re


# Enums
CONTACT_METHODS = ['email', 'phone', 'sms', 'app_notification']
RELATIONSHIP_TYPES = ['mother', 'father', 'guardian', 'stepmother', 'stepfather',
                     'grandparent', 'foster_parent', 'other']


# Base Schemas
class ParentBaseSchema(BaseModel):
    """Base schema with common fields"""
    occupation: Optional[str] = Field(None, max_length=100)
    workplace: Optional[str] = Field(None, max_length=200)
    phone_mobile: Optional[str] = Field(None, max_length=20)
    phone_work: Optional[str] = Field(None, max_length=20)
    preferred_contact_method: Optional[str] = Field(None)
    emergency_contact: Optional[bool] = Field(False)
    pickup_authorized: Optional[bool] = Field(False)
    receives_newsletter: Optional[bool] = Field(True)

    @field_validator('phone_mobile', 'phone_work')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == '':
            return None

        # Basic phone validation (can be enhanced)
        # Accepts formats like: +1-555-0123, (555) 0123, 555-0123, etc.
        phone_pattern = r'^[\d\s\-\(\)\+\.]+$'
        if not re.match(phone_pattern, v):
            raise ValueError('Invalid phone number format')

        return v

    @field_validator('preferred_contact_method')
    @classmethod
    def validate_contact_method(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None

        if v not in CONTACT_METHODS:
            raise ValueError(f'Contact method must be one of: {", ".join(CONTACT_METHODS)}')

        return v


# Create Schema
class ParentCreateSchema(ParentBaseSchema):
    """Schema for creating a parent"""
    school_id: uuid.UUID = Field(..., description="School UUID")
    user_id: uuid.UUID = Field(..., description="User account UUID (must have 'parent' persona)")


# Update Schema
class ParentUpdateSchema(ParentBaseSchema):
    """Schema for updating a parent (all fields optional)"""
    pass


# Response Schemas
class UserBasicSchema(BaseModel):
    """Basic user information for nested responses"""
    id: str
    email: str
    first_name: str
    last_name: str
    persona: str

    class Config:
        from_attributes = True


class StudentBasicSchema(BaseModel):
    """Basic student information for nested responses"""
    id: str
    student_id: str
    grade_level: int
    user: Optional[UserBasicSchema] = None

    class Config:
        from_attributes = True


class ParentStudentRelationshipSchema(BaseModel):
    """Parent-student relationship response"""
    student_id: str
    relationship_type: str
    is_primary_contact: bool
    has_legal_custody: bool
    has_pickup_permission: bool
    student: Optional[StudentBasicSchema] = None

    class Config:
        from_attributes = True


class ParentResponseSchema(BaseModel):
    """Schema for parent response"""
    id: str
    school_id: str
    user_id: str
    occupation: Optional[str] = None
    workplace: Optional[str] = None
    phone_mobile: Optional[str] = None
    phone_work: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    emergency_contact: bool
    pickup_authorized: bool
    receives_newsletter: bool
    created_at: datetime
    updated_at: datetime

    # Nested relationships
    user: Optional[UserBasicSchema] = None
    children: Optional[List[ParentStudentRelationshipSchema]] = None

    class Config:
        from_attributes = True


# List Response Schema
class ParentListResponseSchema(BaseModel):
    """Schema for paginated parent list response"""
    parents: List[ParentResponseSchema]
    total: int
    page: int
    limit: int


# Link Student Schema
class ParentStudentLinkSchema(BaseModel):
    """Schema for linking parent to student"""
    student_id: uuid.UUID = Field(..., description="Student UUID to link")
    relationship_type: str = Field(..., description="Type of relationship")
    is_primary_contact: Optional[bool] = Field(False, description="Is this the primary contact?")
    has_legal_custody: Optional[bool] = Field(True, description="Does parent have legal custody?")
    has_pickup_permission: Optional[bool] = Field(True, description="Can parent pick up student?")

    @field_validator('relationship_type')
    @classmethod
    def validate_relationship_type(cls, v: str) -> str:
        if v not in RELATIONSHIP_TYPES:
            raise ValueError(f'Relationship type must be one of: {", ".join(RELATIONSHIP_TYPES)}')
        return v


# Relationship Response Schema
class ParentStudentRelationshipResponseSchema(BaseModel):
    """Full parent-student relationship response"""
    id: str
    school_id: str
    parent_id: str
    student_id: str
    relationship_type: str
    is_primary_contact: bool
    has_legal_custody: bool
    has_pickup_permission: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Statistics Schema
class ParentStatisticsSchema(BaseModel):
    """Schema for parent statistics"""
    total_parents: int
    emergency_contacts: int
    pickup_authorized: int
    newsletter_subscribers: int
    parents_with_children: int
    parents_without_children: int


# Search Parameters Schema
class ParentSearchSchema(BaseModel):
    """Schema for parent search parameters"""
    q: str = Field(..., min_length=2, description="Search query (min 2 characters)")
    page: Optional[int] = Field(1, ge=1, description="Page number")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Results per page")
