"""
School Controller
API endpoints for school operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from config.database import get_db
from services.school_service import SchoolService
from schemas.school_schema import (
    SchoolCreateSchema,
    SchoolUpdateSchema,
    SchoolResponseSchema,
    SchoolListResponseSchema,
    SchoolSearchSchema,
    SchoolStatusChangeSchema,
    SchoolSettingsUpdateSchema,
    SchoolLeadershipSchema,
    SchoolStatisticsSchema,
    SchoolLogoUploadSchema,
    StatusEnum,
)
from utils.auth import CurrentUser, require_admin


router = APIRouter(prefix="/schools", tags=["Schools"])


@router.post(
    "",
    response_model=SchoolResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new school",
    description="Create a new school. Only system administrators can create schools."
)
async def create_school(
    school_data: SchoolCreateSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new school

    - **name**: School name (must be unique)
    - **slug**: URL-friendly identifier (auto-generated if not provided)
    - **address_line1**: Primary address line
    - **city**: City
    - **state**: State/Province
    - **postal_code**: Postal/ZIP code
    - **country**: Country (default: USA)
    - **phone**: Contact phone number
    - **email**: Contact email
    - **website_url**: School website
    - **principal_id**: Principal user UUID (optional)
    - **hod_id**: Head of Department user UUID (optional)
    - **timezone**: School timezone (default: America/New_York)
    - **locale**: School locale (default: en_US)
    """
    service = SchoolService(db)

    try:
        school = await service.create_school(school_data, current_user.id)
        return school
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=SchoolListResponseSchema,
    summary="List schools",
    description="Search and list schools with filters and pagination. Only administrators can list schools."
)
async def list_schools(
    search: Optional[str] = Query(None, description="Search in name, city, or email"),
    status_filter: Optional[StatusEnum] = Query(None, alias="status", description="Filter by status"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: str = Query("name", description="Sort field"),
    order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List schools with filtering and pagination

    Returns a paginated list of schools with metadata
    """
    service = SchoolService(db)

    search_params = SchoolSearchSchema(
        search=search,
        status=status_filter,
        city=city,
        state=state,
        page=page,
        limit=limit,
        sort=sort,
        order=order
    )

    schools, pagination = await service.search_schools(search_params)

    return {
        "data": schools,
        "pagination": pagination
    }


@router.get(
    "/slug/{slug}",
    response_model=SchoolResponseSchema,
    summary="Get a school by slug",
    description="Get a school by its URL slug"
)
async def get_school_by_slug(
    slug: str,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get school by slug

    - **slug**: School URL slug
    """
    service = SchoolService(db)
    school = await service.get_school_by_slug(slug)

    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )

    return school


@router.get(
    "/{school_id}",
    response_model=SchoolResponseSchema,
    summary="Get a school",
    description="Get a school by ID. Administrators can view any school."
)
async def get_school(
    school_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get school by ID

    - **school_id**: School UUID
    """
    service = SchoolService(db)
    school = await service.get_school(school_id)

    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )

    return school


@router.put(
    "/{school_id}",
    response_model=SchoolResponseSchema,
    summary="Update a school",
    description="Update a school. Only administrators can update schools."
)
async def update_school(
    school_id: uuid.UUID,
    school_data: SchoolUpdateSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update school

    - **school_id**: School UUID
    - All fields are optional
    """
    service = SchoolService(db)

    try:
        school = await service.update_school(
            school_id=school_id,
            school_data=school_data,
            updated_by_id=current_user.id
        )

        if not school:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="School not found"
            )

        return school
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{school_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a school",
    description="Soft delete a school. Only administrators can delete schools."
)
async def delete_school(
    school_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete school (soft delete)

    - **school_id**: School UUID
    """
    service = SchoolService(db)
    success = await service.delete_school(school_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )

    return None


@router.patch(
    "/{school_id}/status",
    response_model=SchoolResponseSchema,
    summary="Change school status",
    description="Change school status. Only administrators can change status."
)
async def change_school_status(
    school_id: uuid.UUID,
    status_data: SchoolStatusChangeSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Change school status

    - **school_id**: School UUID
    - **status**: New status (active, inactive, suspended)
    """
    service = SchoolService(db)
    school = await service.change_school_status(
        school_id=school_id,
        new_status=status_data.status.value,
        updated_by_id=current_user.id
    )

    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )

    return school


@router.patch(
    "/{school_id}/settings",
    response_model=SchoolResponseSchema,
    summary="Update school settings",
    description="Update school settings. Only administrators can update settings."
)
async def update_school_settings(
    school_id: uuid.UUID,
    settings_data: SchoolSettingsUpdateSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update school settings

    - **school_id**: School UUID
    - **settings**: Settings dictionary (will be merged with existing settings)
    """
    service = SchoolService(db)
    school = await service.update_school_settings(
        school_id=school_id,
        settings=settings_data.settings,
        updated_by_id=current_user.id
    )

    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )

    return school


@router.patch(
    "/{school_id}/leadership",
    response_model=SchoolResponseSchema,
    summary="Assign school leadership",
    description="Assign principal and/or HOD to school. Only administrators can assign leadership."
)
async def assign_leadership(
    school_id: uuid.UUID,
    leadership_data: SchoolLeadershipSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign school leadership

    - **school_id**: School UUID
    - **principal_id**: Principal user UUID (optional)
    - **hod_id**: HOD user UUID (optional)
    """
    service = SchoolService(db)

    try:
        # Assign principal if provided
        if leadership_data.principal_id:
            school = await service.assign_principal(
                school_id=school_id,
                principal_id=leadership_data.principal_id,
                updated_by_id=current_user.id
            )
            if not school:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="School not found"
                )

        # Assign HOD if provided
        if leadership_data.hod_id:
            school = await service.assign_hod(
                school_id=school_id,
                hod_id=leadership_data.hod_id,
                updated_by_id=current_user.id
            )
            if not school:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="School not found"
                )

        # Return updated school
        school = await service.get_school(school_id)
        return school

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{school_id}/logo",
    response_model=SchoolResponseSchema,
    summary="Upload school logo",
    description="Upload or update school logo URL. Only administrators can upload logos."
)
async def upload_school_logo(
    school_id: uuid.UUID,
    logo_data: SchoolLogoUploadSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload school logo

    - **school_id**: School UUID
    - **logo_url**: Logo URL (should be publicly accessible)
    """
    service = SchoolService(db)

    try:
        school = await service.update_school(
            school_id=school_id,
            school_data=SchoolUpdateSchema(logo_url=logo_data.logo_url),
            updated_by_id=current_user.id
        )

        if not school:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="School not found"
            )

        return school

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/statistics/summary",
    response_model=SchoolStatisticsSchema,
    summary="Get school statistics",
    description="Get school statistics. Only administrators can view statistics."
)
async def get_school_statistics(
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get school statistics

    Returns counts by status and state
    """
    service = SchoolService(db)
    stats = await service.get_statistics()
    return stats
