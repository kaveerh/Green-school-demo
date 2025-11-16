"""
Bursary Schemas

Pydantic schemas for Bursary request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime
from enum import Enum
import uuid


# Enums
class BursaryTypeEnum(str, Enum):
    """Valid bursary types"""
    MERIT = "merit"
    NEED = "need"
    SPORTS = "sports"
    ACADEMIC = "academic"
    OTHER = "other"


class CoverageTypeEnum(str, Enum):
    """Valid coverage types"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


# Create Schema
class BursaryCreateSchema(BaseModel):
    """Schema for creating a bursary"""
    school_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    bursary_type: BursaryTypeEnum
    coverage_type: CoverageTypeEnum
    coverage_value: Decimal = Field(..., gt=0, description="Percentage (0-100) or dollar amount")
    max_coverage_amount: Optional[Decimal] = Field(None, gt=0, description="Cap for percentage-based bursaries")
    academic_year: str = Field(..., min_length=9, max_length=9, pattern=r'^\d{4}-\d{4}$')
    eligible_grades: List[int] = Field(..., min_items=1, description="List of eligible grades 1-7")
    max_recipients: Optional[int] = Field(None, gt=0, description="Max recipients, null = unlimited")
    application_deadline: Optional[date] = None
    sponsor_name: Optional[str] = Field(None, max_length=255)
    sponsor_contact: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    is_active: Optional[bool] = Field(True)


# Update Schema
class BursaryUpdateSchema(BaseModel):
    """Schema for updating a bursary"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    coverage_type: Optional[CoverageTypeEnum] = None
    coverage_value: Optional[Decimal] = Field(None, gt=0)
    max_coverage_amount: Optional[Decimal] = Field(None, gt=0)
    eligible_grades: Optional[List[int]] = Field(None, min_items=1)
    max_recipients: Optional[int] = Field(None, gt=0)
    application_deadline: Optional[date] = None
    sponsor_name: Optional[str] = Field(None, max_length=255)
    sponsor_contact: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    is_active: Optional[bool] = None


# Response Schema
class BursaryResponseSchema(BaseModel):
    """Schema for bursary response"""
    id: uuid.UUID
    school_id: uuid.UUID
    name: str
    description: Optional[str]
    bursary_type: str
    coverage_type: str
    coverage_value: float
    max_coverage_amount: Optional[float]
    academic_year: str
    eligible_grades: List[int]
    max_recipients: Optional[int]
    current_recipients: int
    is_active: bool
    application_deadline: Optional[date]
    sponsor_name: Optional[str]
    sponsor_contact: Optional[str]
    terms_and_conditions: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_percentage_based: bool
    is_fixed_amount: bool
    has_capacity: bool
    is_deadline_passed: bool
    can_accept_applications: bool

    school: Optional[dict] = None

    class Config:
        from_attributes = True


# List Response Schema
class BursaryListResponseSchema(BaseModel):
    """Schema for paginated bursary list"""
    data: list[BursaryResponseSchema]
    total: int
    page: int
    limit: int
    pages: int


# Eligibility Check Response
class BursaryEligibilitySchema(BaseModel):
    """Schema for bursary eligibility check response"""
    eligible: bool
    bursary_id: str
    bursary_name: str
    reasons: List[str]
    coverage_info: dict


# Statistics Schema
class BursaryStatisticsSchema(BaseModel):
    """Schema for bursary statistics"""
    total_bursaries: int
    active_bursaries: int
    total_recipients: int
    total_amount_distributed: float
    by_type: dict
