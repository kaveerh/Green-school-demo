"""
Activity Fee Schemas

Pydantic schemas for ActivityFee request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum
import uuid


# Enums
class FeeFrequencyEnum(str, Enum):
    """Valid fee frequencies"""
    ONE_TIME = "one_time"
    YEARLY = "yearly"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"


# Create Schema
class ActivityFeeCreateSchema(BaseModel):
    """Schema for creating an activity fee"""
    school_id: uuid.UUID
    activity_id: uuid.UUID
    academic_year: str = Field(..., pattern=r'^\d{4}-\d{4}$')
    fee_amount: Decimal = Field(..., ge=0, description="Fee amount, 0 for free activities")
    fee_frequency: FeeFrequencyEnum
    allow_prorate: Optional[bool] = Field(True)
    prorate_calculation: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = Field(True)


# Update Schema
class ActivityFeeUpdateSchema(BaseModel):
    """Schema for updating an activity fee"""
    fee_amount: Optional[Decimal] = Field(None, ge=0)
    fee_frequency: Optional[FeeFrequencyEnum] = None
    allow_prorate: Optional[bool] = None
    prorate_calculation: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# Response Schema
class ActivityFeeResponseSchema(BaseModel):
    """Schema for activity fee response"""
    id: uuid.UUID
    school_id: uuid.UUID
    activity_id: uuid.UUID
    academic_year: str
    fee_amount: float
    fee_frequency: str
    allow_prorate: bool
    prorate_calculation: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_one_time: bool
    is_recurring: bool
    can_prorate: bool
    display_frequency: str
    annual_cost: float

    # Relationships
    activity: Optional[dict] = None
    school: Optional[dict] = None

    class Config:
        from_attributes = True


# List Response Schema
class ActivityFeeListResponseSchema(BaseModel):
    """Schema for paginated activity fee list"""
    data: list[ActivityFeeResponseSchema]
    total: int
    page: int
    limit: int
    pages: int


# Prorated Fee Calculation Response
class ProratedFeeResponseSchema(BaseModel):
    """Schema for prorated fee calculation response"""
    activity_fee_id: str
    original_amount: float
    fee_frequency: str
    can_prorate: bool
    months_remaining: int
    prorated_amount: float
    savings: float


# Student Activity Fees Response
class StudentActivityFeesResponseSchema(BaseModel):
    """Schema for student's total activity fees"""
    total_activity_fees: float
    activity_count: int
    activities: List[dict]


# Statistics Schema
class ActivityFeeStatisticsSchema(BaseModel):
    """Schema for activity fee statistics"""
    total_activity_fees: int
    active_activity_fees: int
    average_fee_amount: float
    by_frequency: dict
