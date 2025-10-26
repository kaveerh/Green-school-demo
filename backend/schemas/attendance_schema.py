"""
Attendance Schemas

Pydantic schemas for Attendance request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime, time
from enum import Enum
import uuid


# Enums
class AttendanceStatusEnum(str, Enum):
    """Valid attendance statuses"""
    PRESENT = "present"
    ABSENT = "absent"
    TARDY = "tardy"
    EXCUSED = "excused"
    SICK = "sick"


# Create Schema
class AttendanceCreateSchema(BaseModel):
    """Schema for creating an attendance record"""
    school_id: uuid.UUID
    student_id: uuid.UUID
    attendance_date: date
    status: AttendanceStatusEnum
    class_id: Optional[uuid.UUID] = None  # NULL for homeroom attendance
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    notes: Optional[str] = None
    recorded_by: Optional[uuid.UUID] = None

    @field_validator('check_out_time')
    @classmethod
    def validate_check_out_time(cls, v: Optional[time], info) -> Optional[time]:
        """Validate check_out_time is after check_in_time"""
        if v and 'check_in_time' in info.data:
            check_in = info.data['check_in_time']
            if check_in and v < check_in:
                raise ValueError('Check-out time must be after check-in time')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "school_id": "60da2256-81fc-4ca5-bf6b-467b8d371c61",
                "student_id": "c7d715a4-cca0-4133-9a6d-172d585a10e6",
                "attendance_date": "2025-10-24",
                "status": "present",
                "class_id": "2e008ff4-dc05-4c6b-8059-ca92fceb3f9a",
                "check_in_time": "08:30:00",
                "notes": "On time"
            }
        }


# Bulk Create Schema
class StudentAttendanceSchema(BaseModel):
    """Schema for single student in bulk attendance creation"""
    student_id: uuid.UUID
    status: AttendanceStatusEnum
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    notes: Optional[str] = None


class AttendanceBulkCreateSchema(BaseModel):
    """Schema for creating multiple attendance records for a class"""
    school_id: uuid.UUID
    class_id: uuid.UUID
    attendance_date: date
    students: List[StudentAttendanceSchema] = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "school_id": "60da2256-81fc-4ca5-bf6b-467b8d371c61",
                "class_id": "2e008ff4-dc05-4c6b-8059-ca92fceb3f9a",
                "attendance_date": "2025-10-24",
                "students": [
                    {
                        "student_id": "c7d715a4-cca0-4133-9a6d-172d585a10e6",
                        "status": "present",
                        "check_in_time": "08:30:00"
                    },
                    {
                        "student_id": "d8e826b5-ddb1-5244-a07e-283e696b21f7",
                        "status": "absent",
                        "notes": "Called in sick"
                    }
                ]
            }
        }


# Update Schema
class AttendanceUpdateSchema(BaseModel):
    """Schema for updating an attendance record"""
    status: Optional[AttendanceStatusEnum] = None
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    notes: Optional[str] = None


# Mark Parent Notified Schema
class AttendanceMarkNotifiedSchema(BaseModel):
    """Schema for marking attendance records as parent notified"""
    attendance_ids: List[uuid.UUID] = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "attendance_ids": [
                    "21ff69fd-da5b-4617-bf4c-7d9d481a1d25",
                    "32ff69fd-da5b-4617-bf4c-7d9d481a1d26"
                ]
            }
        }


# Response Schemas
class StudentBasicSchema(BaseModel):
    """Basic student info for nested responses"""
    id: str
    student_id: str
    grade_level: int
    name: Optional[str] = None

    class Config:
        from_attributes = True


class ClassBasicSchema(BaseModel):
    """Basic class info for nested responses"""
    id: str
    name: str
    code: str

    class Config:
        from_attributes = True


class AttendanceResponseSchema(BaseModel):
    """Schema for attendance response"""
    id: str
    school_id: str
    student_id: str
    class_id: Optional[str]
    attendance_date: date
    status: str
    check_in_time: Optional[time]
    check_out_time: Optional[time]
    notes: Optional[str]
    recorded_by: Optional[str]
    parent_notified: bool
    notified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_present: bool
    is_absent: bool
    needs_parent_notification: bool
    duration_minutes: int

    # Nested relationships (optional)
    student: Optional[StudentBasicSchema] = None
    class_obj: Optional[ClassBasicSchema] = Field(None, alias="class")
    recorded_by_name: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class AttendanceListResponseSchema(BaseModel):
    """Schema for paginated attendance list"""
    attendance: List[AttendanceResponseSchema]
    total: int
    page: int
    limit: int


class AttendanceStatisticsSchema(BaseModel):
    """Schema for attendance statistics"""
    total_records: int
    unique_students: int
    days_tracked: int
    avg_daily_attendance: float
    by_status: Dict[str, int]
    present_count: int
    absent_count: int
    tardy_count: int
    excused_count: int
    attendance_rate: float
    absence_rate: float

    class Config:
        json_schema_extra = {
            "example": {
                "total_records": 500,
                "unique_students": 25,
                "days_tracked": 20,
                "avg_daily_attendance": 25.0,
                "by_status": {
                    "present": 450,
                    "absent": 30,
                    "tardy": 15,
                    "sick": 5
                },
                "present_count": 450,
                "absent_count": 35,
                "tardy_count": 15,
                "excused_count": 0,
                "attendance_rate": 90.0,
                "absence_rate": 7.0
            }
        }


class UnnotifiedAbsencesResponseSchema(BaseModel):
    """Schema for unnotified absences list"""
    absences: List[AttendanceResponseSchema]
    count: int

    class Config:
        json_schema_extra = {
            "example": {
                "count": 5,
                "absences": []
            }
        }
