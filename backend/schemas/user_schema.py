"""
User Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class PersonaEnum(str, Enum):
    """Valid user personas"""
    ADMINISTRATOR = "administrator"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    VENDOR = "vendor"


class StatusEnum(str, Enum):
    """Valid user statuses"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class UserBaseSchema(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Phone number must contain only digits and valid separators (+, -, spaces, parentheses)')
        return v


class UserCreateSchema(UserBaseSchema):
    """Schema for creating a new user"""
    persona: PersonaEnum
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    school_id: uuid.UUID

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if v is None:
            return v

        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')

        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')

        return v


class UserUpdateSchema(BaseModel):
    """Schema for updating a user"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Phone number must contain only digits and valid separators')
        return v


class UserStatusChangeSchema(BaseModel):
    """Schema for changing user status"""
    status: StatusEnum


class UserPersonaChangeSchema(BaseModel):
    """Schema for changing user persona"""
    persona: PersonaEnum


class UserResponseSchema(UserBaseSchema):
    """Schema for user response"""
    id: uuid.UUID
    school_id: uuid.UUID
    persona: PersonaEnum
    status: StatusEnum
    email_verified: bool
    last_login: Optional[datetime]
    keycloak_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class UserListResponseSchema(BaseModel):
    """Schema for paginated user list response"""
    data: list[UserResponseSchema]
    pagination: Dict[str, Any]


class UserSearchSchema(BaseModel):
    """Schema for user search parameters"""
    search: Optional[str] = None
    persona: Optional[PersonaEnum] = None
    status: Optional[StatusEnum] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    sort: str = Field(default="created_at")
    order: str = Field(default="desc", pattern="^(asc|desc)$")


class UserStatisticsSchema(BaseModel):
    """Schema for user statistics"""
    total: int
    by_persona: Dict[str, int]
    by_status: Dict[str, int]


class PasswordResetRequestSchema(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetSchema(BaseModel):
    """Schema for password reset"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')

        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')

        return v


class EmailVerificationSchema(BaseModel):
    """Schema for email verification"""
    token: str
