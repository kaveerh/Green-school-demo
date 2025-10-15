"""
School Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import re


class StatusEnum(str, Enum):
    """Valid school statuses"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class SchoolBaseSchema(BaseModel):
    """Base school schema with common fields"""
    name: str = Field(..., min_length=2, max_length=255)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default="USA", max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website_url: Optional[str] = Field(None, max_length=500)
    facebook_url: Optional[str] = Field(None, max_length=500)
    twitter_url: Optional[str] = Field(None, max_length=500)
    instagram_url: Optional[str] = Field(None, max_length=500)
    timezone: str = Field(default="America/New_York", max_length=50)
    locale: str = Field(default="en_US", max_length=10)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Phone number must contain only digits and valid separators (+, -, spaces, parentheses)')
        return v

    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v):
        """Validate postal code format"""
        if v and not re.match(r'^[A-Za-z0-9\s-]+$', v):
            raise ValueError('Postal code contains invalid characters')
        return v

    @field_validator('website_url', 'facebook_url', 'twitter_url', 'instagram_url')
    @classmethod
    def validate_url(cls, v):
        """Validate URL format"""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class SchoolCreateSchema(SchoolBaseSchema):
    """Schema for creating a new school"""
    slug: Optional[str] = Field(None, min_length=2, max_length=255, pattern="^[a-z0-9-]+$")
    principal_id: Optional[uuid.UUID] = None
    hod_id: Optional[uuid.UUID] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    status: StatusEnum = Field(default=StatusEnum.ACTIVE)
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v, values):
        """Auto-generate slug from name if not provided"""
        if v:
            return v

        # Get name from values
        if 'name' in values.data:
            name = values.data['name']
            # Convert name to slug format
            slug = name.lower()
            slug = re.sub(r'[^a-z0-9\s-]', '', slug)
            slug = re.sub(r'[\s-]+', '-', slug)
            return slug.strip('-')

        return v


class SchoolUpdateSchema(BaseModel):
    """Schema for updating a school"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255, pattern="^[a-z0-9-]+$")
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website_url: Optional[str] = Field(None, max_length=500)
    facebook_url: Optional[str] = Field(None, max_length=500)
    twitter_url: Optional[str] = Field(None, max_length=500)
    instagram_url: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    principal_id: Optional[uuid.UUID] = None
    hod_id: Optional[uuid.UUID] = None
    timezone: Optional[str] = Field(None, max_length=50)
    locale: Optional[str] = Field(None, max_length=10)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Phone number must contain only digits and valid separators')
        return v

    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v):
        """Validate postal code format"""
        if v and not re.match(r'^[A-Za-z0-9\s-]+$', v):
            raise ValueError('Postal code contains invalid characters')
        return v

    @field_validator('website_url', 'facebook_url', 'twitter_url', 'instagram_url', 'logo_url')
    @classmethod
    def validate_url(cls, v):
        """Validate URL format"""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class SchoolStatusChangeSchema(BaseModel):
    """Schema for changing school status"""
    status: StatusEnum


class SchoolSettingsUpdateSchema(BaseModel):
    """Schema for updating school settings"""
    settings: Dict[str, Any]

    @field_validator('settings')
    @classmethod
    def validate_settings(cls, v):
        """Validate settings structure"""
        if not isinstance(v, dict):
            raise ValueError('Settings must be a dictionary')
        return v


class SchoolLeadershipSchema(BaseModel):
    """Schema for assigning school leadership"""
    principal_id: Optional[uuid.UUID] = None
    hod_id: Optional[uuid.UUID] = None


class SchoolResponseSchema(SchoolBaseSchema):
    """Schema for school response"""
    id: uuid.UUID
    slug: str
    logo_url: Optional[str]
    principal_id: Optional[uuid.UUID]
    hod_id: Optional[uuid.UUID]
    status: StatusEnum
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    is_active: Optional[bool] = None
    full_address: Optional[str] = None

    class Config:
        from_attributes = True


class SchoolListResponseSchema(BaseModel):
    """Schema for paginated school list response"""
    data: list[SchoolResponseSchema]
    pagination: Dict[str, Any]


class SchoolSearchSchema(BaseModel):
    """Schema for school search parameters"""
    search: Optional[str] = None
    status: Optional[StatusEnum] = None
    city: Optional[str] = None
    state: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    sort: str = Field(default="name")
    order: str = Field(default="asc", pattern="^(asc|desc)$")


class SchoolStatisticsSchema(BaseModel):
    """Schema for school statistics"""
    total: int
    by_status: Dict[str, int]
    by_state: Dict[str, int]
    active_count: int
    inactive_count: int


class SchoolLogoUploadSchema(BaseModel):
    """Schema for logo upload"""
    logo_url: str = Field(..., max_length=500)

    @field_validator('logo_url')
    @classmethod
    def validate_logo_url(cls, v):
        """Validate logo URL format"""
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Logo URL must start with http:// or https://')
        return v
