"""
Lesson Controller

API endpoints for lesson planning and curriculum management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import Optional, List
from datetime import date
from uuid import UUID
import math

from schemas.lesson_schema import (
    LessonCreateRequest,
    LessonUpdateRequest,
    LessonStatusUpdateRequest,
    LessonCompleteRequest,
    LessonFromTemplateRequest,
    LessonDuplicateRequest,
    LessonResponse,
    LessonListResponse,
    LessonStatisticsResponse,
    LessonQueryParams,
    LessonSearchParams,
    LessonDateRangeParams,
    LessonUpcomingParams,
    LessonTemplateParams,
    LessonStatisticsParams
)
from services.lesson_service import LessonService
from repositories.lesson_repository import LessonRepository
from repositories.teacher_repository import TeacherRepository
from repositories.class_repository import ClassRepository
from repositories.subject_repository import SubjectRepository
from config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/api/v1/lessons", tags=["lessons"])


# Dependency injection
async def get_lesson_service(db: AsyncSession = Depends(get_db)) -> LessonService:
    """Get lesson service with dependencies"""
    lesson_repo = LessonRepository(db)
    teacher_repo = TeacherRepository(db)
    class_repo = ClassRepository(db)
    subject_repo = SubjectRepository(db)
    return LessonService(lesson_repo, teacher_repo, class_repo, subject_repo)


@router.post(
    "",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create lesson",
    description="Create a new lesson with full lesson plan"
)
async def create_lesson(
    request: LessonCreateRequest,
    school_id: UUID = Query(..., description="School UUID"),
    service: LessonService = Depends(get_lesson_service)
):
    """Create a new lesson"""
    try:
        lesson = await service.create_lesson(
            school_id=school_id,
            class_id=request.class_id,
            teacher_id=request.teacher_id,
            subject_id=request.subject_id,
            title=request.title,
            scheduled_date=request.scheduled_date,
            duration_minutes=request.duration_minutes,
            lesson_number=request.lesson_number,
            description=request.description,
            learning_objectives=request.learning_objectives,
            materials_needed=request.materials_needed,
            curriculum_standards=request.curriculum_standards,
            introduction=request.introduction,
            main_activity=request.main_activity,
            assessment=request.assessment,
            homework=request.homework,
            notes=request.notes,
            links=request.links,
            color=request.color,
            is_template=request.is_template,
            template_id=request.template_id
        )
        return LessonResponse(**lesson.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create lesson: {str(e)}"
        )


@router.post(
    "/from-template",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create lesson from template",
    description="Create a new lesson using an existing template"
)
async def create_lesson_from_template(
    request: LessonFromTemplateRequest,
    school_id: UUID = Query(..., description="School UUID"),
    service: LessonService = Depends(get_lesson_service)
):
    """Create lesson from template"""
    try:
        overrides = {}
        if request.title:
            overrides['title'] = request.title
        if request.color:
            overrides['color'] = request.color

        lesson = await service.create_from_template(
            template_id=request.template_id,
            class_id=request.class_id,
            scheduled_date=request.scheduled_date,
            lesson_number=request.lesson_number,
            overrides=overrides if overrides else None
        )
        return LessonResponse(**lesson.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create lesson from template: {str(e)}"
        )


@router.get(
    "",
    response_model=LessonListResponse,
    summary="List lessons",
    description="Get lessons with pagination and filters"
)
async def list_lessons(
    school_id: UUID = Query(..., description="School UUID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    class_id: Optional[UUID] = Query(None, description="Filter by class"),
    teacher_id: Optional[UUID] = Query(None, description="Filter by teacher"),
    subject_id: Optional[UUID] = Query(None, description="Filter by subject"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    is_template: Optional[bool] = Query(None, description="Filter templates"),
    service: LessonService = Depends(get_lesson_service)
):
    """List lessons with filters"""
    try:
        lessons, total = await service.get_lessons(
            school_id=school_id,
            page=page,
            limit=limit,
            class_id=class_id,
            teacher_id=teacher_id,
            subject_id=subject_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            is_template=is_template
        )

        return LessonListResponse(
            lessons=[LessonResponse(**lesson.to_dict()) for lesson in lessons],
            total=total,
            page=page,
            limit=limit,
            pages=math.ceil(total / limit) if total > 0 else 0
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list lessons: {str(e)}"
        )


@router.get(
    "/by-date-range",
    response_model=List[LessonResponse],
    summary="Get lessons by date range",
    description="Get lessons within a date range (for calendar view)"
)
async def get_lessons_by_date_range(
    school_id: UUID = Query(..., description="School UUID"),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    teacher_id: Optional[UUID] = Query(None, description="Filter by teacher"),
    class_id: Optional[UUID] = Query(None, description="Filter by class"),
    subject_id: Optional[UUID] = Query(None, description="Filter by subject"),
    service: LessonService = Depends(get_lesson_service)
):
    """Get lessons by date range"""
    try:
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_date must be after start_date"
            )

        lessons = await service.get_lessons_by_date_range(
            school_id=school_id,
            start_date=start_date,
            end_date=end_date,
            teacher_id=teacher_id,
            class_id=class_id,
            subject_id=subject_id
        )

        return [LessonResponse(**lesson.to_dict()) for lesson in lessons]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get lessons by date range: {str(e)}"
        )


@router.get(
    "/upcoming",
    response_model=List[LessonResponse],
    summary="Get upcoming lessons",
    description="Get lessons scheduled within the next N days"
)
async def get_upcoming_lessons(
    school_id: UUID = Query(..., description="School UUID"),
    teacher_id: Optional[UUID] = Query(None, description="Filter by teacher"),
    days: int = Query(7, ge=1, le=90, description="Number of days ahead"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    service: LessonService = Depends(get_lesson_service)
):
    """Get upcoming lessons"""
    try:
        lessons = await service.get_upcoming_lessons(
            school_id=school_id,
            teacher_id=teacher_id,
            days=days,
            limit=limit
        )

        return [LessonResponse(**lesson.to_dict()) for lesson in lessons]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upcoming lessons: {str(e)}"
        )


@router.get(
    "/past-due",
    response_model=List[LessonResponse],
    summary="Get past due lessons",
    description="Get lessons that are past their scheduled date but not completed"
)
async def get_past_due_lessons(
    school_id: UUID = Query(..., description="School UUID"),
    teacher_id: Optional[UUID] = Query(None, description="Filter by teacher"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    service: LessonService = Depends(get_lesson_service)
):
    """Get past due lessons"""
    try:
        lessons = await service.get_past_due_lessons(
            school_id=school_id,
            teacher_id=teacher_id,
            limit=limit
        )

        return [LessonResponse(**lesson.to_dict()) for lesson in lessons]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get past due lessons: {str(e)}"
        )


@router.get(
    "/search",
    response_model=List[LessonResponse],
    summary="Search lessons",
    description="Search lessons by title, description, or content"
)
async def search_lessons(
    school_id: UUID = Query(..., description="School UUID"),
    query: str = Query(..., min_length=1, description="Search query"),
    teacher_id: Optional[UUID] = Query(None, description="Filter by teacher"),
    subject_id: Optional[UUID] = Query(None, description="Filter by subject"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    service: LessonService = Depends(get_lesson_service)
):
    """Search lessons"""
    try:
        lessons = await service.search_lessons(
            school_id=school_id,
            query=query,
            teacher_id=teacher_id,
            subject_id=subject_id,
            limit=limit
        )

        return [LessonResponse(**lesson.to_dict()) for lesson in lessons]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search lessons: {str(e)}"
        )


@router.get(
    "/templates",
    response_model=List[LessonResponse],
    summary="Get lesson templates",
    description="Get all lesson templates for reuse"
)
async def get_templates(
    school_id: UUID = Query(..., description="School UUID"),
    teacher_id: Optional[UUID] = Query(None, description="Filter by teacher"),
    subject_id: Optional[UUID] = Query(None, description="Filter by subject"),
    service: LessonService = Depends(get_lesson_service)
):
    """Get lesson templates"""
    try:
        lessons = await service.get_templates(
            school_id=school_id,
            teacher_id=teacher_id,
            subject_id=subject_id
        )

        return [LessonResponse(**lesson.to_dict()) for lesson in lessons]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=LessonStatisticsResponse,
    summary="Get lesson statistics",
    description="Get aggregated lesson statistics"
)
async def get_statistics(
    school_id: UUID = Query(..., description="School UUID"),
    teacher_id: Optional[UUID] = Query(None, description="Filter by teacher"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    service: LessonService = Depends(get_lesson_service)
):
    """Get lesson statistics"""
    try:
        if start_date and end_date and end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_date must be after start_date"
            )

        stats = await service.get_statistics(
            school_id=school_id,
            teacher_id=teacher_id,
            start_date=start_date,
            end_date=end_date
        )

        return LessonStatisticsResponse(**stats)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get(
    "/{lesson_id}",
    response_model=LessonResponse,
    summary="Get lesson by ID",
    description="Get a single lesson by UUID"
)
async def get_lesson(
    lesson_id: UUID = Path(..., description="Lesson UUID"),
    service: LessonService = Depends(get_lesson_service)
):
    """Get lesson by ID"""
    try:
        lesson = await service.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson {lesson_id} not found"
            )

        return LessonResponse(**lesson.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get lesson: {str(e)}"
        )


@router.put(
    "/{lesson_id}",
    response_model=LessonResponse,
    summary="Update lesson",
    description="Update lesson details"
)
async def update_lesson(
    lesson_id: UUID = Path(..., description="Lesson UUID"),
    request: LessonUpdateRequest = None,
    service: LessonService = Depends(get_lesson_service)
):
    """Update lesson"""
    try:
        # Convert request to dict, excluding None values
        updates = request.model_dump(exclude_none=True)

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        lesson = await service.update_lesson(lesson_id, updates)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson {lesson_id} not found"
            )

        return LessonResponse(**lesson.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update lesson: {str(e)}"
        )


@router.patch(
    "/{lesson_id}/status",
    response_model=LessonResponse,
    summary="Update lesson status",
    description="Update lesson status (draft, scheduled, in_progress, completed, cancelled)"
)
async def update_status(
    lesson_id: UUID = Path(..., description="Lesson UUID"),
    request: LessonStatusUpdateRequest = None,
    service: LessonService = Depends(get_lesson_service)
):
    """Update lesson status"""
    try:
        lesson = await service.update_lesson(lesson_id, {"status": request.status})
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson {lesson_id} not found"
            )

        return LessonResponse(**lesson.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update status: {str(e)}"
        )


@router.post(
    "/{lesson_id}/start",
    response_model=LessonResponse,
    summary="Start lesson",
    description="Start a lesson (set status to in_progress)"
)
async def start_lesson(
    lesson_id: UUID = Path(..., description="Lesson UUID"),
    service: LessonService = Depends(get_lesson_service)
):
    """Start lesson"""
    try:
        lesson = await service.start_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson {lesson_id} not found"
            )

        return LessonResponse(**lesson.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start lesson: {str(e)}"
        )


@router.post(
    "/{lesson_id}/complete",
    response_model=LessonResponse,
    summary="Complete lesson",
    description="Complete a lesson with reflection"
)
async def complete_lesson(
    lesson_id: UUID = Path(..., description="Lesson UUID"),
    request: LessonCompleteRequest = None,
    service: LessonService = Depends(get_lesson_service)
):
    """Complete lesson"""
    try:
        lesson = await service.complete_lesson(
            lesson_id=lesson_id,
            completion_percentage=request.completion_percentage,
            actual_duration_minutes=request.actual_duration_minutes,
            reflection=request.reflection,
            what_went_well=request.what_went_well,
            what_to_improve=request.what_to_improve,
            modifications_needed=request.modifications_needed
        )
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson {lesson_id} not found"
            )

        return LessonResponse(**lesson.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete lesson: {str(e)}"
        )


@router.post(
    "/{lesson_id}/cancel",
    response_model=LessonResponse,
    summary="Cancel lesson",
    description="Cancel a lesson"
)
async def cancel_lesson(
    lesson_id: UUID = Path(..., description="Lesson UUID"),
    service: LessonService = Depends(get_lesson_service)
):
    """Cancel lesson"""
    try:
        lesson = await service.cancel_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson {lesson_id} not found"
            )

        return LessonResponse(**lesson.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel lesson: {str(e)}"
        )


@router.post(
    "/{lesson_id}/convert-to-template",
    response_model=LessonResponse,
    summary="Convert to template",
    description="Convert a lesson to a reusable template"
)
async def convert_to_template(
    lesson_id: UUID = Path(..., description="Lesson UUID"),
    service: LessonService = Depends(get_lesson_service)
):
    """Convert lesson to template"""
    try:
        lesson = await service.convert_to_template(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson {lesson_id} not found"
            )

        return LessonResponse(**lesson.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to convert to template: {str(e)}"
        )


@router.post(
    "/{lesson_id}/duplicate",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate lesson",
    description="Duplicate a lesson to a new date/class"
)
async def duplicate_lesson(
    lesson_id: UUID = Path(..., description="Lesson UUID"),
    request: LessonDuplicateRequest = None,
    service: LessonService = Depends(get_lesson_service)
):
    """Duplicate lesson"""
    try:
        lesson = await service.duplicate_lesson(
            lesson_id=lesson_id,
            new_scheduled_date=request.new_scheduled_date,
            new_class_id=request.new_class_id,
            new_lesson_number=request.new_lesson_number
        )
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson {lesson_id} not found"
            )

        return LessonResponse(**lesson.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to duplicate lesson: {str(e)}"
        )


@router.delete(
    "/{lesson_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete lesson",
    description="Soft delete a lesson"
)
async def delete_lesson(
    lesson_id: UUID = Path(..., description="Lesson UUID"),
    service: LessonService = Depends(get_lesson_service)
):
    """Delete lesson"""
    try:
        success = await service.delete_lesson(lesson_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson {lesson_id} not found"
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete lesson: {str(e)}"
        )
