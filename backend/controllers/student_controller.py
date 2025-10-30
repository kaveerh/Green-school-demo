"""
Student Controller
API endpoints for student operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from config.database import get_db
from services.student_service import StudentService
from schemas.student_schema import (
    StudentCreateSchema,
    StudentUpdateSchema,
    StudentResponseSchema,
    StudentListResponseSchema,
    StudentSearchSchema,
    StudentStatusChangeSchema,
    StudentStatisticsSchema,
    ParentStudentLinkSchema,
    ParentStudentRelationshipResponseSchema,
    ParentStudentRelationshipListSchema,
    StudentStatusEnum,
    GenderEnum,
)
from utils.auth import CurrentUser, require_admin

router = APIRouter(prefix="/students", tags=["Students"])


def _student_to_response(student) -> StudentResponseSchema:
    """Convert Student model to response schema with user data"""
    student_dict = student.to_dict(include_sensitive=True)  # Include all fields

    # Add user relationship data if loaded
    if hasattr(student, 'user') and student.user:
        student_dict['user'] = {
            'id': str(student.user.id),
            'email': student.user.email,
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'full_name': f"{student.user.first_name} {student.user.last_name}",
            'persona': student.user.persona,
            'status': student.user.status,
            'phone': student.user.phone,
            'avatar_url': student.user.avatar_url
        }

    return StudentResponseSchema(**student_dict)


@router.post(
    "",
    response_model=StudentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Create a student profile. Only administrators can create students."
)
async def create_student(
    student_data: StudentCreateSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new student profile

    - **user_id**: User UUID (must have student persona)
    - **student_id**: Unique student identifier within school
    - **grade_level**: Grade level (1-7)
    - **date_of_birth**: Student's date of birth
    - **enrollment_date**: Date of enrollment
    """
    service = StudentService(db)

    try:
        student = await service.create_student(student_data, current_user.id)
        return student
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=StudentListResponseSchema,
    summary="List students",
    description="Search and list students with filters and pagination."
)
async def list_students(
    search: Optional[str] = Query(None, description="Search in student_id or name"),
    grade_level: Optional[int] = Query(None, ge=1, le=7, description="Filter by grade level"),
    status_filter: Optional[StudentStatusEnum] = Query(None, alias="status", description="Filter by status"),
    gender: Optional[GenderEnum] = Query(None, description="Filter by gender"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: str = Query("created_at", description="Sort field"),
    order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List students with filtering and pagination

    Returns a paginated list of students with metadata
    """
    service = StudentService(db)

    search_params = StudentSearchSchema(
        search=search,
        grade_level=grade_level,
        status=status_filter,
        gender=gender,
        page=page,
        limit=limit,
        sort=sort,
        order=order
    )

    students, pagination = await service.search_students(
        school_id=current_user.school_id,
        search_params=search_params
    )

    # Convert students to response schemas with user data
    student_responses = [_student_to_response(student) for student in students]

    return {
        "data": student_responses,
        "pagination": pagination
    }


@router.get(
    "/enrolled",
    response_model=StudentListResponseSchema,
    summary="List enrolled students",
    description="Get all currently enrolled students"
)
async def list_enrolled_students(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all currently enrolled students in the school
    """
    service = StudentService(db)
    students, pagination = await service.get_enrolled_students(
        school_id=current_user.school_id,
        page=page,
        limit=limit
    )

    return {
        "data": students,
        "pagination": pagination
    }


@router.get(
    "/grade/{grade}",
    response_model=StudentListResponseSchema,
    summary="List students by grade",
    description="Get all students in a specific grade level"
)
async def list_students_by_grade(
    grade: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get students by grade level

    - **grade**: Grade level (1-7)
    """
    service = StudentService(db)

    try:
        students, pagination = await service.get_students_by_grade(
            school_id=current_user.school_id,
            grade_level=grade,
            page=page,
            limit=limit
        )
        return {
            "data": students,
            "pagination": pagination
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/user/{user_id}",
    response_model=StudentResponseSchema,
    summary="Get student by user ID",
    description="Get a student profile by user ID"
)
async def get_student_by_user_id(
    user_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get student by user ID

    - **user_id**: User UUID
    """
    service = StudentService(db)
    student = await service.get_student_by_user_id(user_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for this user"
        )

    return student


@router.get(
    "/student-id/{student_id}",
    response_model=StudentResponseSchema,
    summary="Get student by student ID",
    description="Get a student by their student ID"
)
async def get_student_by_student_id(
    student_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get student by student ID

    - **student_id**: Student identifier
    """
    service = StudentService(db)
    student = await service.get_student_by_student_id(
        school_id=current_user.school_id,
        student_id=student_id
    )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student


@router.get(
    "/{student_id}",
    response_model=StudentResponseSchema,
    summary="Get a student",
    description="Get a student by ID."
)
async def get_student(
    student_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get student by ID

    - **student_id**: Student UUID
    """
    service = StudentService(db)
    student = await service.get_student(student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student


@router.put(
    "/{student_id}",
    response_model=StudentResponseSchema,
    summary="Update a student",
    description="Update a student profile. Only administrators can update students."
)
async def update_student(
    student_id: uuid.UUID,
    student_data: StudentUpdateSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update student profile

    - **student_id**: Student UUID
    - All fields are optional
    """
    service = StudentService(db)

    try:
        student = await service.update_student(
            student_id=student_id,
            student_data=student_data,
            updated_by_id=current_user.id
        )

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        return student
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student",
    description="Soft delete a student profile. Only administrators can delete students."
)
async def delete_student(
    student_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete student (soft delete)

    - **student_id**: Student UUID
    """
    service = StudentService(db)
    success = await service.delete_student(student_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return None


@router.patch(
    "/{student_id}/status",
    response_model=StudentResponseSchema,
    summary="Change student status",
    description="Change student status. Only administrators can change status."
)
async def change_student_status(
    student_id: uuid.UUID,
    status_data: StudentStatusChangeSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Change student status

    - **student_id**: Student UUID
    - **status**: New status (enrolled, graduated, transferred, withdrawn, suspended)
    """
    service = StudentService(db)
    student = await service.change_student_status(
        student_id=student_id,
        new_status=status_data.status.value,
        updated_by_id=current_user.id
    )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student


@router.post(
    "/{student_id}/promote",
    response_model=StudentResponseSchema,
    summary="Promote student to next grade",
    description="Promote a student to the next grade level. Only administrators can promote students."
)
async def promote_student(
    student_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Promote student to next grade level

    - **student_id**: Student UUID

    Student must be currently enrolled and in grades 1-6 to be promoted.
    """
    service = StudentService(db)

    try:
        student = await service.promote_student(
            student_id=student_id,
            updated_by_id=current_user.id
        )

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        return student
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{student_id}/link-parent",
    response_model=ParentStudentRelationshipResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Link parent to student",
    description="Create a parent-student relationship. Only administrators can link parents."
)
async def link_parent(
    student_id: uuid.UUID,
    link_data: ParentStudentLinkSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Link a parent to a student

    - **student_id**: Student UUID (must match link_data.student_id)
    - **parent_id**: Parent user UUID
    - **relationship_type**: Type of relationship (mother, father, guardian, etc.)
    - **is_primary_contact**: Whether this is the primary contact
    - **has_pickup_permission**: Whether parent can pick up student
    """
    if link_data.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student ID in path must match student_id in request body"
        )

    service = StudentService(db)

    try:
        relationship = await service.link_parent(link_data, current_user.id)
        return relationship
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{student_id}/unlink-parent/{parent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink parent from student",
    description="Remove a parent-student relationship. Only administrators can unlink parents."
)
async def unlink_parent(
    student_id: uuid.UUID,
    parent_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Unlink a parent from a student

    - **student_id**: Student UUID
    - **parent_id**: Parent user UUID
    """
    service = StudentService(db)
    success = await service.unlink_parent(parent_id, student_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent-student relationship not found"
        )

    return None


@router.get(
    "/{student_id}/parents",
    response_model=ParentStudentRelationshipListSchema,
    summary="Get student's parents",
    description="Get all parent relationships for a student"
)
async def get_student_parents(
    student_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all parents for a student

    - **student_id**: Student UUID
    """
    service = StudentService(db)
    relationships = await service.get_student_parents(student_id)

    return {
        "data": relationships
    }


@router.get(
    "/statistics/summary",
    response_model=StudentStatisticsSchema,
    summary="Get student statistics",
    description="Get student statistics for the school. Only administrators can view statistics."
)
async def get_student_statistics(
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get student statistics

    Returns counts by status, grade level, and gender
    """
    service = StudentService(db)
    stats = await service.get_statistics(current_user.school_id)
    return stats
