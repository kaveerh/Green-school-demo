"""
Attendance Controller

API endpoints for Attendance CRUD operations and reporting.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from services.attendance_service import AttendanceService
from schemas.attendance_schema import (
    AttendanceCreateSchema,
    AttendanceBulkCreateSchema,
    AttendanceUpdateSchema,
    AttendanceMarkNotifiedSchema,
    AttendanceResponseSchema,
    AttendanceListResponseSchema,
    AttendanceStatisticsSchema,
    UnnotifiedAbsencesResponseSchema
)
from config.database import get_db
from datetime import date
import uuid


router = APIRouter(prefix="/attendance", tags=["attendance"])


# Dependency to get AttendanceService
async def get_attendance_service(session: AsyncSession = Depends(get_db)) -> AttendanceService:
    return AttendanceService(session)


# 1. Create Single Attendance Record
@router.post("", response_model=AttendanceResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    attendance_data: AttendanceCreateSchema,
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Create a single attendance record.

    **Required:**
    - school_id, student_id, attendance_date, status

    **Optional:**
    - class_id (NULL for homeroom attendance)
    - check_in_time, check_out_time
    - notes, recorded_by

    **Permissions:** Teacher, Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.UUID("ea2ad94a-b077-48c2-ae25-6e3e8dc54499")  # Placeholder (real user from DB)

        attendance = await service.create_attendance(
            school_id=attendance_data.school_id,
            student_id=attendance_data.student_id,
            attendance_date=attendance_data.attendance_date,
            status=attendance_data.status.value,
            created_by_id=current_user_id,
            class_id=attendance_data.class_id,
            check_in_time=attendance_data.check_in_time,
            check_out_time=attendance_data.check_out_time,
            notes=attendance_data.notes,
            recorded_by=attendance_data.recorded_by
        )

        return AttendanceResponseSchema(**attendance.to_dict(include_relationships=True))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create attendance: {str(e)}"
        )


# 2. Bulk Create Attendance Records
@router.post("/bulk", response_model=List[AttendanceResponseSchema], status_code=status.HTTP_201_CREATED)
async def bulk_create_attendance(
    bulk_data: AttendanceBulkCreateSchema,
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Create multiple attendance records for a class at once.

    Useful for teachers marking attendance for entire class.

    **Required:**
    - school_id, class_id, attendance_date
    - students (array with student_id and status for each)

    **Permissions:** Teacher (assigned), Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.UUID("ea2ad94a-b077-48c2-ae25-6e3e8dc54499")  # Placeholder (real user from DB)

        student_statuses = [
            {
                'student_id': student.student_id,
                'status': student.status.value,
                'check_in_time': student.check_in_time,
                'check_out_time': student.check_out_time,
                'notes': student.notes
            }
            for student in bulk_data.students
        ]

        attendances = await service.bulk_create_attendance(
            school_id=bulk_data.school_id,
            class_id=bulk_data.class_id,
            attendance_date=bulk_data.attendance_date,
            student_statuses=student_statuses,
            created_by_id=current_user_id
        )

        return [AttendanceResponseSchema(**a.to_dict(include_relationships=True)) for a in attendances]

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk create attendance: {str(e)}"
        )


# 3. Get Attendance by ID
@router.get("/{attendance_id}", response_model=AttendanceResponseSchema)
async def get_attendance(
    attendance_id: uuid.UUID,
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Get a specific attendance record by ID with relationships.

    **Permissions:** Teacher, Administrator, Student (own only), Parent (children only)
    """
    try:
        attendance = await service.repository.get_with_relationships(attendance_id)

        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        return AttendanceResponseSchema(**attendance.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attendance: {str(e)}"
        )


# 4. Update Attendance Record
@router.put("/{attendance_id}", response_model=AttendanceResponseSchema)
async def update_attendance(
    attendance_id: uuid.UUID,
    attendance_data: AttendanceUpdateSchema,
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Update an attendance record.

    All fields are optional. Only provided fields will be updated.

    **Permissions:** Teacher (recorder), Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.UUID("ea2ad94a-b077-48c2-ae25-6e3e8dc54499")  # Placeholder (real user from DB)

        attendance = await service.update_attendance(
            attendance_id=attendance_id,
            updated_by_id=current_user_id,
            status=attendance_data.status.value if attendance_data.status else None,
            check_in_time=attendance_data.check_in_time,
            check_out_time=attendance_data.check_out_time,
            notes=attendance_data.notes
        )

        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        # Load relationships for response
        attendance_with_relationships = await service.repository.get_with_relationships(attendance_id)

        return AttendanceResponseSchema(**attendance_with_relationships.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update attendance: {str(e)}"
        )


# 5. Delete Attendance Record
@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance(
    attendance_id: uuid.UUID,
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Soft delete an attendance record.

    **Permissions:** Administrator only
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.UUID("ea2ad94a-b077-48c2-ae25-6e3e8dc54499")  # Placeholder (real user from DB)

        success = await service.delete_attendance(attendance_id, current_user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete attendance: {str(e)}"
        )


# 6. Get Student Attendance
@router.get("/student/{student_id}", response_model=AttendanceListResponseSchema)
async def get_student_attendance(
    student_id: uuid.UUID,
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Results per page"),
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Get all attendance records for a student with optional filters.

    **Query Parameters:**
    - start_date, end_date: Date range filter
    - status: Filter by specific status
    - page, limit: Pagination

    **Permissions:** Teacher, Administrator, Student (own only), Parent (children only)
    """
    try:
        attendance_records, total = await service.get_student_attendance(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            page=page,
            limit=limit
        )

        return AttendanceListResponseSchema(
            attendance=[AttendanceResponseSchema(**a.to_dict(include_relationships=True)) for a in attendance_records],
            total=total,
            page=page,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student attendance: {str(e)}"
        )


# 7. Get Class Attendance for Date
@router.get("/class/{class_id}/date/{attendance_date}", response_model=AttendanceListResponseSchema)
async def get_class_attendance(
    class_id: uuid.UUID,
    attendance_date: date,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=200),
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Get all attendance records for a class on a specific date.

    **Permissions:** Teacher (assigned), Administrator
    """
    try:
        attendance_records, total = await service.get_class_attendance(
            class_id=class_id,
            attendance_date=attendance_date,
            page=page,
            limit=limit
        )

        return AttendanceListResponseSchema(
            attendance=[AttendanceResponseSchema(**a.to_dict(include_relationships=True)) for a in attendance_records],
            total=total,
            page=page,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get class attendance: {str(e)}"
        )


# 8. Get School Attendance for Date
@router.get("/school/{school_id}/date/{attendance_date}", response_model=AttendanceListResponseSchema)
async def get_school_attendance(
    school_id: uuid.UUID,
    attendance_date: date,
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=200),
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Get all attendance records for a school on a specific date.

    **Permissions:** Administrator
    """
    try:
        attendance_records, total = await service.get_school_attendance(
            school_id=school_id,
            attendance_date=attendance_date,
            status=status,
            page=page,
            limit=limit
        )

        return AttendanceListResponseSchema(
            attendance=[AttendanceResponseSchema(**a.to_dict(include_relationships=True)) for a in attendance_records],
            total=total,
            page=page,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get school attendance: {str(e)}"
        )


# 9. Get Attendance by Date Range
@router.get("/date-range", response_model=List[AttendanceResponseSchema])
async def get_attendance_by_date_range(
    school_id: uuid.UUID = Query(..., description="School ID"),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    class_id: Optional[uuid.UUID] = Query(None, description="Filter by class"),
    student_id: Optional[uuid.UUID] = Query(None, description="Filter by student"),
    status: Optional[str] = Query(None, description="Filter by status"),
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Get attendance records within a date range with optional filters.

    **Query Parameters:**
    - school_id (required)
    - start_date, end_date (required)
    - class_id, student_id, status (optional filters)

    **Permissions:** Teacher, Administrator
    """
    try:
        attendance_records = await service.get_attendance_by_date_range(
            school_id=school_id,
            start_date=start_date,
            end_date=end_date,
            class_id=class_id,
            student_id=student_id,
            status=status
        )

        return [AttendanceResponseSchema(**a.to_dict(include_relationships=True)) for a in attendance_records]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attendance by date range: {str(e)}"
        )


# 10. Get Unnotified Absences
@router.get("/unnotified-absences/school/{school_id}", response_model=UnnotifiedAbsencesResponseSchema)
async def get_unnotified_absences(
    school_id: uuid.UUID,
    attendance_date: Optional[date] = Query(None, description="Date to check (default: today)"),
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Get absence records that haven't been sent to parents yet.

    Defaults to today's date if not specified.

    **Permissions:** Teacher, Administrator
    """
    try:
        absences = await service.get_unnotified_absences(
            school_id=school_id,
            attendance_date=attendance_date
        )

        return UnnotifiedAbsencesResponseSchema(
            absences=[AttendanceResponseSchema(**a.to_dict(include_relationships=True)) for a in absences],
            count=len(absences)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unnotified absences: {str(e)}"
        )


# 11. Mark Parent Notified
@router.post("/mark-notified", status_code=status.HTTP_200_OK)
async def mark_parent_notified(
    data: AttendanceMarkNotifiedSchema,
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Mark multiple attendance records as parent notified.

    Updates parent_notified flag and notified_at timestamp.

    **Permissions:** Teacher, Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.UUID("ea2ad94a-b077-48c2-ae25-6e3e8dc54499")  # Placeholder (real user from DB)

        count = await service.bulk_mark_parent_notified(
            attendance_ids=data.attendance_ids,
            updated_by_id=current_user_id
        )

        return {
            "message": f"Successfully marked {count} attendance records as notified",
            "count": count
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark parent notified: {str(e)}"
        )


# 12. Get Attendance Statistics
@router.get("/statistics/summary", response_model=AttendanceStatisticsSchema)
async def get_attendance_statistics(
    school_id: uuid.UUID = Query(..., description="School ID"),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    class_id: Optional[uuid.UUID] = Query(None, description="Filter by class"),
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Get attendance statistics for a school within a date range.

    Returns:
    - Total records and unique students
    - Days tracked and average daily attendance
    - Breakdown by status
    - Attendance and absence rates

    **Permissions:** Administrator, Teacher
    """
    try:
        stats = await service.get_statistics(
            school_id=school_id,
            start_date=start_date,
            end_date=end_date,
            class_id=class_id
        )

        return AttendanceStatisticsSchema(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attendance statistics: {str(e)}"
        )
