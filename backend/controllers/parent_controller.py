"""
Parent Controller

API endpoints for Parent CRUD operations and relationship management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from services.parent_service import ParentService
from schemas.parent_schema import (
    ParentCreateSchema,
    ParentUpdateSchema,
    ParentResponseSchema,
    ParentListResponseSchema,
    ParentStudentLinkSchema,
    ParentStudentRelationshipResponseSchema,
    ParentStatisticsSchema
)
from database import get_db
import uuid


router = APIRouter(prefix="/parents", tags=["parents"])


# Dependency to get ParentService
async def get_parent_service(session: AsyncSession = Depends(get_db)) -> ParentService:
    return ParentService(session)


# 1. Create Parent
@router.post("", response_model=ParentResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_parent(
    parent_data: ParentCreateSchema,
    service: ParentService = Depends(get_parent_service)
):
    """
    Create a new parent.

    **Required:**
    - school_id: School UUID
    - user_id: User account UUID (must have 'parent' persona)

    **Optional:**
    - occupation, workplace
    - phone_mobile, phone_work
    - preferred_contact_method (email, phone, sms, app_notification)
    - emergency_contact (default: false)
    - pickup_authorized (default: false)
    - receives_newsletter (default: true)

    **Permissions:** Administrator only
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()  # Placeholder

        parent = await service.create_parent(
            school_id=parent_data.school_id,
            user_id=parent_data.user_id,
            occupation=parent_data.occupation,
            workplace=parent_data.workplace,
            phone_mobile=parent_data.phone_mobile,
            phone_work=parent_data.phone_work,
            preferred_contact_method=parent_data.preferred_contact_method,
            emergency_contact=parent_data.emergency_contact or False,
            pickup_authorized=parent_data.pickup_authorized or False,
            receives_newsletter=parent_data.receives_newsletter if parent_data.receives_newsletter is not None else True,
            created_by_id=current_user_id
        )

        # Load relationships for response
        parent_with_relations = await service.get_parent_by_id(parent.id)

        return ParentResponseSchema(
            **parent_with_relations.to_dict(include_relationships=True)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create parent: {str(e)}"
        )


# 2. List Parents (Paginated)
@router.get("", response_model=ParentListResponseSchema)
async def list_parents(
    school_id: Optional[uuid.UUID] = Query(None, description="Filter by school"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Results per page"),
    service: ParentService = Depends(get_parent_service)
):
    """
    List parents with pagination.

    **Query Parameters:**
    - school_id: Filter by school (optional)
    - page: Page number (default: 1)
    - limit: Results per page (default: 50, max: 100)

    **Permissions:** Administrator, Teacher
    """
    try:
        # TODO: Get current user's school_id from auth if not provided
        if not school_id:
            school_id = uuid.UUID("60da2256-81fc-4ca5-bf6b-467b8d371c61")  # Placeholder

        parents, total = await service.get_parents_by_school(school_id, page, limit)

        return ParentListResponseSchema(
            parents=[ParentResponseSchema(**p.to_dict(include_relationships=False)) for p in parents],
            total=total,
            page=page,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list parents: {str(e)}"
        )


# 3. Get Parent by ID
@router.get("/{parent_id}", response_model=ParentResponseSchema)
async def get_parent(
    parent_id: uuid.UUID,
    service: ParentService = Depends(get_parent_service)
):
    """
    Get a specific parent by ID with relationships.

    **Permissions:** Administrator, Teacher, Parent (own only)
    """
    try:
        parent = await service.get_parent_by_id(parent_id)

        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent not found"
            )

        return ParentResponseSchema(
            **parent.to_dict(include_relationships=True)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get parent: {str(e)}"
        )


# 4. Update Parent
@router.put("/{parent_id}", response_model=ParentResponseSchema)
async def update_parent(
    parent_id: uuid.UUID,
    parent_data: ParentUpdateSchema,
    service: ParentService = Depends(get_parent_service)
):
    """
    Update parent information.

    All fields are optional. Only provided fields will be updated.

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()  # Placeholder

        parent = await service.update_parent(
            parent_id=parent_id,
            updated_by_id=current_user_id,
            occupation=parent_data.occupation,
            workplace=parent_data.workplace,
            phone_mobile=parent_data.phone_mobile,
            phone_work=parent_data.phone_work,
            preferred_contact_method=parent_data.preferred_contact_method,
            emergency_contact=parent_data.emergency_contact,
            pickup_authorized=parent_data.pickup_authorized,
            receives_newsletter=parent_data.receives_newsletter
        )

        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent not found"
            )

        # Reload with relationships
        parent_with_relations = await service.get_parent_by_id(parent.id)

        return ParentResponseSchema(
            **parent_with_relations.to_dict(include_relationships=True)
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
            detail=f"Failed to update parent: {str(e)}"
        )


# 5. Delete Parent
@router.delete("/{parent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parent(
    parent_id: uuid.UUID,
    service: ParentService = Depends(get_parent_service)
):
    """
    Soft delete a parent.

    This will also soft delete all parent-student relationships.

    **Permissions:** Administrator only
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()  # Placeholder

        success = await service.delete_parent(parent_id, current_user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent not found"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete parent: {str(e)}"
        )


# 6. Link Parent to Student
@router.post("/{parent_id}/link-student", response_model=ParentStudentRelationshipResponseSchema, status_code=status.HTTP_201_CREATED)
async def link_parent_to_student(
    parent_id: uuid.UUID,
    link_data: ParentStudentLinkSchema,
    service: ParentService = Depends(get_parent_service)
):
    """
    Create a relationship between parent and student.

    **Required:**
    - student_id: Student UUID
    - relationship_type: mother, father, guardian, etc.

    **Optional:**
    - is_primary_contact (default: false)
    - has_legal_custody (default: true)
    - has_pickup_permission (default: true)

    **Permissions:** Administrator only
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()  # Placeholder

        relationship = await service.link_student(
            parent_id=parent_id,
            student_id=link_data.student_id,
            relationship_type=link_data.relationship_type,
            is_primary_contact=link_data.is_primary_contact or False,
            has_legal_custody=link_data.has_legal_custody if link_data.has_legal_custody is not None else True,
            has_pickup_permission=link_data.has_pickup_permission if link_data.has_pickup_permission is not None else True,
            created_by_id=current_user_id
        )

        return ParentStudentRelationshipResponseSchema(
            id=str(relationship.id),
            school_id=str(relationship.school_id),
            parent_id=str(relationship.parent_id),
            student_id=str(relationship.student_id),
            relationship_type=relationship.relationship_type,
            is_primary_contact=relationship.is_primary_contact,
            has_legal_custody=relationship.has_legal_custody,
            has_pickup_permission=relationship.has_pickup_permission,
            created_at=relationship.created_at,
            updated_at=relationship.updated_at
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link parent to student: {str(e)}"
        )


# 7. Unlink Parent from Student
@router.delete("/{parent_id}/unlink-student/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_parent_from_student(
    parent_id: uuid.UUID,
    student_id: uuid.UUID,
    service: ParentService = Depends(get_parent_service)
):
    """
    Remove relationship between parent and student.

    **Permissions:** Administrator only
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()  # Placeholder

        success = await service.unlink_student(parent_id, student_id, current_user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relationship not found"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlink parent from student: {str(e)}"
        )


# 8. Get Parent's Children
@router.get("/{parent_id}/students", response_model=List[dict])
async def get_parent_children(
    parent_id: uuid.UUID,
    service: ParentService = Depends(get_parent_service)
):
    """
    Get all children (students) for a parent.

    **Permissions:** Administrator, Teacher, Parent (own only)
    """
    try:
        students = await service.get_parent_children(parent_id)

        return [
            {
                "id": str(s.id),
                "student_id": s.student_id,
                "grade_level": s.grade_level,
                "status": s.status,
                "user": {
                    "id": str(s.user.id),
                    "first_name": s.user.first_name,
                    "last_name": s.user.last_name,
                    "email": s.user.email
                } if s.user else None
            }
            for s in students
        ]

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get parent's children: {str(e)}"
        )


# 9. Search Parents
@router.get("/search/query", response_model=ParentListResponseSchema)
async def search_parents(
    q: str = Query(..., min_length=2, description="Search query"),
    school_id: Optional[uuid.UUID] = Query(None, description="Filter by school"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    service: ParentService = Depends(get_parent_service)
):
    """
    Search parents by name, email, phone, occupation, or workplace.

    **Query Parameters:**
    - q: Search query (min 2 characters)
    - school_id: Filter by school
    - page, limit: Pagination

    **Permissions:** Administrator, Teacher
    """
    try:
        # TODO: Get current user's school_id from auth if not provided
        if not school_id:
            school_id = uuid.UUID("60da2256-81fc-4ca5-bf6b-467b8d371c61")  # Placeholder

        parents, total = await service.search_parents(school_id, q, page, limit)

        return ParentListResponseSchema(
            parents=[ParentResponseSchema(**p.to_dict(include_relationships=False)) for p in parents],
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
            detail=f"Failed to search parents: {str(e)}"
        )


# 10. Get Student's Parents
@router.get("/by-student/{student_id}", response_model=List[ParentResponseSchema])
async def get_student_parents(
    student_id: uuid.UUID,
    service: ParentService = Depends(get_parent_service)
):
    """
    Get all parents for a specific student.

    **Permissions:** Administrator, Teacher
    """
    try:
        parents = await service.get_student_parents(student_id)

        return [ParentResponseSchema(**p.to_dict(include_relationships=True)) for p in parents]

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student's parents: {str(e)}"
        )


# 11. Get Statistics
@router.get("/statistics/summary", response_model=ParentStatisticsSchema)
async def get_parent_statistics(
    school_id: Optional[uuid.UUID] = Query(None, description="Filter by school"),
    service: ParentService = Depends(get_parent_service)
):
    """
    Get parent statistics for a school.

    Returns counts for:
    - Total parents
    - Emergency contacts
    - Pickup authorized
    - Newsletter subscribers
    - Parents with/without children

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current user's school_id from auth if not provided
        if not school_id:
            school_id = uuid.UUID("60da2256-81fc-4ca5-bf6b-467b8d371c61")  # Placeholder

        stats = await service.get_statistics(school_id)

        return ParentStatisticsSchema(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
