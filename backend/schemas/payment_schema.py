"""
Payment Schemas

Pydantic schemas for Payment request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime
from enum import Enum
import uuid


# Enums
class PaymentMethodEnum(str, Enum):
    """Valid payment methods"""
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    ONLINE = "online"
    OTHER = "other"


class PaymentStatusEnum(str, Enum):
    """Valid payment statuses"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


# Create Payment Schema
class PaymentCreateSchema(BaseModel):
    """Schema for creating a payment"""
    school_id: uuid.UUID
    student_fee_id: uuid.UUID
    amount: Decimal = Field(..., gt=0, description="Payment amount must be > 0")
    payment_method: PaymentMethodEnum
    payment_date: Optional[date] = None
    transaction_reference: Optional[str] = Field(None, max_length=255)
    allocation_notes: Optional[str] = None
    notes: Optional[str] = None
    auto_generate_receipt: Optional[bool] = Field(True)


# Create Pending Payment Schema
class PaymentPendingCreateSchema(BaseModel):
    """Schema for creating a pending payment"""
    school_id: uuid.UUID
    student_fee_id: uuid.UUID
    amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethodEnum
    transaction_reference: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


# Confirm Payment Schema
class PaymentConfirmSchema(BaseModel):
    """Schema for confirming a pending payment"""
    transaction_reference: Optional[str] = Field(None, max_length=255)


# Refund Payment Schema
class PaymentRefundSchema(BaseModel):
    """Schema for refunding a payment"""
    refund_reason: str = Field(..., min_length=1, description="Reason for refund")


# Update Payment Schema
class PaymentUpdateSchema(BaseModel):
    """Schema for updating a payment"""
    transaction_reference: Optional[str] = Field(None, max_length=255)
    allocation_notes: Optional[str] = None
    notes: Optional[str] = None


# Response Schema
class PaymentResponseSchema(BaseModel):
    """Schema for payment response"""
    id: uuid.UUID
    school_id: uuid.UUID
    student_fee_id: uuid.UUID
    student_id: uuid.UUID
    amount: float
    payment_date: date
    payment_method: str
    transaction_reference: Optional[str]
    receipt_number: str
    allocation_notes: Optional[str]
    status: str
    refund_reason: Optional[str]
    refunded_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_completed: bool
    is_pending: bool
    is_refunded: bool
    can_be_refunded: bool
    display_amount: str
    payment_method_display: str

    # Relationships
    student: Optional[dict] = None
    student_fee: Optional[dict] = None
    processed_by: Optional[dict] = None

    class Config:
        from_attributes = True


# List Response Schema
class PaymentListResponseSchema(BaseModel):
    """Schema for paginated payment list"""
    data: list[PaymentResponseSchema]
    total: int
    page: int
    limit: int
    pages: int


# Receipt Data Schema
class PaymentReceiptSchema(BaseModel):
    """Schema for payment receipt"""
    receipt_number: str
    payment_date: str
    payment_method: str
    amount: float
    display_amount: str
    student: dict
    fee: dict
    transaction_reference: Optional[str]
    allocation_notes: Optional[str]
    notes: Optional[str]
    processed_by: Optional[dict]
    status: str
    is_refunded: bool
    refund_reason: Optional[str]


# Revenue Report Schema
class RevenueReportSchema(BaseModel):
    """Schema for revenue report"""
    total_revenue: float
    total_payments: int
    average_payment: float
    by_payment_method: dict
    by_period: List[dict]
