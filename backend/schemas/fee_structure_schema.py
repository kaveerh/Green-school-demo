"""
Fee Structure Schemas

Pydantic schemas for FeeStructure request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
import uuid


# Create Schema
class FeeStructureCreateSchema(BaseModel):
    """Schema for creating a fee structure"""
    school_id: uuid.UUID
    grade_level: int = Field(..., ge=1, le=7, description="Grade level 1-7")
    academic_year: str = Field(..., min_length=9, max_length=9, pattern=r'^\d{4}-\d{4}$', description="Format: YYYY-YYYY")
    yearly_amount: Decimal = Field(..., gt=0, description="Yearly tuition amount")
    monthly_amount: Decimal = Field(..., gt=0, description="Monthly tuition amount")
    weekly_amount: Decimal = Field(..., gt=0, description="Weekly tuition amount")
    yearly_discount: Optional[Decimal] = Field(10.00, ge=0, le=100, description="Yearly payment discount %")
    monthly_discount: Optional[Decimal] = Field(5.00, ge=0, le=100, description="Monthly payment discount %")
    weekly_discount: Optional[Decimal] = Field(0.00, ge=0, le=100, description="Weekly payment discount %")
    sibling_2_discount: Optional[Decimal] = Field(10.00, ge=0, le=100, description="2nd sibling discount %")
    sibling_3_discount: Optional[Decimal] = Field(15.00, ge=0, le=100, description="3rd sibling discount %")
    sibling_4_plus_discount: Optional[Decimal] = Field(20.00, ge=0, le=100, description="4th+ sibling discount %")
    apply_sibling_to_all: Optional[bool] = Field(False, description="Apply discount to all siblings or only younger")
    is_active: Optional[bool] = Field(True, description="Active status")


# Update Schema
class FeeStructureUpdateSchema(BaseModel):
    """Schema for updating a fee structure"""
    yearly_amount: Optional[Decimal] = Field(None, gt=0)
    monthly_amount: Optional[Decimal] = Field(None, gt=0)
    weekly_amount: Optional[Decimal] = Field(None, gt=0)
    yearly_discount: Optional[Decimal] = Field(None, ge=0, le=100)
    monthly_discount: Optional[Decimal] = Field(None, ge=0, le=100)
    weekly_discount: Optional[Decimal] = Field(None, ge=0, le=100)
    sibling_2_discount: Optional[Decimal] = Field(None, ge=0, le=100)
    sibling_3_discount: Optional[Decimal] = Field(None, ge=0, le=100)
    sibling_4_plus_discount: Optional[Decimal] = Field(None, ge=0, le=100)
    apply_sibling_to_all: Optional[bool] = None
    is_active: Optional[bool] = None


# Response Schema
class FeeStructureResponseSchema(BaseModel):
    """Schema for fee structure response"""
    id: uuid.UUID
    school_id: uuid.UUID
    grade_level: int
    academic_year: str
    yearly_amount: float
    monthly_amount: float
    weekly_amount: float
    yearly_discount: float
    monthly_discount: float
    weekly_discount: float
    sibling_2_discount: float
    sibling_3_discount: float
    sibling_4_plus_discount: float
    apply_sibling_to_all: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    school: Optional[dict] = None

    class Config:
        from_attributes = True


# List Response Schema
class FeeStructureListResponseSchema(BaseModel):
    """Schema for paginated fee structure list"""
    data: list[FeeStructureResponseSchema]
    total: int
    page: int
    limit: int
    pages: int
