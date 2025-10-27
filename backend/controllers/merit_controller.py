"""
Merit Controller

HTTP request handlers for Merit operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date
import uuid

from config.database import get_db
from repositories.merit_repository import MeritRepository
from services.merit_service import MeritService
from schemas.merit_schema import (
    MeritCreateSchema,
    MeritBatchCreateSchema,
    MeritUpdateSchema,
    MeritResponseSchema,
    MeritListResponseSchema,
    MeritSummarySchema,
    ClassMeritSummarySchema,
    LeaderboardEntrySchema,
    MeritStatisticsSchema,
)

router = APIRouter(prefix="/merits", tags=["merits"])


def get_merit_service(db: AsyncSession = Depends(get_db)) -> MeritService:
    """Dependency to get MeritService instance"""
    repository = MeritRepository(db)
    return MeritService(repository)


# ===== Merit CRUD Endpoints =====

@router.post("", response_model=MeritResponseSchema, status_code=status.HTTP_201_CREATED)
async def award_merit(
    merit_data: MeritCreateSchema,
    awarded_by_id: uuid.UUID = Query(..., description="ID of user awarding the merit"),
    service: MeritService = Depends(get_merit_service)
):
    """
    Award merit to a student

    - **student_id**: Student receiving the merit (required)
    - **category**: Merit category (required)
    - **points**: Merit points 1-10 (required)
    - **reason**: Description of achievement (required, min 10 chars)
    """
    try:
        merit = await service.award_merit(
            school_id=merit_data.school_id,
            student_id=merit_data.student_id,
            awarded_by_id=awarded_by_id,
            category=merit_data.category.value,
            points=merit_data.points,
            reason=merit_data.reason,
            class_id=merit_data.class_id,
            subject_id=merit_data.subject_id,
            quarter=merit_data.quarter.value if merit_data.quarter else None,
            academic_year=merit_data.academic_year,
            awarded_date=merit_data.awarded_date
        )
        return MeritResponseSchema.model_validate(merit.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/batch", response_model=List[MeritResponseSchema], status_code=status.HTTP_201_CREATED)
async def award_batch_merits(
    merit_data: MeritBatchCreateSchema,
    awarded_by_id: uuid.UUID = Query(..., description="ID of user awarding the merits"),
    service: MeritService = Depends(get_merit_service)
):
    """
    Award merits to multiple students (class award)

    - **student_ids**: List of student IDs (required)
    - **category**: Merit category (required)
    - **points**: Merit points 1-10 (required)
    - **reason**: Description of achievement (required)
    """
    try:
        merits = await service.award_batch_merits(
            school_id=merit_data.school_id,
            student_ids=merit_data.student_ids,
            awarded_by_id=awarded_by_id,
            category=merit_data.category.value,
            points=merit_data.points,
            reason=merit_data.reason,
            class_id=merit_data.class_id,
            subject_id=merit_data.subject_id,
            quarter=merit_data.quarter.value if merit_data.quarter else None,
            academic_year=merit_data.academic_year,
            awarded_date=merit_data.awarded_date
        )
        return [MeritResponseSchema.model_validate(m.to_dict(include_relationships=True)) for m in merits]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=MeritListResponseSchema)
async def get_merits(
    school_id: uuid.UUID = Query(..., description="School ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    quarter: Optional[str] = Query(None, description="Filter by quarter"),
    awarded_by_id: Optional[uuid.UUID] = Query(None, description="Filter by awarder"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: MeritService = Depends(get_merit_service)
):
    """
    Get all merits for a school with optional filters

    Supports filtering by:
    - Category (academic, behavior, participation, leadership, attendance, other)
    - Quarter (Q1, Q2, Q3, Q4)
    - Awarded by (teacher/admin)
    - Date range

    Returns paginated results.
    """
    try:
        merits, total = await service.repository.get_by_school(
            school_id=school_id,
            category=category,
            quarter=quarter,
            awarded_by_id=awarded_by_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )

        pages = (total + limit - 1) // limit

        return MeritListResponseSchema(
            merits=[MeritResponseSchema.model_validate(m.to_dict(include_relationships=True)) for m in merits],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{merit_id}", response_model=MeritResponseSchema)
async def get_merit_by_id(
    merit_id: uuid.UUID,
    service: MeritService = Depends(get_merit_service)
):
    """
    Get merit by ID

    Returns full merit information including relationships.
    """
    try:
        merit = await service.repository.get_by_id(merit_id)
        if not merit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merit not found")

        return MeritResponseSchema.model_validate(merit.to_dict(include_relationships=True))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{merit_id}", response_model=MeritResponseSchema)
async def update_merit(
    merit_id: uuid.UUID,
    merit_data: MeritUpdateSchema,
    updated_by_id: uuid.UUID = Query(..., description="ID of user updating the merit"),
    service: MeritService = Depends(get_merit_service)
):
    """
    Update merit information

    Limited fields can be updated (category, points, reason, quarter).
    """
    try:
        update_data = merit_data.model_dump(exclude_unset=True)

        # Convert enum values to strings
        if 'category' in update_data and update_data['category']:
            update_data['category'] = update_data['category'].value
        if 'quarter' in update_data and update_data['quarter']:
            update_data['quarter'] = update_data['quarter'].value

        merit = await service.update_merit(
            merit_id=merit_id,
            updated_by_id=updated_by_id,
            **update_data
        )
        return MeritResponseSchema.model_validate(merit.to_dict(include_relationships=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{merit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_merit(
    merit_id: uuid.UUID,
    deleted_by_id: uuid.UUID = Query(..., description="ID of user revoking the merit"),
    service: MeritService = Depends(get_merit_service)
):
    """
    Revoke merit (soft delete)

    Only administrators should be able to revoke merits.
    Maintains audit trail.
    """
    try:
        await service.revoke_merit(merit_id, deleted_by_id=deleted_by_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ===== Query Endpoints =====

@router.get("/student/{student_id}", response_model=MeritListResponseSchema)
async def get_student_merits(
    student_id: uuid.UUID,
    category: Optional[str] = Query(None, description="Filter by category"),
    quarter: Optional[str] = Query(None, description="Filter by quarter"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: MeritService = Depends(get_merit_service)
):
    """
    Get all merits for a student

    Returns merit history with optional filters.
    """
    try:
        merits, total = await service.repository.get_by_student(
            student_id=student_id,
            category=category,
            quarter=quarter,
            page=page,
            limit=limit
        )

        pages = (total + limit - 1) // limit

        return MeritListResponseSchema(
            merits=[MeritResponseSchema.model_validate(m.to_dict(include_relationships=True)) for m in merits],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/student/{student_id}/summary", response_model=MeritSummarySchema)
async def get_student_merit_summary(
    student_id: uuid.UUID,
    service: MeritService = Depends(get_merit_service)
):
    """
    Get merit summary for a student

    Returns total points, breakdown by category and quarter, and recent merits.
    """
    try:
        summary = await service.get_student_summary(student_id)
        return MeritSummarySchema(**summary)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/class/{class_id}", response_model=MeritListResponseSchema)
async def get_class_merits(
    class_id: uuid.UUID,
    quarter: Optional[str] = Query(None, description="Filter by quarter"),
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: MeritService = Depends(get_merit_service)
):
    """
    Get all merits for a class

    Returns merits awarded to students in the class.
    """
    try:
        merits, total = await service.repository.get_by_class(
            class_id=class_id,
            quarter=quarter,
            category=category,
            page=page,
            limit=limit
        )

        pages = (total + limit - 1) // limit

        return MeritListResponseSchema(
            merits=[MeritResponseSchema.model_validate(m.to_dict(include_relationships=True)) for m in merits],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/class/{class_id}/summary", response_model=ClassMeritSummarySchema)
async def get_class_merit_summary(
    class_id: uuid.UUID,
    quarter: Optional[str] = Query(None, description="Filter by quarter"),
    service: MeritService = Depends(get_merit_service)
):
    """
    Get class merit statistics

    Returns total points, average per student, breakdown by category, and top students.
    """
    try:
        summary = await service.get_class_summary(class_id, quarter)
        return ClassMeritSummarySchema(**summary)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/teacher/{teacher_id}", response_model=MeritListResponseSchema)
async def get_teacher_merits(
    teacher_id: uuid.UUID,
    quarter: Optional[str] = Query(None, description="Filter by quarter"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: MeritService = Depends(get_merit_service)
):
    """
    Get merits awarded by a teacher

    Returns all merits awarded by the specified teacher.
    """
    try:
        merits, total = await service.repository.get_by_teacher(
            teacher_id=teacher_id,
            quarter=quarter,
            page=page,
            limit=limit
        )

        pages = (total + limit - 1) // limit

        return MeritListResponseSchema(
            merits=[MeritResponseSchema.model_validate(m.to_dict(include_relationships=True)) for m in merits],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/leaderboard/rankings", response_model=List[LeaderboardEntrySchema])
async def get_merit_leaderboard(
    school_id: uuid.UUID = Query(..., description="School ID"),
    grade_level: Optional[int] = Query(None, ge=1, le=7, description="Filter by grade level"),
    quarter: Optional[str] = Query(None, description="Filter by quarter"),
    limit: int = Query(20, ge=1, le=100, description="Number of top students"),
    service: MeritService = Depends(get_merit_service)
):
    """
    Get merit leaderboard

    Returns top students ranked by total merit points.
    Can filter by grade level and quarter.
    """
    try:
        leaderboard = await service.get_leaderboard(
            school_id=school_id,
            grade_level=grade_level,
            quarter=quarter,
            limit=limit
        )
        return [LeaderboardEntrySchema(**entry) for entry in leaderboard]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/summary", response_model=MeritStatisticsSchema)
async def get_merit_statistics(
    school_id: uuid.UUID = Query(..., description="School ID"),
    quarter: Optional[str] = Query(None, description="Filter by quarter"),
    grade_level: Optional[int] = Query(None, ge=1, le=7, description="Filter by grade level"),
    service: MeritService = Depends(get_merit_service)
):
    """
    Get school-wide merit statistics

    Returns comprehensive statistics including:
    - Total merits and points
    - Breakdown by category
    - Breakdown by quarter
    - Average per student
    """
    try:
        stats = await service.get_statistics(
            school_id=school_id,
            quarter=quarter,
            grade_level=grade_level
        )
        return MeritStatisticsSchema(**stats)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
