"""
Activity Fee Controller

API endpoints for Activity Fee CRUD operations and prorated calculations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from services.activity_fee_service import ActivityFeeService
from schemas.activity_fee_schema import (
    ActivityFeeCreateSchema,
    ActivityFeeUpdateSchema,
    ActivityFeeResponseSchema,
    ActivityFeeListResponseSchema,
    ProratedFeeResponseSchema,
    StudentActivityFeesResponseSchema,
    ActivityFeeStatisticsSchema,
    FeeFrequencyEnum
)
from config.database import get_db
import uuid
import math


router = APIRouter(prefix="/activity-fees", tags=["activity-fees"])

# TEMPORARY: Hardcoded admin ID for testing (until Keycloak auth is integrated)
# TODO: Replace with get_current_user() from auth middleware
TEMP_ADMIN_ID = uuid.UUID("ea2ad94a-b077-48c2-ae25-6e3e8dc54499")


# Dependency
async def get_activity_fee_service(session: AsyncSession = Depends(get_db)) -> ActivityFeeService:
    return ActivityFeeService(session)


# 1. Create Activity Fee
@router.post("", response_model=ActivityFeeResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_activity_fee(
    activity_fee_data: ActivityFeeCreateSchema,
    service: ActivityFeeService = Depends(get_activity_fee_service)
):
    """
    Create a new activity fee for an activity.

    **Fee Frequencies:**
    - one_time: Single payment for the activity
    - yearly: Annual fee
    - quarterly: Fee per quarter
    - monthly: Monthly fee

    **Prorating:**
    - Enable allow_prorate for mid-year enrollments
    - Calculates fee based on remaining months

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = TEMP_ADMIN_ID

        activity_fee = await service.create_activity_fee(
            school_id=activity_fee_data.school_id,
            activity_id=activity_fee_data.activity_id,
            academic_year=activity_fee_data.academic_year,
            fee_amount=activity_fee_data.fee_amount,
            fee_frequency=activity_fee_data.fee_frequency.value,
            allow_prorate=activity_fee_data.allow_prorate,
            prorate_calculation=activity_fee_data.prorate_calculation,
            description=activity_fee_data.description,
            created_by_id=current_user_id
        )

        return ActivityFeeResponseSchema(**activity_fee.to_dict(include_relationships=True))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create activity fee: {str(e)}"
        )


# 2. Get Activity Fee by ID
@router.get("/{activity_fee_id}", response_model=ActivityFeeResponseSchema)
async def get_activity_fee(
    activity_fee_id: uuid.UUID,
    service: ActivityFeeService = Depends(get_activity_fee_service)
):
    """
    Get a specific activity fee by ID.

    **Permissions:** Administrator, Parent (view only), Student (view only)
    """
    try:
        activity_fee = await service.get_activity_fee(activity_fee_id, include_relationships=True)

        if not activity_fee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity fee not found"
            )

        return ActivityFeeResponseSchema(**activity_fee.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity fee: {str(e)}"
        )


# 3. Get Activity Fee by Activity and Year
@router.get("/activity/{activity_id}/year/{academic_year}", response_model=ActivityFeeResponseSchema)
async def get_activity_fee_by_activity_year(
    activity_id: uuid.UUID,
    academic_year: str = Path(..., pattern=r'^\d{4}-\d{4}$'),
    service: ActivityFeeService = Depends(get_activity_fee_service)
):
    """
    Get activity fee for a specific activity and academic year.

    **Permissions:** Administrator, Parent (view only), Student (view only)
    """
    try:
        activity_fee = await service.get_by_activity_and_year(activity_id, academic_year)

        if not activity_fee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity fee not found for activity {activity_id}, {academic_year}"
            )

        return ActivityFeeResponseSchema(**activity_fee.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity fee: {str(e)}"
        )


# 4. List Activity Fees
@router.get("", response_model=ActivityFeeListResponseSchema)
async def list_activity_fees(
    school_id: uuid.UUID = Query(...),
    academic_year: Optional[str] = Query(None, pattern=r'^\d{4}-\d{4}$'),
    fee_frequency: Optional[FeeFrequencyEnum] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: ActivityFeeService = Depends(get_activity_fee_service)
):
    """
    List activity fees with filtering and pagination.

    **Filters:**
    - academic_year: Filter by academic year
    - fee_frequency: one_time, yearly, quarterly, monthly
    - is_active: Filter active/inactive fees

    **Permissions:** Administrator, Parent (view only), Student (view only)
    """
    try:
        activity_fees, total = await service.list_activity_fees(
            school_id=school_id,
            academic_year=academic_year,
            fee_frequency=fee_frequency.value if fee_frequency else None,
            is_active=is_active,
            page=page,
            limit=limit
        )

        pages = math.ceil(total / limit) if total > 0 else 0

        return ActivityFeeListResponseSchema(
            data=[ActivityFeeResponseSchema(**af.to_dict(include_relationships=True)) for af in activity_fees],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list activity fees: {str(e)}"
        )


# 5. Calculate Prorated Fee
@router.get("/{activity_fee_id}/prorate", response_model=ProratedFeeResponseSchema)
async def calculate_prorated_fee(
    activity_fee_id: uuid.UUID,
    enrollment_date: date = Query(..., description="Date student enrolled in activity"),
    service: ActivityFeeService = Depends(get_activity_fee_service)
):
    """
    Calculate prorated fee for mid-year enrollment.

    Returns original amount, prorated amount, and savings.

    **Permissions:** Administrator
    """
    try:
        prorated = await service.calculate_prorated_fee(activity_fee_id, enrollment_date)
        return ProratedFeeResponseSchema(**prorated)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate prorated fee: {str(e)}"
        )


# 6. Get Student Activity Fees
@router.get("/student/{student_id}/total", response_model=StudentActivityFeesResponseSchema)
async def get_student_activity_fees(
    student_id: uuid.UUID,
    academic_year: str = Query(..., pattern=r'^\d{4}-\d{4}$'),
    service: ActivityFeeService = Depends(get_activity_fee_service)
):
    """
    Get total activity fees for a student.

    Returns total fee amount and breakdown by activity.

    **Permissions:** Administrator, Parent (own children), Student (own only)
    """
    try:
        result = await service.get_student_activity_fees(student_id, academic_year)
        return StudentActivityFeesResponseSchema(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student activity fees: {str(e)}"
        )


# 7. Update Activity Fee
@router.put("/{activity_fee_id}", response_model=ActivityFeeResponseSchema)
async def update_activity_fee(
    activity_fee_id: uuid.UUID,
    activity_fee_data: ActivityFeeUpdateSchema,
    service: ActivityFeeService = Depends(get_activity_fee_service)
):
    """
    Update activity fee details.

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = TEMP_ADMIN_ID

        updated_activity_fee = await service.update_activity_fee(
            activity_fee_id=activity_fee_id,
            updated_by_id=current_user_id,
            fee_amount=activity_fee_data.fee_amount,
            fee_frequency=activity_fee_data.fee_frequency.value if activity_fee_data.fee_frequency else None,
            allow_prorate=activity_fee_data.allow_prorate,
            prorate_calculation=activity_fee_data.prorate_calculation,
            description=activity_fee_data.description,
            is_active=activity_fee_data.is_active
        )

        if not updated_activity_fee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity fee not found"
            )

        return ActivityFeeResponseSchema(**updated_activity_fee.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update activity fee: {str(e)}"
        )


# 8. Get Statistics
@router.get("/statistics/summary", response_model=ActivityFeeStatisticsSchema)
async def get_statistics(
    school_id: uuid.UUID = Query(...),
    academic_year: Optional[str] = Query(None, pattern=r'^\d{4}-\d{4}$'),
    service: ActivityFeeService = Depends(get_activity_fee_service)
):
    """
    Get comprehensive activity fee statistics.

    Includes:
    - Total and active activity fees
    - Average fee amount
    - Breakdown by frequency

    **Permissions:** Administrator
    """
    try:
        stats = await service.get_statistics(school_id, academic_year)
        return ActivityFeeStatisticsSchema(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


# 9. Delete Activity Fee
@router.delete("/{activity_fee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity_fee(
    activity_fee_id: uuid.UUID,
    service: ActivityFeeService = Depends(get_activity_fee_service)
):
    """
    Delete activity fee (soft delete).

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = TEMP_ADMIN_ID

        success = await service.delete_activity_fee(activity_fee_id, current_user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity fee not found"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete activity fee: {str(e)}"
        )
