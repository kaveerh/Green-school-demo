"""
Activity Controller

HTTP request handlers for Activity and ActivityEnrollment operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date
import uuid

from config.database import get_db
from services.activity_service import ActivityService
from schemas.activity_schema import (
    ActivityCreateSchema,
    ActivityUpdateSchema,
    ActivityResponseSchema,
    ActivityListResponseSchema,
    EnrollmentCreateSchema,
    EnrollmentWithdrawSchema,
    EnrollmentResponseSchema,
    PaymentRecordSchema,
    ConsentUpdateSchema,
    RosterResponseSchema,
    PaymentSummarySchema,
    ActivityStatisticsSchema
)

router = APIRouter(prefix="/activities", tags=["activities"])


def get_activity_service(db: AsyncSession = Depends(get_db)) -> ActivityService:
    """Dependency to get ActivityService instance"""
    return ActivityService(db)


# ===== Activity CRUD Endpoints =====

@router.post("", response_model=ActivityResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity_data: ActivityCreateSchema,
    created_by_id: uuid.UUID = Query(..., description="ID of user creating the activity"),
    service: ActivityService = Depends(get_activity_service)
):
    """
    Create a new extracurricular activity

    - **school_id**: School ID (required)
    - **name**: Activity name (required)
    - **activity_type**: Type (sports, club, art, music, academic, other) (required)
    - **grade_levels**: Eligible grade levels 1-7 (required)
    - **code**: Unique activity code (optional)
    - **coordinator_id**: Coordinator user ID (optional)
    - **max_participants**: Maximum enrollment capacity (optional)
    - **schedule**: Days and times JSONB (optional)
    - **cost, registration_fee, equipment_fee**: Financial details
    - **requirements**: Array of requirements (optional)
    """
    try:
        activity = await service.create_activity(
            school_id=activity_data.school_id,
            name=activity_data.name,
            activity_type=activity_data.activity_type.value,
            grade_levels=activity_data.grade_levels,
            created_by_id=created_by_id,
            code=activity_data.code,
            category=activity_data.category,
            description=activity_data.description,
            coordinator_id=activity_data.coordinator_id,
            max_participants=activity_data.max_participants,
            min_participants=activity_data.min_participants,
            schedule=activity_data.schedule,
            start_date=activity_data.start_date,
            end_date=activity_data.end_date,
            location=activity_data.location,
            room_id=activity_data.room_id,
            cost=activity_data.cost,
            registration_fee=activity_data.registration_fee,
            equipment_fee=activity_data.equipment_fee,
            requirements=activity_data.requirements,
            equipment_needed=activity_data.equipment_needed,
            uniform_required=activity_data.uniform_required,
            contact_email=activity_data.contact_email,
            contact_phone=activity_data.contact_phone,
            parent_info=activity_data.parent_info,
            status=activity_data.status.value,
            is_featured=activity_data.is_featured,
            registration_open=activity_data.registration_open,
            photo_url=activity_data.photo_url,
            color=activity_data.color
        )
        return ActivityResponseSchema.model_validate(activity.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=ActivityListResponseSchema)
async def get_activities(
    school_id: uuid.UUID = Query(..., description="School ID"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    activity_status: Optional[str] = Query(None, description="Filter by status"),
    grade_level: Optional[int] = Query(None, ge=1, le=7, description="Filter by grade level"),
    registration_open: Optional[bool] = Query(None, description="Filter by registration status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: ActivityService = Depends(get_activity_service)
):
    """
    Get all activities for a school with optional filters

    Supports filtering by:
    - Activity type (sports, club, art, music, academic, other)
    - Status (active, full, cancelled, completed)
    - Grade level (1-7)
    - Registration open/closed

    Returns paginated results.
    """
    try:
        activities, total = await service.repository.get_by_school(
            school_id=school_id,
            activity_type=activity_type,
            status=activity_status,
            grade_level=grade_level,
            registration_open=registration_open,
            page=page,
            limit=limit
        )

        pages = (total + limit - 1) // limit

        return ActivityListResponseSchema(
            activities=[ActivityResponseSchema.model_validate(a.to_dict(include_relationships=False)) for a in activities],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{activity_id}", response_model=ActivityResponseSchema)
async def get_activity_by_id(
    activity_id: uuid.UUID,
    service: ActivityService = Depends(get_activity_service)
):
    """Get a specific activity by ID"""
    try:
        activity = await service.repository.get_with_relationships(activity_id)
        if not activity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        return ActivityResponseSchema.model_validate(activity.to_dict(include_relationships=True))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{activity_id}", response_model=ActivityResponseSchema)
async def update_activity(
    activity_id: uuid.UUID,
    activity_data: ActivityUpdateSchema,
    updated_by_id: uuid.UUID = Query(..., description="ID of user updating the activity"),
    service: ActivityService = Depends(get_activity_service)
):
    """Update an existing activity"""
    try:
        updates = activity_data.model_dump(exclude_unset=True)

        # Convert enums to values
        if 'activity_type' in updates and updates['activity_type']:
            updates['activity_type'] = updates['activity_type'].value
        if 'status' in updates and updates['status']:
            updates['status'] = updates['status'].value

        activity = await service.update_activity(
            activity_id=activity_id,
            updated_by_id=updated_by_id,
            **updates
        )

        if not activity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

        return ActivityResponseSchema.model_validate(activity.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: uuid.UUID,
    deleted_by_id: uuid.UUID = Query(..., description="ID of user deleting the activity"),
    service: ActivityService = Depends(get_activity_service)
):
    """Soft delete an activity"""
    try:
        success = await service.delete_activity(activity_id, deleted_by_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== Query Endpoints =====

@router.get("/type/{activity_type}", response_model=ActivityListResponseSchema)
async def get_activities_by_type(
    activity_type: str,
    school_id: uuid.UUID = Query(..., description="School ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: ActivityService = Depends(get_activity_service)
):
    """
    Get activities by type

    Valid types: sports, club, art, music, academic, other
    """
    try:
        activities, total = await service.repository.get_by_type(school_id, activity_type, page, limit)
        pages = (total + limit - 1) // limit

        return ActivityListResponseSchema(
            activities=[ActivityResponseSchema.model_validate(a.to_dict(include_relationships=False)) for a in activities],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/coordinator/{coordinator_id}", response_model=ActivityListResponseSchema)
async def get_activities_by_coordinator(
    coordinator_id: uuid.UUID,
    school_id: uuid.UUID = Query(..., description="School ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: ActivityService = Depends(get_activity_service)
):
    """Get activities coordinated by a specific user"""
    try:
        activities, total = await service.repository.get_by_coordinator(coordinator_id, school_id, page, limit)
        pages = (total + limit - 1) // limit

        return ActivityListResponseSchema(
            activities=[ActivityResponseSchema.model_validate(a.to_dict(include_relationships=False)) for a in activities],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/featured/list", response_model=List[ActivityResponseSchema])
async def get_featured_activities(
    school_id: uuid.UUID = Query(..., description="School ID"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of activities to return"),
    service: ActivityService = Depends(get_activity_service)
):
    """Get featured activities for a school"""
    try:
        activities = await service.repository.get_featured(school_id, limit)
        return [ActivityResponseSchema.model_validate(a.to_dict(include_relationships=False)) for a in activities]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/search/query", response_model=ActivityListResponseSchema)
async def search_activities(
    school_id: uuid.UUID = Query(..., description="School ID"),
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: ActivityService = Depends(get_activity_service)
):
    """Search activities by name, description, or category"""
    try:
        activities, total = await service.repository.search(school_id, q, page, limit)
        pages = (total + limit - 1) // limit

        return ActivityListResponseSchema(
            activities=[ActivityResponseSchema.model_validate(a.to_dict(include_relationships=False)) for a in activities],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== Enrollment Endpoints =====

@router.post("/{activity_id}/enroll", response_model=EnrollmentResponseSchema, status_code=status.HTTP_201_CREATED)
async def enroll_student(
    activity_id: uuid.UUID,
    enrollment_data: EnrollmentCreateSchema,
    created_by_id: uuid.UUID = Query(..., description="ID of user creating the enrollment"),
    service: ActivityService = Depends(get_activity_service)
):
    """
    Enroll a student in an activity

    - Validates student's grade level eligibility
    - Checks activity capacity
    - Creates enrollment or adds to waitlist if full
    - Requires parent consent and emergency contact info
    """
    try:
        enrollment = await service.enroll_student(
            activity_id=activity_id,
            student_id=enrollment_data.student_id,
            parent_consent=enrollment_data.parent_consent,
            medical_clearance=enrollment_data.medical_clearance,
            emergency_contact_provided=enrollment_data.emergency_contact_provided,
            created_by_id=created_by_id
        )
        return EnrollmentResponseSchema.model_validate(enrollment.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{activity_id}/withdraw/{student_id}", response_model=EnrollmentResponseSchema)
async def withdraw_student(
    activity_id: uuid.UUID,
    student_id: uuid.UUID,
    withdrawal_data: EnrollmentWithdrawSchema,
    withdrawn_by_id: uuid.UUID = Query(..., description="ID of user withdrawing the student"),
    service: ActivityService = Depends(get_activity_service)
):
    """
    Withdraw a student from an activity

    - Updates enrollment status to withdrawn
    - Automatically promotes first student from waitlist if applicable
    """
    try:
        enrollment = await service.withdraw_student(
            activity_id=activity_id,
            student_id=student_id,
            withdrawn_by_id=withdrawn_by_id,
            reason=withdrawal_data.reason
        )
        if not enrollment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        return EnrollmentResponseSchema.model_validate(enrollment.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{activity_id}/roster", response_model=RosterResponseSchema)
async def get_activity_roster(
    activity_id: uuid.UUID,
    service: ActivityService = Depends(get_activity_service)
):
    """
    Get complete roster for an activity

    Returns:
    - Activity details
    - Active enrollments
    - Waitlisted enrollments
    - Available slots
    """
    try:
        roster = await service.get_activity_roster(activity_id)
        return roster
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/student/{student_id}/enrollments", response_model=List[EnrollmentResponseSchema])
async def get_student_activities(
    student_id: uuid.UUID,
    enrollment_status: Optional[str] = Query(None, description="Filter by enrollment status"),
    service: ActivityService = Depends(get_activity_service)
):
    """Get all activities a student is enrolled in"""
    try:
        enrollments = await service.get_student_activities(student_id, enrollment_status)
        return [EnrollmentResponseSchema.model_validate(e.to_dict(include_relationships=True)) for e in enrollments]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== Payment Endpoints =====

@router.post("/enrollments/{enrollment_id}/payment", response_model=EnrollmentResponseSchema)
async def record_payment(
    enrollment_id: uuid.UUID,
    payment_data: PaymentRecordSchema,
    updated_by_id: uuid.UUID = Query(..., description="ID of user recording the payment"),
    service: ActivityService = Depends(get_activity_service)
):
    """
    Record a payment for an enrollment

    - Updates payment status (pending → partial → paid)
    - Prevents overpayment
    """
    try:
        enrollment = await service.record_payment(
            enrollment_id=enrollment_id,
            amount=payment_data.amount,
            updated_by_id=updated_by_id,
            payment_date=payment_data.payment_date
        )
        if not enrollment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        return EnrollmentResponseSchema.model_validate(enrollment.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/enrollments/{enrollment_id}/waive-payment", response_model=EnrollmentResponseSchema)
async def waive_payment(
    enrollment_id: uuid.UUID,
    updated_by_id: uuid.UUID = Query(..., description="ID of user waiving the payment"),
    service: ActivityService = Depends(get_activity_service)
):
    """Waive payment requirement for an enrollment"""
    try:
        enrollment = await service.waive_payment(enrollment_id, updated_by_id)
        if not enrollment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        return EnrollmentResponseSchema.model_validate(enrollment.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{activity_id}/payments", response_model=PaymentSummarySchema)
async def get_payment_summary(
    activity_id: uuid.UUID,
    service: ActivityService = Depends(get_activity_service)
):
    """
    Get payment summary for an activity

    Returns:
    - Total expected revenue
    - Total collected
    - Total outstanding
    - Payment status breakdown
    """
    try:
        summary = await service.get_payment_summary(activity_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== Statistics Endpoint =====

@router.get("/statistics/summary", response_model=ActivityStatisticsSchema)
async def get_activity_statistics(
    school_id: uuid.UUID = Query(..., description="School ID"),
    service: ActivityService = Depends(get_activity_service)
):
    """
    Get activity statistics for a school

    Returns:
    - Total activities by type and status
    - Total enrollments
    - Average enrollment per activity
    - Total revenue and outstanding payments
    """
    try:
        stats = await service.get_statistics(school_id)
        return ActivityStatisticsSchema.model_validate(stats)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
