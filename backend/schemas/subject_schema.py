"""
Subject Schemas

Pydantic schemas for Subject validation and serialization.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime
import re
import uuid as uuid_pkg


class SubjectBaseSchema(BaseModel):
    """Base schema with common subject fields."""

    code: str = Field(..., min_length=2, max_length=50, description="Subject code (e.g., MATH, ELA)")
    name: str = Field(..., min_length=1, max_length=200, description="Subject name")
    description: Optional[str] = Field(None, max_length=2000, description="Subject description")
    category: str = Field(default="core", description="Subject category")
    subject_type: Optional[str] = Field(None, description="Subject type")
    grade_levels: List[int] = Field(default=[1, 2, 3, 4, 5, 6, 7], description="Grade levels (1-7)")
    color: Optional[str] = Field(None, description="Hex color code (#RRGGBB)")
    icon: Optional[str] = Field(None, max_length=50, description="Icon/emoji")
    display_order: int = Field(default=0, description="Display order")
    credits: Optional[float] = Field(None, ge=0, description="Credit hours")
    is_required: bool = Field(default=True, description="Required subject flag")
    is_active: bool = Field(default=True, description="Active status")

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate and uppercase subject code."""
        if not v:
            raise ValueError("Subject code cannot be empty")

        # Convert to uppercase
        v = v.upper().strip()

        # Check format (alphanumeric + underscore only)
        if not re.match(r'^[A-Z0-9_]+$', v):
            raise ValueError("Subject code must contain only uppercase letters, numbers, and underscores")

        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate subject category."""
        valid_categories = ['core', 'elective', 'enrichment', 'remedial', 'other']
        if v not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        return v

    @field_validator('subject_type')
    @classmethod
    def validate_subject_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate subject type."""
        if v is None:
            return v

        valid_types = ['academic', 'arts', 'physical', 'technical', 'other']
        if v not in valid_types:
            raise ValueError(f"Invalid subject type. Must be one of: {', '.join(valid_types)}")
        return v

    @field_validator('grade_levels')
    @classmethod
    def validate_grade_levels(cls, v: List[int]) -> List[int]:
        """Validate grade levels."""
        if not v:
            raise ValueError("At least one grade level must be specified")

        # Check all grades are in valid range
        invalid_grades = [g for g in v if g < 1 or g > 7]
        if invalid_grades:
            raise ValueError(f"Invalid grade levels: {invalid_grades}. Must be between 1 and 7")

        # Remove duplicates and sort
        return sorted(list(set(v)))

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate hex color format."""
        if v is None or v == "":
            return None

        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError("Color must be in hex format (#RRGGBB)")

        return v.upper()


class SubjectCreateSchema(SubjectBaseSchema):
    """Schema for creating a new subject."""

    school_id: uuid_pkg.UUID = Field(..., description="School UUID")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "school_id": "60da2256-81fc-4ca5-bf6b-467b8d371c61",
                "code": "MATH",
                "name": "Mathematics",
                "description": "Core mathematics curriculum covering arithmetic, algebra, and geometry",
                "category": "core",
                "subject_type": "academic",
                "grade_levels": [1, 2, 3, 4, 5, 6, 7],
                "color": "#2196F3",
                "icon": "🔢",
                "is_required": True,
                "is_active": True
            }
        }


class SubjectUpdateSchema(BaseModel):
    """Schema for updating a subject (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = None
    subject_type: Optional[str] = None
    grade_levels: Optional[List[int]] = None
    color: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    display_order: Optional[int] = None
    credits: Optional[float] = Field(None, ge=0)
    is_required: Optional[bool] = None
    is_active: Optional[bool] = None

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        """Validate subject category."""
        if v is None:
            return v
        valid_categories = ['core', 'elective', 'enrichment', 'remedial', 'other']
        if v not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        return v

    @field_validator('subject_type')
    @classmethod
    def validate_subject_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate subject type."""
        if v is None:
            return v
        valid_types = ['academic', 'arts', 'physical', 'technical', 'other']
        if v not in valid_types:
            raise ValueError(f"Invalid subject type. Must be one of: {', '.join(valid_types)}")
        return v

    @field_validator('grade_levels')
    @classmethod
    def validate_grade_levels(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Validate grade levels."""
        if v is None:
            return v

        if not v:
            raise ValueError("At least one grade level must be specified")

        invalid_grades = [g for g in v if g < 1 or g > 7]
        if invalid_grades:
            raise ValueError(f"Invalid grade levels: {invalid_grades}. Must be between 1 and 7")

        return sorted(list(set(v)))

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate hex color format."""
        if v is None or v == "":
            return None

        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError("Color must be in hex format (#RRGGBB)")

        return v.upper()

    class Config:
        from_attributes = True


class SubjectResponseSchema(BaseModel):
    """Schema for subject response."""

    id: str
    school_id: str
    code: str
    name: str
    description: Optional[str]
    category: str
    subject_type: Optional[str]
    grade_levels: List[int]
    color: Optional[str]
    icon: Optional[str]
    display_order: int
    credits: Optional[float]
    is_required: bool
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    # Computed fields
    is_available: Optional[bool] = None
    is_core: Optional[bool] = None
    grade_range: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "school_id": "60da2256-81fc-4ca5-bf6b-467b8d371c61",
                "code": "MATH",
                "name": "Mathematics",
                "description": "Core mathematics curriculum...",
                "category": "core",
                "subject_type": "academic",
                "grade_levels": [1, 2, 3, 4, 5, 6, 7],
                "color": "#2196F3",
                "icon": "🔢",
                "display_order": 0,
                "credits": None,
                "is_required": True,
                "is_active": True,
                "is_available": True,
                "is_core": True,
                "grade_range": "1-7",
                "created_at": "2025-10-17T10:00:00Z",
                "updated_at": "2025-10-17T10:00:00Z"
            }
        }


class SubjectListResponseSchema(BaseModel):
    """Schema for paginated subject list response."""

    subjects: List[SubjectResponseSchema]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True


class SubjectStatusSchema(BaseModel):
    """Schema for changing subject status."""

    is_active: bool = Field(..., description="New active status")

    class Config:
        from_attributes = True


class SubjectStatisticsSchema(BaseModel):
    """Schema for subject statistics."""

    total_subjects: int
    active_subjects: int
    inactive_subjects: int
    by_category: Dict[str, int]
    by_type: Dict[str, int]
    required_subjects: int
    elective_subjects: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "total_subjects": 10,
                "active_subjects": 8,
                "inactive_subjects": 2,
                "by_category": {
                    "core": 6,
                    "elective": 3,
                    "enrichment": 1
                },
                "by_type": {
                    "academic": 5,
                    "arts": 2,
                    "physical": 2,
                    "technical": 1
                },
                "required_subjects": 6,
                "elective_subjects": 4
            }
        }
