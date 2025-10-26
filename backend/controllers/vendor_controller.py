"""
Vendor Controller

HTTP request handlers for Vendor operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from config.database import get_db
from repositories.vendor_repository import VendorRepository
from services.vendor_service import VendorService
from schemas.vendor_schema import (
    VendorCreateSchema,
    VendorUpdateSchema,
    VendorStatusUpdateSchema,
    VendorRatingUpdateSchema,
    VendorResponseSchema,
    VendorListResponseSchema,
    VendorStatisticsSchema,
    VendorAlertsResponseSchema
)

router = APIRouter(prefix="/vendors", tags=["vendors"])


def get_vendor_service(db: AsyncSession = Depends(get_db)) -> VendorService:
    """Dependency to get VendorService instance"""
    repository = VendorRepository(db)
    return VendorService(repository)


# ===== Vendor CRUD Endpoints =====

@router.post("", response_model=VendorResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_data: VendorCreateSchema,
    created_by_id: uuid.UUID = Query(..., description="ID of user creating the vendor"),
    service: VendorService = Depends(get_vendor_service)
):
    """
    Create a new vendor

    - **school_id**: School ID (required)
    - **company_name**: Company name (required, unique per school)
    - **vendor_type**: Type of vendor (required)
    - **email**: Valid email address (optional)
    - **status**: Vendor status (default: active)
    """
    try:
        vendor = await service.create_vendor(
            school_id=vendor_data.school_id,
            company_name=vendor_data.company_name,
            vendor_type=vendor_data.vendor_type.value,
            created_by_id=created_by_id,
            user_id=vendor_data.user_id,
            business_number=vendor_data.business_number,
            category=vendor_data.category,
            services_provided=vendor_data.services_provided,
            primary_contact_name=vendor_data.primary_contact_name,
            primary_contact_title=vendor_data.primary_contact_title,
            email=vendor_data.email,
            phone=vendor_data.phone,
            phone_alt=vendor_data.phone_alt,
            website=vendor_data.website,
            address_line1=vendor_data.address_line1,
            address_line2=vendor_data.address_line2,
            city=vendor_data.city,
            state=vendor_data.state,
            postal_code=vendor_data.postal_code,
            country=vendor_data.country,
            description=vendor_data.description,
            certifications=vendor_data.certifications,
            insurance_policy_number=vendor_data.insurance_policy_number,
            insurance_expiry_date=vendor_data.insurance_expiry_date,
            contract_start_date=vendor_data.contract_start_date,
            contract_end_date=vendor_data.contract_end_date,
            contract_value=vendor_data.contract_value,
            payment_terms=vendor_data.payment_terms,
            tax_exempt=vendor_data.tax_exempt,
            status=vendor_data.status.value,
            performance_rating=vendor_data.performance_rating,
            total_orders=vendor_data.total_orders,
            preferred=vendor_data.preferred,
            notes=vendor_data.notes
        )
        return VendorResponseSchema.model_validate(vendor.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=VendorListResponseSchema)
async def get_vendors(
    school_id: uuid.UUID = Query(..., description="School ID"),
    vendor_type: Optional[str] = Query(None, description="Filter by vendor type"),
    vendor_status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: VendorService = Depends(get_vendor_service)
):
    """
    Get all vendors for a school with optional filters

    Supports filtering by:
    - Vendor type (food_service, supplies, maintenance, it_services, transportation, events, other)
    - Status (active, inactive, suspended, terminated)

    Returns paginated results.
    """
    try:
        vendors, total = await service.repository.get_by_school(
            school_id=school_id,
            vendor_type=vendor_type,
            status=vendor_status,
            page=page,
            limit=limit
        )

        pages = (total + limit - 1) // limit

        return VendorListResponseSchema(
            vendors=[VendorResponseSchema.model_validate(v.to_dict(include_relationships=False)) for v in vendors],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{vendor_id}", response_model=VendorResponseSchema)
async def get_vendor_by_id(
    vendor_id: uuid.UUID,
    service: VendorService = Depends(get_vendor_service)
):
    """
    Get vendor by ID

    Returns full vendor information including computed properties.
    """
    try:
        vendor = await service.repository.get_by_id(vendor_id)
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

        return VendorResponseSchema.model_validate(vendor.to_dict(include_relationships=True))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{vendor_id}", response_model=VendorResponseSchema)
async def update_vendor(
    vendor_id: uuid.UUID,
    vendor_data: VendorUpdateSchema,
    updated_by_id: uuid.UUID = Query(..., description="ID of user updating the vendor"),
    service: VendorService = Depends(get_vendor_service)
):
    """
    Update vendor information

    All fields are optional. Only provided fields will be updated.
    """
    try:
        update_data = vendor_data.model_dump(exclude_unset=True)

        # Convert enum values to strings
        if 'vendor_type' in update_data and update_data['vendor_type']:
            update_data['vendor_type'] = update_data['vendor_type'].value
        if 'status' in update_data and update_data['status']:
            update_data['status'] = update_data['status'].value

        vendor = await service.update_vendor(
            vendor_id=vendor_id,
            updated_by_id=updated_by_id,
            **update_data
        )
        return VendorResponseSchema.model_validate(vendor.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    vendor_id: uuid.UUID,
    deleted_by_id: uuid.UUID = Query(..., description="ID of user deleting the vendor"),
    service: VendorService = Depends(get_vendor_service)
):
    """
    Delete vendor (soft delete)

    Soft deletes the vendor, maintaining audit trail.
    """
    try:
        await service.delete_vendor(vendor_id, deleted_by_id=deleted_by_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== Query Endpoints =====

@router.get("/type/{vendor_type}", response_model=VendorListResponseSchema)
async def get_vendors_by_type(
    vendor_type: str,
    school_id: uuid.UUID = Query(..., description="School ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: VendorService = Depends(get_vendor_service)
):
    """
    Get vendors by type

    Returns vendors filtered by type with pagination.
    """
    try:
        vendors, total = await service.repository.get_by_type(
            school_id=school_id,
            vendor_type=vendor_type,
            page=page,
            limit=limit
        )

        pages = (total + limit - 1) // limit

        return VendorListResponseSchema(
            vendors=[VendorResponseSchema.model_validate(v.to_dict(include_relationships=False)) for v in vendors],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/search/query", response_model=VendorListResponseSchema)
async def search_vendors(
    school_id: uuid.UUID = Query(..., description="School ID"),
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: VendorService = Depends(get_vendor_service)
):
    """
    Search vendors

    Searches across company name, description, and category.
    """
    try:
        vendors, total = await service.repository.search(
            school_id=school_id,
            query_text=q,
            page=page,
            limit=limit
        )

        pages = (total + limit - 1) // limit

        return VendorListResponseSchema(
            vendors=[VendorResponseSchema.model_validate(v.to_dict(include_relationships=False)) for v in vendors],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/preferred/list", response_model=list[VendorResponseSchema])
async def get_preferred_vendors(
    school_id: uuid.UUID = Query(..., description="School ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of vendors"),
    service: VendorService = Depends(get_vendor_service)
):
    """
    Get preferred vendors

    Returns active vendors marked as preferred, ordered by rating.
    """
    try:
        vendors = await service.repository.get_preferred(school_id=school_id, limit=limit)
        return [VendorResponseSchema.model_validate(v.to_dict(include_relationships=False)) for v in vendors]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== Status Management =====

@router.patch("/{vendor_id}/status", response_model=VendorResponseSchema)
async def update_vendor_status(
    vendor_id: uuid.UUID,
    status_data: VendorStatusUpdateSchema,
    updated_by_id: uuid.UUID = Query(..., description="ID of user updating the status"),
    service: VendorService = Depends(get_vendor_service)
):
    """
    Update vendor status

    Changes vendor status (active, inactive, suspended, terminated).
    """
    try:
        vendor = await service.update_status(
            vendor_id=vendor_id,
            status=status_data.status.value,
            updated_by_id=updated_by_id
        )
        return VendorResponseSchema.model_validate(vendor.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{vendor_id}/rating", response_model=VendorResponseSchema)
async def update_vendor_rating(
    vendor_id: uuid.UUID,
    rating_data: VendorRatingUpdateSchema,
    updated_by_id: uuid.UUID = Query(..., description="ID of user updating the rating"),
    service: VendorService = Depends(get_vendor_service)
):
    """
    Update vendor performance rating

    Updates the performance rating (0-5).
    """
    try:
        vendor = await service.update_rating(
            vendor_id=vendor_id,
            rating=rating_data.rating,
            updated_by_id=updated_by_id
        )
        return VendorResponseSchema.model_validate(vendor.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== Alerts & Statistics =====

@router.get("/alerts/summary", response_model=VendorAlertsResponseSchema)
async def get_vendor_alerts(
    school_id: uuid.UUID = Query(..., description="School ID"),
    service: VendorService = Depends(get_vendor_service)
):
    """
    Get vendor-related alerts

    Returns alerts for expiring contracts and expired insurance.
    """
    try:
        alerts = await service.get_alerts(school_id=school_id)
        return VendorAlertsResponseSchema(**alerts)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/summary", response_model=VendorStatisticsSchema)
async def get_vendor_statistics(
    school_id: uuid.UUID = Query(..., description="School ID"),
    service: VendorService = Depends(get_vendor_service)
):
    """
    Get vendor statistics

    Returns comprehensive vendor statistics including counts, ratings, and contract values.
    """
    try:
        stats = await service.repository.get_statistics(school_id=school_id)
        return VendorStatisticsSchema(**stats)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
