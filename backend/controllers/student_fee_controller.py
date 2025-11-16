"""
Student Fee Controller

API endpoints for StudentFee CRUD operations and fee calculations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from services.student_fee_service import StudentFeeService
from schemas.student_fee_schema import (
    StudentFeeCreateSchema,
    StudentFeeUpdateSchema,
    StudentFeeResponseSchema,
    StudentFeeListResponseSchema,
    FeeCalculatePreviewSchema,
    FeePreviewResponseSchema,
    StudentFeeStatisticsSchema,
    FeeStatusEnum
)
from config.database import get_db
import uuid
import math


router = APIRouter(prefix="/student-fees", tags=["student-fees"])

# TEMPORARY: Hardcoded admin ID for testing (until Keycloak auth is integrated)
# TODO: Replace with get_current_user() from auth middleware
TEMP_ADMIN_ID = uuid.UUID("ea2ad94a-b077-48c2-ae25-6e3e8dc54499")


# Dependency
async def get_student_fee_service(session: AsyncSession = Depends(get_db)) -> StudentFeeService:
    return StudentFeeService(session)


# 1. Calculate Fee Preview (No Save)
@router.post("/calculate", response_model=FeePreviewResponseSchema)
async def calculate_fee_preview(
    preview_data: FeeCalculatePreviewSchema,
    service: StudentFeeService = Depends(get_student_fee_service)
):
    """
    Calculate fee preview without saving to database.

    Shows complete calculation with all discounts and bursaries applied.
    Use this before creating actual fee record.

    **Permissions:** Administrator
    """
    try:
        preview = await service.calculate_fee_preview(
            school_id=preview_data.school_id,
            student_id=preview_data.student_id,
            academic_year=preview_data.academic_year,
            payment_frequency=preview_data.payment_frequency.value,
            bursary_id=preview_data.bursary_id,
            include_activities=preview_data.include_activities,
            material_fees=preview_data.material_fees,
            other_fees=preview_data.other_fees
        )

        return FeePreviewResponseSchema(**preview)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate fee preview: {str(e)}"
        )


# 2. Create Student Fee
@router.post("", response_model=StudentFeeResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_student_fee(
    fee_data: StudentFeeCreateSchema,
    service: StudentFeeService = Depends(get_student_fee_service)
):
    """
    Create a new student fee record with automatic calculation.

    Automatically calculates:
    - Base tuition from fee structure
    - Payment frequency discount
    - Sibling discount (based on enrollment dates)
    - Activity fees (from student enrollments)
    - Bursary coverage

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = TEMP_ADMIN_ID

        student_fee = await service.create_student_fee(
            school_id=fee_data.school_id,
            student_id=fee_data.student_id,
            academic_year=fee_data.academic_year,
            payment_frequency=fee_data.payment_frequency.value,
            created_by_id=current_user_id,
            bursary_id=fee_data.bursary_id,
            material_fees=fee_data.material_fees,
            other_fees=fee_data.other_fees,
            notes=fee_data.notes
        )

        return StudentFeeResponseSchema(**student_fee.to_dict(include_relationships=True))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create student fee: {str(e)}"
        )


# 3. Get Student Fee by ID
@router.get("/{fee_id}", response_model=StudentFeeResponseSchema)
async def get_student_fee(
    fee_id: uuid.UUID,
    service: StudentFeeService = Depends(get_student_fee_service)
):
    """
    Get a specific student fee by ID with relationships.

    **Permissions:** Administrator, Parent (own children), Student (own only)
    """
    try:
        fee = await service.get_student_fee(fee_id, include_relationships=True)

        if not fee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student fee not found"
            )

        return StudentFeeResponseSchema(**fee.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student fee: {str(e)}"
        )


# 4. List Student Fees
@router.get("", response_model=StudentFeeListResponseSchema)
async def list_student_fees(
    school_id: uuid.UUID = Query(..., description="School ID"),
    academic_year: Optional[str] = Query(None, pattern=r'^\d{4}-\d{4}$'),
    status: Optional[FeeStatusEnum] = None,
    payment_frequency: Optional[str] = None,
    has_bursary: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: StudentFeeService = Depends(get_student_fee_service)
):
    """
    List student fees with filtering and pagination.

    **Filters:**
    - academic_year: Filter by academic year
    - status: pending, partial, paid, overdue, waived
    - payment_frequency: yearly, monthly, weekly
    - has_bursary: true/false

    **Permissions:** Administrator
    """
    try:
        fees, total = await service.list_student_fees(
            school_id=school_id,
            academic_year=academic_year,
            status=status.value if status else None,
            payment_frequency=payment_frequency,
            has_bursary=has_bursary,
            page=page,
            limit=limit
        )

        pages = math.ceil(total / limit) if total > 0 else 0

        return StudentFeeListResponseSchema(
            data=[StudentFeeResponseSchema(**fee.to_dict(include_relationships=True)) for fee in fees],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list student fees: {str(e)}"
        )


# 5. Get Overdue Fees
@router.get("/overdue/list", response_model=StudentFeeListResponseSchema)
async def get_overdue_fees(
    school_id: uuid.UUID = Query(...),
    academic_year: Optional[str] = Query(None, pattern=r'^\d{4}-\d{4}$'),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: StudentFeeService = Depends(get_student_fee_service)
):
    """
    Get all overdue fees (past due date with balance).

    **Permissions:** Administrator
    """
    try:
        fees, total = await service.get_overdue_fees(
            school_id=school_id,
            academic_year=academic_year,
            page=page,
            limit=limit
        )

        pages = math.ceil(total / limit) if total > 0 else 0

        return StudentFeeListResponseSchema(
            data=[StudentFeeResponseSchema(**fee.to_dict(include_relationships=True)) for fee in fees],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get overdue fees: {str(e)}"
        )


# 6. Mark Fees as Overdue (Batch Operation)
@router.post("/overdue/mark")
async def mark_fees_overdue(
    school_id: uuid.UUID = Query(...),
    service: StudentFeeService = Depends(get_student_fee_service)
):
    """
    Mark pending/partial fees as overdue if past due date.

    This is typically run as a scheduled job.

    **Permissions:** Administrator
    """
    try:
        count = await service.mark_fees_overdue(school_id)

        return {
            "message": f"Marked {count} fees as overdue",
            "count": count
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark fees overdue: {str(e)}"
        )


# 7. Update Student Fee
@router.put("/{fee_id}", response_model=StudentFeeResponseSchema)
async def update_student_fee(
    fee_id: uuid.UUID,
    fee_data: StudentFeeUpdateSchema,
    service: StudentFeeService = Depends(get_student_fee_service)
):
    """
    Update student fee and optionally recalculate.

    Set recalculate=true to recalculate all amounts after update.

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = TEMP_ADMIN_ID

        updated_fee = await service.update_student_fee(
            fee_id=fee_id,
            updated_by_id=current_user_id,
            payment_frequency=fee_data.payment_frequency.value if fee_data.payment_frequency else None,
            bursary_id=fee_data.bursary_id,
            material_fees=fee_data.material_fees,
            other_fees=fee_data.other_fees,
            notes=fee_data.notes,
            recalculate=fee_data.recalculate
        )

        if not updated_fee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student fee not found"
            )

        return StudentFeeResponseSchema(**updated_fee.to_dict(include_relationships=True))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update student fee: {str(e)}"
        )


# 8. Get Statistics
@router.get("/statistics/summary", response_model=StudentFeeStatisticsSchema)
async def get_statistics(
    school_id: uuid.UUID = Query(...),
    academic_year: Optional[str] = Query(None, pattern=r'^\d{4}-\d{4}$'),
    service: StudentFeeService = Depends(get_student_fee_service)
):
    """
    Get comprehensive fee statistics for a school.

    Includes:
    - Total fees by status
    - Financial totals (before/after discounts, bursaries, paid, balance)
    - Collection rate
    - Breakdown by payment frequency

    **Permissions:** Administrator
    """
    try:
        stats = await service.get_statistics(school_id, academic_year)
        return StudentFeeStatisticsSchema(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


# 9. Delete Student Fee
@router.delete("/{fee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student_fee(
    fee_id: uuid.UUID,
    service: StudentFeeService = Depends(get_student_fee_service)
):
    """
    Delete student fee (soft delete).

    Also decrements bursary recipient count if applicable.

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = TEMP_ADMIN_ID

        success = await service.delete_student_fee(fee_id, current_user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student fee not found"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete student fee: {str(e)}"
        )
