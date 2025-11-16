"""
Fee Structure Controller

API endpoints for Fee Structure CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from services.fee_structure_service import FeeStructureService
from schemas.fee_structure_schema import (
    FeeStructureCreateSchema,
    FeeStructureUpdateSchema,
    FeeStructureResponseSchema,
    FeeStructureListResponseSchema
)
from config.database import get_db
import uuid
import math


router = APIRouter(prefix="/fee-structures", tags=["fee-structures"])


# Dependency
async def get_fee_structure_service(session: AsyncSession = Depends(get_db)) -> FeeStructureService:
    return FeeStructureService(session)


# 1. Create Fee Structure
@router.post("", response_model=FeeStructureResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_fee_structure(
    fee_structure_data: FeeStructureCreateSchema,
    service: FeeStructureService = Depends(get_fee_structure_service)
):
    """
    Create a new fee structure for a grade level and academic year.

    **Business Rules:**
    - One fee structure per grade level per academic year
    - Grades must be 1-7
    - Academic year format: YYYY-YYYY (e.g., 2024-2025)

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()

        fee_structure = await service.create_fee_structure(
            school_id=fee_structure_data.school_id,
            grade_level=fee_structure_data.grade_level,
            academic_year=fee_structure_data.academic_year,
            yearly_amount=fee_structure_data.yearly_amount,
            monthly_amount=fee_structure_data.monthly_amount,
            weekly_amount=fee_structure_data.weekly_amount,
            yearly_discount=fee_structure_data.yearly_discount,
            monthly_discount=fee_structure_data.monthly_discount,
            weekly_discount=fee_structure_data.weekly_discount,
            sibling_2_discount=fee_structure_data.sibling_2_discount,
            sibling_3_discount=fee_structure_data.sibling_3_discount,
            sibling_4_plus_discount=fee_structure_data.sibling_4_plus_discount,
            apply_sibling_to_all=fee_structure_data.apply_sibling_to_all,
            created_by_id=current_user_id
        )

        return FeeStructureResponseSchema(**fee_structure.to_dict(include_relationships=True))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create fee structure: {str(e)}"
        )


# 2. Get Fee Structure by ID
@router.get("/{fee_structure_id}", response_model=FeeStructureResponseSchema)
async def get_fee_structure(
    fee_structure_id: uuid.UUID,
    service: FeeStructureService = Depends(get_fee_structure_service)
):
    """
    Get a specific fee structure by ID.

    **Permissions:** Administrator
    """
    try:
        fee_structure = await service.get_fee_structure(fee_structure_id, include_relationships=True)

        if not fee_structure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fee structure not found"
            )

        return FeeStructureResponseSchema(**fee_structure.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get fee structure: {str(e)}"
        )


# 3. Get Fee Structure for Grade and Year
@router.get("/grade/{grade_level}/year/{academic_year}", response_model=FeeStructureResponseSchema)
async def get_fee_structure_by_grade_year(
    grade_level: int = Path(..., ge=1, le=7),
    academic_year: str = Path(..., pattern=r'^\d{4}-\d{4}$'),
    school_id: uuid.UUID = Query(...),
    service: FeeStructureService = Depends(get_fee_structure_service)
):
    """
    Get fee structure for a specific grade level and academic year.

    **Permissions:** Administrator
    """
    try:
        fee_structure = await service.get_by_grade_and_year(
            school_id=school_id,
            grade_level=grade_level,
            academic_year=academic_year
        )

        if not fee_structure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fee structure not found for Grade {grade_level}, {academic_year}"
            )

        return FeeStructureResponseSchema(**fee_structure.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get fee structure: {str(e)}"
        )


# 4. List Fee Structures
@router.get("", response_model=FeeStructureListResponseSchema)
async def list_fee_structures(
    school_id: uuid.UUID = Query(...),
    academic_year: Optional[str] = Query(None, pattern=r'^\d{4}-\d{4}$'),
    grade_level: Optional[int] = Query(None, ge=1, le=7),
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: FeeStructureService = Depends(get_fee_structure_service)
):
    """
    List fee structures with filtering and pagination.

    **Filters:**
    - academic_year: Filter by academic year
    - grade_level: Filter by grade (1-7)
    - is_active: Filter active/inactive structures

    **Permissions:** Administrator
    """
    try:
        fee_structures, total = await service.list_fee_structures(
            school_id=school_id,
            academic_year=academic_year,
            grade_level=grade_level,
            is_active=is_active,
            page=page,
            limit=limit
        )

        pages = math.ceil(total / limit) if total > 0 else 0

        return FeeStructureListResponseSchema(
            data=[FeeStructureResponseSchema(**fs.to_dict(include_relationships=True)) for fs in fee_structures],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list fee structures: {str(e)}"
        )


# 5. Update Fee Structure
@router.put("/{fee_structure_id}", response_model=FeeStructureResponseSchema)
async def update_fee_structure(
    fee_structure_id: uuid.UUID,
    fee_structure_data: FeeStructureUpdateSchema,
    service: FeeStructureService = Depends(get_fee_structure_service)
):
    """
    Update fee structure details.

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()

        updated_fee_structure = await service.update_fee_structure(
            fee_structure_id=fee_structure_id,
            updated_by_id=current_user_id,
            yearly_amount=fee_structure_data.yearly_amount,
            monthly_amount=fee_structure_data.monthly_amount,
            weekly_amount=fee_structure_data.weekly_amount,
            yearly_discount=fee_structure_data.yearly_discount,
            monthly_discount=fee_structure_data.monthly_discount,
            weekly_discount=fee_structure_data.weekly_discount,
            sibling_2_discount=fee_structure_data.sibling_2_discount,
            sibling_3_discount=fee_structure_data.sibling_3_discount,
            sibling_4_plus_discount=fee_structure_data.sibling_4_plus_discount,
            apply_sibling_to_all=fee_structure_data.apply_sibling_to_all,
            is_active=fee_structure_data.is_active
        )

        if not updated_fee_structure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fee structure not found"
            )

        return FeeStructureResponseSchema(**updated_fee_structure.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update fee structure: {str(e)}"
        )


# 6. Delete Fee Structure
@router.delete("/{fee_structure_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fee_structure(
    fee_structure_id: uuid.UUID,
    service: FeeStructureService = Depends(get_fee_structure_service)
):
    """
    Delete fee structure (soft delete).

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()

        success = await service.delete_fee_structure(fee_structure_id, current_user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fee structure not found"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete fee structure: {str(e)}"
        )
