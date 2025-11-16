"""
Student Fee Schemas

Pydantic schemas for StudentFee request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime
from enum import Enum
import uuid


# Enums
class PaymentFrequencyEnum(str, Enum):
    """Valid payment frequencies"""
    YEARLY = "yearly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"


class FeeStatusEnum(str, Enum):
    """Valid fee statuses"""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    WAIVED = "waived"


# Calculate Preview Schema
class FeeCalculatePreviewSchema(BaseModel):
    """Schema for fee calculation preview request"""
    school_id: uuid.UUID
    student_id: uuid.UUID
    academic_year: str = Field(..., pattern=r'^\d{4}-\d{4}$')
    payment_frequency: PaymentFrequencyEnum
    bursary_id: Optional[uuid.UUID] = None
    include_activities: Optional[bool] = Field(True)
    material_fees: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    other_fees: Optional[Decimal] = Field(Decimal('0.00'), ge=0)


# Create Schema
class StudentFeeCreateSchema(BaseModel):
    """Schema for creating a student fee"""
    school_id: uuid.UUID
    student_id: uuid.UUID
    academic_year: str = Field(..., pattern=r'^\d{4}-\d{4}$')
    payment_frequency: PaymentFrequencyEnum
    bursary_id: Optional[uuid.UUID] = None
    material_fees: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    other_fees: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    notes: Optional[str] = None


# Update Schema
class StudentFeeUpdateSchema(BaseModel):
    """Schema for updating a student fee"""
    payment_frequency: Optional[PaymentFrequencyEnum] = None
    bursary_id: Optional[uuid.UUID] = None
    material_fees: Optional[Decimal] = Field(None, ge=0)
    other_fees: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    recalculate: Optional[bool] = Field(True, description="Recalculate fees after update")


# Response Schema
class StudentFeeResponseSchema(BaseModel):
    """Schema for student fee response"""
    id: uuid.UUID
    school_id: uuid.UUID
    student_id: uuid.UUID
    academic_year: str
    payment_frequency: str

    # Fee components
    base_tuition_amount: float
    activity_fees_amount: float
    material_fees_amount: float
    other_fees_amount: float

    # Discounts
    payment_discount_percent: float
    payment_discount_amount: float
    sibling_discount_percent: float
    sibling_discount_amount: float
    sibling_order: Optional[int]

    # Bursary
    bursary_id: Optional[uuid.UUID]
    bursary_amount: float

    # Totals
    total_before_discounts: float
    total_discounts: float
    total_amount_due: float
    total_paid: float
    balance_due: float

    # Status
    status: str
    due_date: Optional[date]
    last_payment_date: Optional[date]

    # Metadata
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_fully_paid: bool
    is_overdue: bool
    payment_progress_percent: float
    has_bursary: bool

    # Relationships
    student: Optional[dict] = None
    bursary: Optional[dict] = None

    class Config:
        from_attributes = True


# List Response Schema
class StudentFeeListResponseSchema(BaseModel):
    """Schema for paginated student fee list"""
    data: list[StudentFeeResponseSchema]
    total: int
    page: int
    limit: int
    pages: int


# Fee Preview Response Schema
class FeePreviewResponseSchema(BaseModel):
    """Schema for fee calculation preview response"""
    student_id: str
    student_name: str
    grade_level: int
    academic_year: str
    payment_frequency: str
    sibling_order: int

    # Fee breakdown
    base_tuition: float
    activity_fees: float
    material_fees: float
    other_fees: float
    total_before_discounts: float

    # Discounts
    payment_discount: dict
    sibling_discount: dict
    total_discounts: float

    # After discounts
    total_after_discounts: float

    # Bursary
    bursary: Optional[dict]
    bursary_amount: float

    # Final
    total_amount_due: float
    balance_due: float
    due_date: Optional[str]

    # Additional info
    activities: List[dict]
    fee_structure_id: str


# Statistics Schema
class StudentFeeStatisticsSchema(BaseModel):
    """Schema for student fee statistics"""
    total_student_fees: int
    by_status: dict
    total_before_discounts: float
    total_discounts: float
    total_bursary_amount: float
    total_amount_due: float
    total_paid: float
    total_balance_due: float
    collection_rate: float
    by_payment_frequency: dict
