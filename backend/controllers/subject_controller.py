"""
Subject Controller

API endpoints for Subject CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from services.subject_service import SubjectService
from schemas.subject_schema import (
    SubjectCreateSchema,
    SubjectUpdateSchema,
    SubjectResponseSchema,
    SubjectListResponseSchema,
    SubjectStatusSchema,
    SubjectStatisticsSchema
)
from config.database import get_db
import uuid


router = APIRouter(prefix="/subjects", tags=["subjects"])


# Dependency to get SubjectService
async def get_subject_service(session: AsyncSession = Depends(get_db)) -> SubjectService:
    return SubjectService(session)


# 1. Create Subject
@router.post("", response_model=SubjectResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: SubjectCreateSchema,
    service: SubjectService = Depends(get_subject_service)
):
    """
    Create a new subject.

    **Required:**
    - school_id: School UUID
    - code: Subject code (uppercase, unique per school)
    - name: Subject name

    **Optional:**
    - description: Subject description
    - category: core, elective, enrichment, remedial, other (default: core)
    - subject_type: academic, arts, physical, technical, other
    - grade_levels: Array of grades 1-7 (default: all grades)
    - color: Hex color code (#RRGGBB)
    - icon: Icon/emoji
    - display_order: Sort order (default: 0)
    - credits: Credit hours
    - is_required: Required flag (default: true)
    - is_active: Active flag (default: true)

    **Permissions:** Administrator only
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()  # Placeholder

        subject = await service.create_subject(
            school_id=subject_data.school_id,
            code=subject_data.code,
            name=subject_data.name,
            description=subject_data.description,
            category=subject_data.category,
            subject_type=subject_data.subject_type,
            grade_levels=subject_data.grade_levels,
            color=subject_data.color,
            icon=subject_data.icon,
            display_order=subject_data.display_order,
            credits=subject_data.credits,
            is_required=subject_data.is_required,
            is_active=subject_data.is_active,
            created_by_id=current_user_id
        )

        # Load relationships for response
        subject_with_relations = await service.get_subject_by_id(subject.id)

        return SubjectResponseSchema(
            **subject_with_relations.to_dict(include_relationships=True)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subject: {str(e)}"
        )


# 2. List Subjects (Paginated with Filters)
@router.get("", response_model=SubjectListResponseSchema)
async def list_subjects(
    school_id: Optional[uuid.UUID] = Query(None, description="Filter by school"),
    category: Optional[str] = Query(None, description="Filter by category"),
    subject_type: Optional[str] = Query(None, description="Filter by type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_required: Optional[bool] = Query(None, description="Filter by required status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Results per page"),
    service: SubjectService = Depends(get_subject_service)
):
    """
    List subjects with pagination and filters.

    **Query Parameters:**
    - school_id: Filter by school (optional)
    - category: Filter by category (core, elective, etc.)
    - subject_type: Filter by type (academic, arts, etc.)
    - is_active: Filter by active status
    - is_required: Filter by required status
    - page: Page number (default: 1)
    - limit: Results per page (default: 50, max: 100)

    **Permissions:** Administrator, Teacher
    """
    try:
        # TODO: Get current user's school_id from auth if not provided
        if not school_id:
            school_id = uuid.UUID("60da2256-81fc-4ca5-bf6b-467b8d371c61")  # Placeholder

        subjects, total = await service.get_subjects_by_school(
            school_id, page, limit, category, subject_type, is_active, is_required
        )

        return SubjectListResponseSchema(
            subjects=[SubjectResponseSchema(**s.to_dict()) for s in subjects],
            total=total,
            page=page,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list subjects: {str(e)}"
        )


# 3. Get Subject by ID
@router.get("/{subject_id}", response_model=SubjectResponseSchema)
async def get_subject(
    subject_id: uuid.UUID,
    service: SubjectService = Depends(get_subject_service)
):
    """
    Get a specific subject by ID.

    **Permissions:** Administrator, Teacher, Student, Parent
    """
    try:
        subject = await service.get_subject_by_id(subject_id)

        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )

        return SubjectResponseSchema(
            **subject.to_dict(include_relationships=True)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subject: {str(e)}"
        )


# 4. Get Subject by Code
@router.get("/code/{code}", response_model=SubjectResponseSchema)
async def get_subject_by_code(
    code: str,
    school_id: Optional[uuid.UUID] = Query(None, description="School UUID"),
    service: SubjectService = Depends(get_subject_service)
):
    """
    Get subject by code within a school.

    **Permissions:** Administrator, Teacher
    """
    try:
        # TODO: Get current user's school_id from auth if not provided
        if not school_id:
            school_id = uuid.UUID("60da2256-81fc-4ca5-bf6b-467b8d371c61")  # Placeholder

        subject = await service.get_subject_by_code(school_id, code)

        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with code '{code}' not found"
            )

        return SubjectResponseSchema(**subject.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subject: {str(e)}"
        )


# 5. Update Subject
@router.put("/{subject_id}", response_model=SubjectResponseSchema)
async def update_subject(
    subject_id: uuid.UUID,
    subject_data: SubjectUpdateSchema,
    service: SubjectService = Depends(get_subject_service)
):
    """
    Update subject information.

    All fields are optional. Only provided fields will be updated.

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()  # Placeholder

        subject = await service.update_subject(
            subject_id=subject_id,
            updated_by_id=current_user_id,
            name=subject_data.name,
            description=subject_data.description,
            category=subject_data.category,
            subject_type=subject_data.subject_type,
            grade_levels=subject_data.grade_levels,
            color=subject_data.color,
            icon=subject_data.icon,
            display_order=subject_data.display_order,
            credits=subject_data.credits,
            is_required=subject_data.is_required,
            is_active=subject_data.is_active
        )

        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )

        # Reload with relationships
        subject_with_relations = await service.get_subject_by_id(subject.id)

        return SubjectResponseSchema(
            **subject_with_relations.to_dict(include_relationships=True)
        )

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
            detail=f"Failed to update subject: {str(e)}"
        )


# 6. Delete Subject
@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: uuid.UUID,
    service: SubjectService = Depends(get_subject_service)
):
    """
    Soft delete a subject.

    **Note:** Cannot delete subjects with active classes, assessments, or lessons.

    **Permissions:** Administrator only
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()  # Placeholder

        success = await service.delete_subject(subject_id, current_user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )

        return None

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
            detail=f"Failed to delete subject: {str(e)}"
        )


# 7. Toggle Subject Status
@router.patch("/{subject_id}/status", response_model=SubjectResponseSchema)
async def toggle_subject_status(
    subject_id: uuid.UUID,
    service: SubjectService = Depends(get_subject_service)
):
    """
    Toggle active status of a subject.

    **Permissions:** Administrator only
    """
    try:
        subject = await service.toggle_status(subject_id)

        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )

        return SubjectResponseSchema(**subject.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle status: {str(e)}"
        )


# 8. Get Subjects by Category
@router.get("/category/{category}", response_model=list[SubjectResponseSchema])
async def get_subjects_by_category(
    category: str,
    school_id: Optional[uuid.UUID] = Query(None, description="School UUID"),
    service: SubjectService = Depends(get_subject_service)
):
    """
    Get all subjects in a specific category.

    **Categories:** core, elective, enrichment, remedial, other

    **Permissions:** Administrator, Teacher
    """
    try:
        # TODO: Get current user's school_id from auth if not provided
        if not school_id:
            school_id = uuid.UUID("60da2256-81fc-4ca5-bf6b-467b8d371c61")  # Placeholder

        subjects = await service.get_subjects_by_category(school_id, category)

        return [SubjectResponseSchema(**s.to_dict()) for s in subjects]

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subjects by category: {str(e)}"
        )


# 9. Get Subjects by Grade Level
@router.get("/grade/{grade}", response_model=list[SubjectResponseSchema])
async def get_subjects_by_grade(
    grade: int,
    school_id: Optional[uuid.UUID] = Query(None, description="School UUID"),
    service: SubjectService = Depends(get_subject_service)
):
    """
    Get all subjects taught at a specific grade level.

    **Grade Range:** 1-7

    **Permissions:** Administrator, Teacher
    """
    try:
        # TODO: Get current user's school_id from auth if not provided
        if not school_id:
            school_id = uuid.UUID("60da2256-81fc-4ca5-bf6b-467b8d371c61")  # Placeholder

        subjects = await service.get_subjects_by_grade(school_id, grade)

        return [SubjectResponseSchema(**s.to_dict()) for s in subjects]

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subjects by grade: {str(e)}"
        )


# 10. Search Subjects
@router.get("/search/query", response_model=SubjectListResponseSchema)
async def search_subjects(
    q: str = Query(..., min_length=2, description="Search query"),
    school_id: Optional[uuid.UUID] = Query(None, description="School UUID"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    service: SubjectService = Depends(get_subject_service)
):
    """
    Search subjects by code, name, or description.

    **Query Parameters:**
    - q: Search query (min 2 characters)
    - school_id: School UUID
    - page, limit: Pagination

    **Permissions:** Administrator, Teacher
    """
    try:
        # TODO: Get current user's school_id from auth if not provided
        if not school_id:
            school_id = uuid.UUID("60da2256-81fc-4ca5-bf6b-467b8d371c61")  # Placeholder

        subjects, total = await service.search_subjects(school_id, q, page, limit)

        return SubjectListResponseSchema(
            subjects=[SubjectResponseSchema(**s.to_dict()) for s in subjects],
            total=total,
            page=page,
            limit=limit
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search subjects: {str(e)}"
        )


# 11. Get Subject Statistics
@router.get("/statistics/summary", response_model=SubjectStatisticsSchema)
async def get_subject_statistics(
    school_id: Optional[uuid.UUID] = Query(None, description="School UUID"),
    service: SubjectService = Depends(get_subject_service)
):
    """
    Get subject statistics for a school.

    Returns counts for:
    - Total subjects
    - Active/inactive subjects
    - By category
    - By type
    - Required/elective subjects

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current user's school_id from auth if not provided
        if not school_id:
            school_id = uuid.UUID("60da2256-81fc-4ca5-bf6b-467b8d371c61")  # Placeholder

        stats = await service.get_statistics(school_id)

        return SubjectStatisticsSchema(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
