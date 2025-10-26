"""
Vendor Schemas

Pydantic schemas for Vendor request/response validation.
"""

from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
from datetime import date
from enum import Enum
import uuid


class VendorType(str, Enum):
    """Vendor type enum"""
    FOOD_SERVICE = "food_service"
    SUPPLIES = "supplies"
    MAINTENANCE = "maintenance"
    IT_SERVICES = "it_services"
    TRANSPORTATION = "transportation"
    EVENTS = "events"
    OTHER = "other"


class VendorStatus(str, Enum):
    """Vendor status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class VendorCreateSchema(BaseModel):
    """Schema for creating a vendor"""
    school_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None

    # Company Information
    company_name: str = Field(..., min_length=1, max_length=255)
    business_number: Optional[str] = Field(None, max_length=50)

    # Vendor Classification
    vendor_type: VendorType
    category: Optional[str] = Field(None, max_length=100)
    services_provided: Optional[List[str]] = None

    # Contact Information
    primary_contact_name: Optional[str] = Field(None, max_length=255)
    primary_contact_title: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    phone_alt: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=500)

    # Address
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field("USA", max_length=100)

    # Business Details
    description: Optional[str] = None
    certifications: Optional[List[str]] = None
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_expiry_date: Optional[date] = None

    # Contract & Financial
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    contract_value: Optional[float] = Field(None, ge=0)
    payment_terms: Optional[str] = Field(None, max_length=100)
    tax_exempt: Optional[bool] = False

    # Performance & Status
    status: VendorStatus = VendorStatus.ACTIVE
    performance_rating: Optional[float] = Field(None, ge=0, le=5)
    total_orders: Optional[int] = Field(0, ge=0)

    # Preferences
    preferred: Optional[bool] = False
    notes: Optional[str] = None

    @field_validator('performance_rating')
    @classmethod
    def validate_rating(cls, v):
        if v is not None and not (0 <= v <= 5):
            raise ValueError('Performance rating must be between 0 and 5')
        return v

    @field_validator('contract_end_date')
    @classmethod
    def validate_contract_dates(cls, v, info):
        if v and info.data.get('contract_start_date'):
            if v < info.data.get('contract_start_date'):
                raise ValueError('Contract end date must be after start date')
        return v


class VendorUpdateSchema(BaseModel):
    """Schema for updating a vendor"""
    user_id: Optional[uuid.UUID] = None

    # Company Information
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    business_number: Optional[str] = Field(None, max_length=50)

    # Vendor Classification
    vendor_type: Optional[VendorType] = None
    category: Optional[str] = Field(None, max_length=100)
    services_provided: Optional[List[str]] = None

    # Contact Information
    primary_contact_name: Optional[str] = Field(None, max_length=255)
    primary_contact_title: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    phone_alt: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=500)

    # Address
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)

    # Business Details
    description: Optional[str] = None
    certifications: Optional[List[str]] = None
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_expiry_date: Optional[date] = None

    # Contract & Financial
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    contract_value: Optional[float] = Field(None, ge=0)
    payment_terms: Optional[str] = Field(None, max_length=100)
    tax_exempt: Optional[bool] = None

    # Performance & Status
    status: Optional[VendorStatus] = None
    performance_rating: Optional[float] = Field(None, ge=0, le=5)
    total_orders: Optional[int] = Field(None, ge=0)

    # Preferences
    preferred: Optional[bool] = None
    notes: Optional[str] = None

    @field_validator('performance_rating')
    @classmethod
    def validate_rating(cls, v):
        if v is not None and not (0 <= v <= 5):
            raise ValueError('Performance rating must be between 0 and 5')
        return v


class VendorStatusUpdateSchema(BaseModel):
    """Schema for updating vendor status"""
    status: VendorStatus


class VendorRatingUpdateSchema(BaseModel):
    """Schema for updating vendor rating"""
    rating: float = Field(..., ge=0, le=5)


class VendorResponseSchema(BaseModel):
    """Schema for vendor response"""
    id: uuid.UUID
    school_id: uuid.UUID
    user_id: Optional[uuid.UUID]

    # Company Information
    company_name: str
    business_number: Optional[str]

    # Vendor Classification
    vendor_type: str
    category: Optional[str]
    services_provided: Optional[List[str]]

    # Contact Information
    primary_contact_name: Optional[str]
    primary_contact_title: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    phone_alt: Optional[str]
    website: Optional[str]

    # Address
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]

    # Business Details
    description: Optional[str]
    certifications: Optional[List[str]]
    insurance_policy_number: Optional[str]
    insurance_expiry_date: Optional[str]

    # Contract & Financial
    contract_start_date: Optional[str]
    contract_end_date: Optional[str]
    contract_value: Optional[float]
    payment_terms: Optional[str]
    tax_exempt: Optional[bool]

    # Performance & Status
    status: str
    performance_rating: Optional[float]
    total_orders: Optional[int]

    # Preferences
    preferred: Optional[bool]
    notes: Optional[str]

    # Audit
    created_at: str
    updated_at: str
    deleted_at: Optional[str]

    # Computed properties
    is_active: bool
    contract_active: bool
    contract_expiring_soon: bool
    insurance_expired: bool
    full_address: str

    model_config = {"from_attributes": True}


class VendorListResponseSchema(BaseModel):
    """Schema for paginated vendor list response"""
    vendors: List[VendorResponseSchema]
    total: int
    page: int
    limit: int
    pages: int


class VendorStatisticsSchema(BaseModel):
    """Schema for vendor statistics"""
    total_vendors: int
    by_type: dict
    by_status: dict
    active_vendors: int
    preferred_vendors: int
    average_rating: float
    total_contract_value: float
    expiring_contracts: int


class VendorAlertSchema(BaseModel):
    """Schema for vendor alerts"""
    vendor_id: str
    company_name: str
    contract_end_date: Optional[str] = None
    days_until_expiry: Optional[int] = None
    insurance_expiry_date: Optional[str] = None
    days_expired: Optional[int] = None


class VendorAlertsResponseSchema(BaseModel):
    """Schema for vendor alerts response"""
    expiring_contracts: List[dict]
    expired_insurance: List[dict]
