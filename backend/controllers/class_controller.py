"""
Class Controller

API endpoints for Class and StudentClass management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid
import math

from config.database import get_db
from services.class_service import ClassService, StudentClassService
from schemas.class_schema import (
    ClassCreateSchema,
    ClassUpdateSchema,
    ClassResponseSchema,
    ClassListResponseSchema,
    ClassStatisticsSchema,
    ClassFilterParams,
    ClassSearchParams,
    StudentClassEnrollSchema,
    StudentClassUpdateGradesSchema,
    StudentClassCompleteSchema,
    StudentClassResponseSchema,
    StudentClassListResponseSchema
)

router = APIRouter()


# ============================================================================
# Class Endpoints
# ============================================================================

@router.post("/", response_model=ClassResponseSchema, status_code=201)
async def create_class(
    school_id: uuid.UUID,
    class_data: ClassCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new class

    Required fields:
    - code: Class code (format: SUBJECT-GRADE-QUARTER-SECTION)
    - name: Class name
    - subject_id: Subject UUID
    - teacher_id: Teacher UUID
    - grade_level: 1-7
    - quarter: Q1, Q2, Q3, or Q4
    - academic_year: YYYY-YYYY format
    - max_students: Maximum capacity
    """
    try:
        service = ClassService(db)

        class_obj = await service.create_class(
            school_id=school_id,
            code=class_data.code,
            name=class_data.name,
            subject_id=class_data.subject_id,
            teacher_id=class_data.teacher_id,
            grade_level=class_data.grade_level,
            quarter=class_data.quarter,
            academic_year=class_data.academic_year,
            max_students=class_data.max_students,
            room_id=class_data.room_id,
            description=class_data.description,
            schedule=class_data.schedule.dict() if class_data.schedule else None,
            color=class_data.color,
            display_order=class_data.display_order
        )

        return ClassResponseSchema(**class_obj.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=ClassListResponseSchema)
async def get_classes(
    school_id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    subject_id: Optional[uuid.UUID] = Query(None, description="Filter by subject"),
    teacher_id: Optional[uuid.UUID] = Query(None, description="Filter by teacher"),
    room_id: Optional[uuid.UUID] = Query(None, description="Filter by room"),
    grade_level: Optional[int] = Query(None, ge=1, le=7, description="Filter by grade"),
    quarter: Optional[str] = Query(None, regex=r'^Q[1-4]$', description="Filter by quarter"),
    academic_year: Optional[str] = Query(None, regex=r'^\d{4}-\d{4}$', description="Filter by year"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of classes with optional filters

    Filters:
    - subject_id: Filter by subject
    - teacher_id: Filter by teacher
    - room_id: Filter by room
    - grade_level: Filter by grade (1-7)
    - quarter: Filter by quarter (Q1-Q4)
    - academic_year: Filter by academic year (YYYY-YYYY)
    - is_active: Filter by active status
    """
    try:
        service = ClassService(db)

        classes, total = await service.get_classes_by_school(
            school_id=school_id,
            page=page,
            limit=limit,
            subject_id=subject_id,
            teacher_id=teacher_id,
            room_id=room_id,
            grade_level=grade_level,
            quarter=quarter,
            academic_year=academic_year,
            is_active=is_active
        )

        total_pages = math.ceil(total / limit)

        return ClassListResponseSchema(
            classes=[ClassResponseSchema(**c.to_dict()) for c in classes],
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/search", response_model=ClassListResponseSchema)
async def search_classes(
    school_id: uuid.UUID,
    query: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Search classes by code, name, or description

    Query matches against:
    - Class code
    - Class name
    - Class description
    """
    try:
        service = ClassService(db)

        classes, total = await service.search_classes(
            school_id=school_id,
            query=query,
            page=page,
            limit=limit
        )

        total_pages = math.ceil(total / limit)

        return ClassListResponseSchema(
            classes=[ClassResponseSchema(**c.to_dict()) for c in classes],
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/statistics", response_model=ClassStatisticsSchema)
async def get_statistics(
    school_id: Optional[uuid.UUID] = Query(None, description="Filter by school (optional)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get class statistics

    Returns:
    - Total classes count
    - Active/inactive counts
    - Distribution by grade level
    - Distribution by quarter
    - Distribution by subject
    - Enrollment statistics
    - Capacity utilization
    """
    try:
        service = ClassService(db)
        stats = await service.get_statistics(school_id)
        return ClassStatisticsSchema(**stats)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/teacher/{teacher_id}", response_model=List[ClassResponseSchema])
async def get_classes_by_teacher(
    school_id: uuid.UUID,
    teacher_id: uuid.UUID = Path(..., description="Teacher ID"),
    quarter: Optional[str] = Query(None, regex=r'^Q[1-4]$', description="Filter by quarter"),
    academic_year: Optional[str] = Query(None, regex=r'^\d{4}-\d{4}$', description="Filter by year"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all classes for a specific teacher

    Optional filters:
    - quarter: Q1, Q2, Q3, or Q4
    - academic_year: YYYY-YYYY format
    """
    try:
        service = ClassService(db)

        classes = await service.get_classes_by_teacher(
            school_id=school_id,
            teacher_id=teacher_id,
            quarter=quarter,
            academic_year=academic_year
        )

        return [ClassResponseSchema(**c.to_dict()) for c in classes]

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/subject/{subject_id}", response_model=List[ClassResponseSchema])
async def get_classes_by_subject(
    school_id: uuid.UUID,
    subject_id: uuid.UUID = Path(..., description="Subject ID"),
    grade_level: Optional[int] = Query(None, ge=1, le=7, description="Filter by grade"),
    quarter: Optional[str] = Query(None, regex=r'^Q[1-4]$', description="Filter by quarter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all classes for a specific subject

    Optional filters:
    - grade_level: 1-7
    - quarter: Q1, Q2, Q3, or Q4
    """
    try:
        service = ClassService(db)

        classes = await service.get_classes_by_subject(
            school_id=school_id,
            subject_id=subject_id,
            grade_level=grade_level,
            quarter=quarter
        )

        return [ClassResponseSchema(**c.to_dict()) for c in classes]

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/room/{room_id}", response_model=List[ClassResponseSchema])
async def get_classes_by_room(
    school_id: uuid.UUID,
    room_id: uuid.UUID = Path(..., description="Room ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get all classes for a specific room"""
    try:
        service = ClassService(db)

        classes = await service.get_classes_by_room(
            school_id=school_id,
            room_id=room_id
        )

        return [ClassResponseSchema(**c.to_dict()) for c in classes]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/code/{code}", response_model=ClassResponseSchema)
async def get_class_by_code(
    school_id: uuid.UUID,
    code: str = Path(..., description="Class code"),
    db: AsyncSession = Depends(get_db)
):
    """Get class by code within a school"""
    try:
        service = ClassService(db)

        class_obj = await service.get_class_by_code(school_id, code)

        if not class_obj:
            raise HTTPException(status_code=404, detail=f"Class with code '{code}' not found")

        return ClassResponseSchema(**class_obj.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{class_id}", response_model=ClassResponseSchema)
async def get_class(
    class_id: uuid.UUID = Path(..., description="Class ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get class by ID with all relationships"""
    try:
        service = ClassService(db)

        class_obj = await service.get_class_by_id(class_id)

        if not class_obj:
            raise HTTPException(status_code=404, detail=f"Class with ID {class_id} not found")

        return ClassResponseSchema(**class_obj.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{class_id}", response_model=ClassResponseSchema)
async def update_class(
    class_id: uuid.UUID,
    class_data: ClassUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Update class

    All fields are optional. Only provided fields will be updated.
    """
    try:
        service = ClassService(db)

        # Build update kwargs from provided fields
        update_data = class_data.dict(exclude_unset=True)

        # Convert schedule to dict if provided
        if 'schedule' in update_data and update_data['schedule']:
            update_data['schedule'] = update_data['schedule']

        class_obj = await service.update_class(class_id, **update_data)

        return ClassResponseSchema(**class_obj.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{class_id}", status_code=204)
async def delete_class(
    class_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete class

    This will set deleted_at timestamp. Associated student enrollments will cascade.
    """
    try:
        service = ClassService(db)
        await service.delete_class(class_id)
        return None

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/{class_id}/status", response_model=ClassResponseSchema)
async def toggle_class_status(
    class_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Toggle class active status (active ↔ inactive)"""
    try:
        service = ClassService(db)
        class_obj = await service.toggle_status(class_id)
        return ClassResponseSchema(**class_obj.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# Student Enrollment Endpoints
# ============================================================================

@router.post("/enrollments", response_model=StudentClassResponseSchema, status_code=201)
async def enroll_student(
    enrollment_data: StudentClassEnrollSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Enroll a student in a class

    Required:
    - student_id: Student UUID
    - class_id: Class UUID

    Optional:
    - enrollment_date: Defaults to today

    Validation:
    - Student and class must belong to same school
    - Student cannot already be enrolled
    - Class must not be full
    - Class must be active
    """
    try:
        service = StudentClassService(db)

        enrollment = await service.enroll_student(
            student_id=enrollment_data.student_id,
            class_id=enrollment_data.class_id,
            enrollment_date=enrollment_data.enrollment_date
        )

        return StudentClassResponseSchema(**enrollment.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/enrollments/{enrollment_id}", response_model=StudentClassResponseSchema)
async def get_enrollment(
    enrollment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get student enrollment by ID"""
    try:
        service = StudentClassService(db)

        enrollment = await service.get_enrollment_by_id(enrollment_id)

        if not enrollment:
            raise HTTPException(status_code=404, detail=f"Enrollment with ID {enrollment_id} not found")

        return StudentClassResponseSchema(**enrollment.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{class_id}/students", response_model=StudentClassListResponseSchema)
async def get_students_in_class(
    class_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all students enrolled in a class"""
    try:
        service = StudentClassService(db)

        enrollments = await service.get_students_in_class(class_id)

        return StudentClassListResponseSchema(
            enrollments=[StudentClassResponseSchema(**e.to_dict()) for e in enrollments],
            total=len(enrollments)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/students/{student_id}/classes", response_model=StudentClassListResponseSchema)
async def get_classes_for_student(
    student_id: uuid.UUID,
    status: Optional[str] = Query(None, regex=r'^(enrolled|dropped|completed|withdrawn)$'),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all classes for a student

    Optional filter:
    - status: enrolled, dropped, completed, or withdrawn
    """
    try:
        service = StudentClassService(db)

        enrollments = await service.get_classes_for_student(student_id, status)

        return StudentClassListResponseSchema(
            enrollments=[StudentClassResponseSchema(**e.to_dict()) for e in enrollments],
            total=len(enrollments)
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/enrollments/{enrollment_id}/drop", response_model=StudentClassResponseSchema)
async def drop_student(
    enrollment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Drop a student from a class

    Sets status to 'dropped' and records drop_date.
    Decrements class enrollment count.
    """
    try:
        service = StudentClassService(db)
        enrollment = await service.drop_student(enrollment_id)
        return StudentClassResponseSchema(**enrollment.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/enrollments/{enrollment_id}/withdraw", response_model=StudentClassResponseSchema)
async def withdraw_student(
    enrollment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Withdraw a student from a class

    Sets status to 'withdrawn' and records drop_date.
    Decrements class enrollment count.
    """
    try:
        service = StudentClassService(db)
        enrollment = await service.withdraw_student(enrollment_id)
        return StudentClassResponseSchema(**enrollment.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/enrollments/{enrollment_id}/complete", response_model=StudentClassResponseSchema)
async def complete_enrollment(
    enrollment_id: uuid.UUID,
    completion_data: StudentClassCompleteSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark enrollment as completed with optional final grade

    Sets status to 'completed'.
    Decrements class enrollment count.
    """
    try:
        service = StudentClassService(db)

        enrollment = await service.complete_enrollment(
            enrollment_id=enrollment_id,
            final_grade=completion_data.final_grade,
            final_score=completion_data.final_score
        )

        return StudentClassResponseSchema(**enrollment.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/enrollments/{enrollment_id}/grades", response_model=StudentClassResponseSchema)
async def update_grades(
    enrollment_id: uuid.UUID,
    grades_data: StudentClassUpdateGradesSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update student's final grade and score"""
    try:
        service = StudentClassService(db)

        enrollment = await service.update_grades(
            enrollment_id=enrollment_id,
            final_grade=grades_data.final_grade,
            final_score=grades_data.final_score
        )

        return StudentClassResponseSchema(**enrollment.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/enrollments/{enrollment_id}", status_code=204)
async def delete_enrollment(
    enrollment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an enrollment (hard delete)

    This permanently removes the enrollment record.
    If status is 'enrolled', decrements class enrollment count.
    """
    try:
        service = StudentClassService(db)
        await service.delete_enrollment(enrollment_id)
        return None

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
