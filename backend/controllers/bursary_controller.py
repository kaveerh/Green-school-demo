"""
Bursary Controller

API endpoints for Bursary CRUD operations and eligibility checking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from services.bursary_service import BursaryService
from schemas.bursary_schema import (
    BursaryCreateSchema,
    BursaryUpdateSchema,
    BursaryResponseSchema,
    BursaryListResponseSchema,
    BursaryEligibilitySchema,
    BursaryStatisticsSchema,
    BursaryTypeEnum
)
from config.database import get_db
import uuid
import math


router = APIRouter(prefix="/bursaries", tags=["bursaries"])

# TEMPORARY: Hardcoded admin ID for testing (until Keycloak auth is integrated)
# TODO: Replace with get_current_user() from auth middleware
TEMP_ADMIN_ID = uuid.UUID("ea2ad94a-b077-48c2-ae25-6e3e8dc54499")


# Dependency
async def get_bursary_service(session: AsyncSession = Depends(get_db)) -> BursaryService:
    return BursaryService(session)


# 1. Create Bursary
@router.post("", response_model=BursaryResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_bursary(
    bursary_data: BursaryCreateSchema,
    service: BursaryService = Depends(get_bursary_service)
):
    """
    Create a new bursary/scholarship program.

    **Coverage Types:**
    - percentage: Coverage as percentage (0-100%)
    - fixed_amount: Coverage as fixed dollar amount

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = TEMP_ADMIN_ID

        bursary = await service.create_bursary(
            school_id=bursary_data.school_id,
            name=bursary_data.name,
            description=bursary_data.description,
            bursary_type=bursary_data.bursary_type.value,
            coverage_type=bursary_data.coverage_type.value,
            coverage_value=bursary_data.coverage_value,
            max_coverage_amount=bursary_data.max_coverage_amount,
            academic_year=bursary_data.academic_year,
            eligible_grades=bursary_data.eligible_grades,
            max_recipients=bursary_data.max_recipients,
            application_deadline=bursary_data.application_deadline,
            sponsor_name=bursary_data.sponsor_name,
            sponsor_contact=bursary_data.sponsor_contact,
            terms_and_conditions=bursary_data.terms_and_conditions,
            created_by_id=current_user_id
        )

        return BursaryResponseSchema(**bursary.to_dict(include_relationships=True))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bursary: {str(e)}"
        )


# 2. Get Bursary by ID
@router.get("/{bursary_id}", response_model=BursaryResponseSchema)
async def get_bursary(
    bursary_id: uuid.UUID,
    service: BursaryService = Depends(get_bursary_service)
):
    """
    Get a specific bursary by ID.

    **Permissions:** Administrator, Parent (view only), Student (view only)
    """
    try:
        bursary = await service.get_bursary(bursary_id, include_relationships=True)

        if not bursary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bursary not found"
            )

        return BursaryResponseSchema(**bursary.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bursary: {str(e)}"
        )


# 3. List Bursaries
@router.get("", response_model=BursaryListResponseSchema)
async def list_bursaries(
    school_id: uuid.UUID = Query(...),
    academic_year: Optional[str] = Query(None, pattern=r'^\d{4}-\d{4}$'),
    bursary_type: Optional[BursaryTypeEnum] = None,
    is_active: Optional[bool] = None,
    has_capacity: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: BursaryService = Depends(get_bursary_service)
):
    """
    List bursaries with filtering and pagination.

    **Filters:**
    - academic_year: Filter by academic year
    - bursary_type: merit, need, sports, academic, other
    - is_active: Filter active/inactive bursaries
    - has_capacity: Filter bursaries accepting applications

    **Permissions:** Administrator, Parent (view only), Student (view only)
    """
    try:
        bursaries, total = await service.list_bursaries(
            school_id=school_id,
            academic_year=academic_year,
            bursary_type=bursary_type.value if bursary_type else None,
            is_active=is_active,
            has_capacity=has_capacity,
            page=page,
            limit=limit
        )

        pages = math.ceil(total / limit) if total > 0 else 0

        return BursaryListResponseSchema(
            data=[BursaryResponseSchema(**b.to_dict(include_relationships=True)) for b in bursaries],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list bursaries: {str(e)}"
        )


# 4. Get Available Bursaries for Student
@router.get("/student/{student_id}/available", response_model=BursaryListResponseSchema)
async def get_available_bursaries(
    student_id: uuid.UUID,
    school_id: uuid.UUID = Query(...),
    academic_year: str = Query(..., pattern=r'^\d{4}-\d{4}$'),
    service: BursaryService = Depends(get_bursary_service)
):
    """
    Get all active bursaries available for a student (based on grade eligibility).

    **Permissions:** Administrator, Parent (own children), Student (own only)
    """
    try:
        bursaries = await service.get_available_bursaries_for_student(
            school_id=school_id,
            student_id=student_id,
            academic_year=academic_year
        )

        return BursaryListResponseSchema(
            data=[BursaryResponseSchema(**b.to_dict(include_relationships=True)) for b in bursaries],
            total=len(bursaries),
            page=1,
            limit=len(bursaries),
            pages=1
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available bursaries: {str(e)}"
        )


# 5. Check Bursary Eligibility
@router.get("/{bursary_id}/eligibility/{student_id}", response_model=BursaryEligibilitySchema)
async def check_eligibility(
    bursary_id: uuid.UUID,
    student_id: uuid.UUID,
    service: BursaryService = Depends(get_bursary_service)
):
    """
    Check if a student is eligible for a specific bursary.

    Returns:
    - eligible: true/false
    - reasons: List of eligibility criteria met/failed
    - coverage_info: Details about coverage amount

    **Permissions:** Administrator, Parent (own children), Student (own only)
    """
    try:
        eligibility = await service.check_eligibility(bursary_id, student_id)
        return BursaryEligibilitySchema(**eligibility)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check eligibility: {str(e)}"
        )


# 6. Update Bursary
@router.put("/{bursary_id}", response_model=BursaryResponseSchema)
async def update_bursary(
    bursary_id: uuid.UUID,
    bursary_data: BursaryUpdateSchema,
    service: BursaryService = Depends(get_bursary_service)
):
    """
    Update bursary details.

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = TEMP_ADMIN_ID

        updated_bursary = await service.update_bursary(
            bursary_id=bursary_id,
            updated_by_id=current_user_id,
            name=bursary_data.name,
            description=bursary_data.description,
            coverage_type=bursary_data.coverage_type.value if bursary_data.coverage_type else None,
            coverage_value=bursary_data.coverage_value,
            max_coverage_amount=bursary_data.max_coverage_amount,
            eligible_grades=bursary_data.eligible_grades,
            max_recipients=bursary_data.max_recipients,
            application_deadline=bursary_data.application_deadline,
            sponsor_name=bursary_data.sponsor_name,
            sponsor_contact=bursary_data.sponsor_contact,
            terms_and_conditions=bursary_data.terms_and_conditions,
            is_active=bursary_data.is_active
        )

        if not updated_bursary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bursary not found"
            )

        return BursaryResponseSchema(**updated_bursary.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update bursary: {str(e)}"
        )


# 7. Get Bursary Statistics
@router.get("/statistics/summary", response_model=BursaryStatisticsSchema)
async def get_statistics(
    school_id: uuid.UUID = Query(...),
    academic_year: Optional[str] = Query(None, pattern=r'^\d{4}-\d{4}$'),
    service: BursaryService = Depends(get_bursary_service)
):
    """
    Get comprehensive bursary statistics.

    Includes:
    - Total and active bursaries
    - Total recipients
    - Total amount distributed
    - Breakdown by bursary type

    **Permissions:** Administrator
    """
    try:
        stats = await service.get_statistics(school_id, academic_year)
        return BursaryStatisticsSchema(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


# 8. Delete Bursary
@router.delete("/{bursary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bursary(
    bursary_id: uuid.UUID,
    service: BursaryService = Depends(get_bursary_service)
):
    """
    Delete bursary (soft delete).

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = TEMP_ADMIN_ID

        success = await service.delete_bursary(bursary_id, current_user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bursary not found"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete bursary: {str(e)}"
        )
