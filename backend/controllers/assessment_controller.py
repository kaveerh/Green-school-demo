"""
Assessment Controller

API endpoints for Assessment CRUD operations and grading.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from services.assessment_service import AssessmentService
from schemas.assessment_schema import (
    AssessmentCreateSchema,
    AssessmentUpdateSchema,
    AssessmentGradeSchema,
    AssessmentResponseSchema,
    AssessmentListResponseSchema,
    AssessmentStatisticsSchema
)
from config.database import get_db
import uuid


router = APIRouter(prefix="/assessments", tags=["assessments"])


# Dependency to get AssessmentService
async def get_assessment_service(session: AsyncSession = Depends(get_db)) -> AssessmentService:
    return AssessmentService(session)


# 1. Create Assessment
@router.post("", response_model=AssessmentResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_data: AssessmentCreateSchema,
    service: AssessmentService = Depends(get_assessment_service)
):
    """
    Create a new assessment.

    **Required:**
    - school_id, student_id, class_id, subject_id, teacher_id
    - title, assessment_type, quarter, assessment_date
    - total_points

    **Optional:**
    - description, due_date, points_earned
    - status (default: pending), weight (default: 1.0)
    - is_extra_credit, is_makeup

    **Permissions:** Teacher, Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()  # Placeholder

        assessment = await service.create_assessment(
            school_id=assessment_data.school_id,
            student_id=assessment_data.student_id,
            class_id=assessment_data.class_id,
            subject_id=assessment_data.subject_id,
            teacher_id=assessment_data.teacher_id,
            title=assessment_data.title,
            description=assessment_data.description,
            assessment_type=assessment_data.assessment_type.value,
            quarter=assessment_data.quarter.value,
            assessment_date=assessment_data.assessment_date,
            due_date=assessment_data.due_date,
            total_points=assessment_data.total_points,
            points_earned=assessment_data.points_earned,
            status=assessment_data.status.value if assessment_data.status else "pending",
            weight=assessment_data.weight or 1.0,
            created_by_id=current_user_id
        )

        return AssessmentResponseSchema(**assessment.to_dict(include_relationships=True))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create assessment: {str(e)}"
        )


# 2. Get Assessment by ID
@router.get("/{assessment_id}", response_model=AssessmentResponseSchema)
async def get_assessment(
    assessment_id: uuid.UUID,
    service: AssessmentService = Depends(get_assessment_service)
):
    """
    Get a specific assessment by ID with relationships.

    **Permissions:** Teacher, Administrator, Student (own only), Parent (children only)
    """
    try:
        assessment = await service.repository.get_with_relationships(assessment_id)

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )

        return AssessmentResponseSchema(**assessment.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get assessment: {str(e)}"
        )


# 3. Grade Assessment
@router.post("/{assessment_id}/grade", response_model=AssessmentResponseSchema)
async def grade_assessment(
    assessment_id: uuid.UUID,
    grade_data: AssessmentGradeSchema,
    service: AssessmentService = Depends(get_assessment_service)
):
    """
    Grade an assessment with points earned and feedback.

    Automatically calculates percentage and assigns letter grade.

    **Permissions:** Teacher (assigned), Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()  # Placeholder

        assessment = await service.grade_assessment(
            assessment_id=assessment_id,
            points_earned=grade_data.points_earned,
            feedback=grade_data.feedback,
            updated_by_id=current_user_id
        )

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )

        return AssessmentResponseSchema(**assessment.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to grade assessment: {str(e)}"
        )


# 4. Get Student Assessments
@router.get("/student/{student_id}", response_model=AssessmentListResponseSchema)
async def get_student_assessments(
    student_id: uuid.UUID,
    quarter: Optional[str] = Query(None, description="Filter by quarter (Q1, Q2, Q3, Q4)"),
    subject_id: Optional[uuid.UUID] = Query(None, description="Filter by subject"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Results per page"),
    service: AssessmentService = Depends(get_assessment_service)
):
    """
    Get all assessments for a student with optional filters.

    **Query Parameters:**
    - quarter: Filter by Q1, Q2, Q3, or Q4
    - subject_id: Filter by subject
    - page, limit: Pagination

    **Permissions:** Teacher, Administrator, Student (own only), Parent (children only)
    """
    try:
        assessments, total = await service.get_student_assessments(
            student_id=student_id,
            quarter=quarter,
            subject_id=subject_id,
            page=page,
            limit=limit
        )

        return AssessmentListResponseSchema(
            assessments=[AssessmentResponseSchema(**a.to_dict(include_relationships=True)) for a in assessments],
            total=total,
            page=page,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student assessments: {str(e)}"
        )


# 5. Get Class Assessments
@router.get("/class/{class_id}", response_model=AssessmentListResponseSchema)
async def get_class_assessments(
    class_id: uuid.UUID,
    quarter: Optional[str] = Query(None, description="Filter by quarter"),
    assessment_type: Optional[str] = Query(None, description="Filter by type"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    service: AssessmentService = Depends(get_assessment_service)
):
    """
    Get all assessments for a class with optional filters.

    **Permissions:** Teacher (assigned), Administrator
    """
    try:
        assessments, total = await service.get_class_assessments(
            class_id=class_id,
            quarter=quarter,
            assessment_type=assessment_type,
            page=page,
            limit=limit
        )

        return AssessmentListResponseSchema(
            assessments=[AssessmentResponseSchema(**a.to_dict(include_relationships=True)) for a in assessments],
            total=total,
            page=page,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get class assessments: {str(e)}"
        )


# 6. Get Teacher Assessments
@router.get("/teacher/{teacher_id}", response_model=AssessmentListResponseSchema)
async def get_teacher_assessments(
    teacher_id: uuid.UUID,
    quarter: Optional[str] = Query(None, description="Filter by quarter"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    service: AssessmentService = Depends(get_assessment_service)
):
    """
    Get all assessments for a teacher with optional filters.

    **Permissions:** Teacher (own), Administrator
    """
    try:
        assessments, total = await service.get_teacher_assessments(
            teacher_id=teacher_id,
            quarter=quarter,
            status=status,
            page=page,
            limit=limit
        )

        return AssessmentListResponseSchema(
            assessments=[AssessmentResponseSchema(**a.to_dict(include_relationships=True)) for a in assessments],
            total=total,
            page=page,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get teacher assessments: {str(e)}"
        )


# 7. Update Assessment
@router.put("/{assessment_id}", response_model=AssessmentResponseSchema)
async def update_assessment(
    assessment_id: uuid.UUID,
    assessment_data: AssessmentUpdateSchema,
    service: AssessmentService = Depends(get_assessment_service)
):
    """
    Update assessment information.

    All fields are optional. Only provided fields will be updated.

    **Permissions:** Teacher (assigned), Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()  # Placeholder

        assessment = await service.repository.get_by_id(assessment_id)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )

        # Update fields
        if assessment_data.title is not None:
            assessment.title = assessment_data.title
        if assessment_data.description is not None:
            assessment.description = assessment_data.description
        if assessment_data.assessment_type is not None:
            assessment.assessment_type = assessment_data.assessment_type.value
        if assessment_data.assessment_date is not None:
            assessment.assessment_date = assessment_data.assessment_date
        if assessment_data.due_date is not None:
            assessment.due_date = assessment_data.due_date
        if assessment_data.total_points is not None:
            assessment.total_points = assessment_data.total_points
        if assessment_data.weight is not None:
            assessment.weight = assessment_data.weight
        if assessment_data.status is not None:
            assessment.status = assessment_data.status.value
        if assessment_data.is_extra_credit is not None:
            assessment.is_extra_credit = assessment_data.is_extra_credit
        if assessment_data.is_makeup is not None:
            assessment.is_makeup = assessment_data.is_makeup

        assessment.updated_by = current_user_id

        updated_assessment = await service.repository.update(assessment)

        return AssessmentResponseSchema(**updated_assessment.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update assessment: {str(e)}"
        )


# 8. Delete Assessment
@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment(
    assessment_id: uuid.UUID,
    service: AssessmentService = Depends(get_assessment_service)
):
    """
    Soft delete an assessment.

    **Permissions:** Teacher (assigned), Administrator only
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()  # Placeholder

        success = await service.delete_assessment(assessment_id, current_user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete assessment: {str(e)}"
        )


# 9. Get Statistics
@router.get("/statistics/summary", response_model=AssessmentStatisticsSchema)
async def get_assessment_statistics(
    school_id: uuid.UUID = Query(..., description="School ID"),
    quarter: Optional[str] = Query(None, description="Filter by quarter"),
    service: AssessmentService = Depends(get_assessment_service)
):
    """
    Get assessment statistics for a school.

    Returns:
    - Total assessments
    - Graded/pending counts
    - Average score
    - Breakdown by type

    **Permissions:** Administrator
    """
    try:
        stats = await service.get_statistics(school_id, quarter)

        return AssessmentStatisticsSchema(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
