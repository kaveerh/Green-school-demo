"""
Teacher Controller
API endpoints for teacher operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from config.database import get_db
from services.teacher_service import TeacherService
from schemas.teacher_schema import (
    TeacherCreateSchema,
    TeacherUpdateSchema,
    TeacherResponseSchema,
    TeacherListResponseSchema,
    TeacherSearchSchema,
    TeacherStatusChangeSchema,
    TeacherStatisticsSchema,
    TeacherGradeAssignmentSchema,
    TeacherSpecializationSchema,
    TeacherStatusEnum,
    EmploymentTypeEnum,
)
from utils.auth import CurrentUser, require_admin

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.post(
    "",
    response_model=TeacherResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new teacher profile",
    description="Create a teacher profile for an existing user with teacher persona. Only administrators can create teacher profiles."
)
async def create_teacher(
    teacher_data: TeacherCreateSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new teacher profile

    - **user_id**: User UUID (must have teacher persona)
    - **employee_id**: Unique employee identifier
    - **hire_date**: Date of hire
    - **department**: Department name
    - **job_title**: Job title (default: Teacher)
    - **grade_levels**: Array of grade levels (1-7)
    - **specializations**: Array of subject specializations
    - **employment_type**: full-time, part-time, contract, substitute
    - **certification_number**: Teaching certification number
    - **certification_expiry**: Certification expiry date
    - **education_level**: Highest education level
    - **university**: University attended
    """
    service = TeacherService(db)

    try:
        teacher = await service.create_teacher(teacher_data, current_user.id)
        return teacher
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=TeacherListResponseSchema,
    summary="List teachers",
    description="Search and list teachers with filters and pagination. Only administrators can list all teachers."
)
async def list_teachers(
    search: Optional[str] = Query(None, description="Search in employee_id, department, or job_title"),
    status_filter: Optional[TeacherStatusEnum] = Query(None, alias="status", description="Filter by status"),
    department: Optional[str] = Query(None, description="Filter by department"),
    employment_type: Optional[EmploymentTypeEnum] = Query(None, description="Filter by employment type"),
    grade: Optional[int] = Query(None, ge=1, le=7, description="Filter by grade level"),
    specialization: Optional[str] = Query(None, description="Filter by specialization"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: str = Query("created_at", description="Sort field"),
    order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List teachers with filtering and pagination

    Returns a paginated list of teachers with metadata
    """
    service = TeacherService(db)

    search_params = TeacherSearchSchema(
        search=search,
        status=status_filter,
        department=department,
        employment_type=employment_type,
        grade=grade,
        specialization=specialization,
        page=page,
        limit=limit,
        sort=sort,
        order=order
    )

    teachers, pagination = await service.search_teachers(
        school_id=current_user.school_id,
        search_params=search_params
    )

    return {
        "data": teachers,
        "pagination": pagination
    }


@router.get(
    "/user/{user_id}",
    response_model=TeacherResponseSchema,
    summary="Get teacher by user ID",
    description="Get a teacher profile by user ID"
)
async def get_teacher_by_user_id(
    user_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get teacher by user ID

    - **user_id**: User UUID
    """
    service = TeacherService(db)
    teacher = await service.get_teacher_by_user_id(user_id)

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found for this user"
        )

    return teacher


@router.get(
    "/employee/{employee_id}",
    response_model=TeacherResponseSchema,
    summary="Get teacher by employee ID",
    description="Get a teacher by their employee ID"
)
async def get_teacher_by_employee_id(
    employee_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get teacher by employee ID

    - **employee_id**: Employee identifier
    """
    service = TeacherService(db)
    teacher = await service.get_teacher_by_employee_id(
        school_id=current_user.school_id,
        employee_id=employee_id
    )

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    return teacher


@router.get(
    "/active",
    response_model=TeacherListResponseSchema,
    summary="List active teachers",
    description="Get all currently active teachers"
)
async def list_active_teachers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all active teachers in the school
    """
    service = TeacherService(db)
    teachers, pagination = await service.get_active_teachers(
        school_id=current_user.school_id,
        page=page,
        limit=limit
    )

    return {
        "data": teachers,
        "pagination": pagination
    }


@router.get(
    "/grade/{grade}",
    response_model=list[TeacherResponseSchema],
    summary="List teachers by grade",
    description="Get all teachers who teach a specific grade level"
)
async def list_teachers_by_grade(
    grade: int,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get teachers by grade level

    - **grade**: Grade level (1-7)
    """
    service = TeacherService(db)

    try:
        teachers = await service.get_teachers_by_grade(
            school_id=current_user.school_id,
            grade=grade
        )
        return teachers
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/specialization/{specialization}",
    response_model=list[TeacherResponseSchema],
    summary="List teachers by specialization",
    description="Get all teachers with a specific subject specialization"
)
async def list_teachers_by_specialization(
    specialization: str,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get teachers by specialization

    - **specialization**: Subject specialization (e.g., MATH, ELA)
    """
    service = TeacherService(db)
    teachers = await service.get_teachers_by_specialization(
        school_id=current_user.school_id,
        specialization=specialization
    )
    return teachers


@router.get(
    "/{teacher_id}",
    response_model=TeacherResponseSchema,
    summary="Get a teacher",
    description="Get a teacher by ID. Administrators can view any teacher."
)
async def get_teacher(
    teacher_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get teacher by ID

    - **teacher_id**: Teacher UUID
    """
    service = TeacherService(db)
    teacher = await service.get_teacher(teacher_id)

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    return teacher


@router.put(
    "/{teacher_id}",
    response_model=TeacherResponseSchema,
    summary="Update a teacher",
    description="Update a teacher profile. Only administrators can update teachers."
)
async def update_teacher(
    teacher_id: uuid.UUID,
    teacher_data: TeacherUpdateSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update teacher profile

    - **teacher_id**: Teacher UUID
    - All fields are optional
    """
    service = TeacherService(db)

    try:
        teacher = await service.update_teacher(
            teacher_id=teacher_id,
            teacher_data=teacher_data,
            updated_by_id=current_user.id
        )

        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )

        return teacher
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{teacher_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a teacher",
    description="Soft delete a teacher profile. Only administrators can delete teachers."
)
async def delete_teacher(
    teacher_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete teacher (soft delete)

    - **teacher_id**: Teacher UUID
    """
    service = TeacherService(db)
    success = await service.delete_teacher(teacher_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    return None


@router.patch(
    "/{teacher_id}/status",
    response_model=TeacherResponseSchema,
    summary="Change teacher status",
    description="Change teacher status. Only administrators can change status."
)
async def change_teacher_status(
    teacher_id: uuid.UUID,
    status_data: TeacherStatusChangeSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Change teacher status

    - **teacher_id**: Teacher UUID
    - **status**: New status (active, inactive, on_leave, terminated)
    """
    service = TeacherService(db)
    teacher = await service.change_teacher_status(
        teacher_id=teacher_id,
        new_status=status_data.status.value,
        updated_by_id=current_user.id
    )

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    return teacher


@router.patch(
    "/{teacher_id}/grades",
    response_model=TeacherResponseSchema,
    summary="Assign grade levels to teacher",
    description="Assign or update grade levels that a teacher teaches. Only administrators can assign grades."
)
async def assign_grades(
    teacher_id: uuid.UUID,
    grades_data: TeacherGradeAssignmentSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign grade levels to teacher

    - **teacher_id**: Teacher UUID
    - **grade_levels**: Array of grades (1-7)
    """
    service = TeacherService(db)

    try:
        teacher = await service.assign_grades(
            teacher_id=teacher_id,
            grade_levels=grades_data.grade_levels,
            updated_by_id=current_user.id
        )

        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )

        return teacher
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{teacher_id}/specializations",
    response_model=TeacherResponseSchema,
    summary="Assign specializations to teacher",
    description="Assign or update subject specializations. Only administrators can assign specializations."
)
async def assign_specializations(
    teacher_id: uuid.UUID,
    specializations_data: TeacherSpecializationSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign specializations to teacher

    - **teacher_id**: Teacher UUID
    - **specializations**: Array of subject codes (e.g., ["MATH", "SCIENCE"])
    """
    service = TeacherService(db)
    teacher = await service.assign_specializations(
        teacher_id=teacher_id,
        specializations=specializations_data.specializations,
        updated_by_id=current_user.id
    )

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    return teacher


@router.get(
    "/statistics/summary",
    response_model=TeacherStatisticsSchema,
    summary="Get teacher statistics",
    description="Get teacher statistics for the school. Only administrators can view statistics."
)
async def get_teacher_statistics(
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get teacher statistics

    Returns counts by status, employment type, and department
    """
    service = TeacherService(db)
    stats = await service.get_statistics(current_user.school_id)
    return stats
