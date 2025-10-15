"""
User Controller
API endpoints for user operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from config.database import get_db
from services.user_service import UserService
from schemas.user_schema import (
    UserCreateSchema,
    UserUpdateSchema,
    UserResponseSchema,
    UserListResponseSchema,
    UserSearchSchema,
    UserStatisticsSchema,
    UserStatusChangeSchema,
    UserPersonaChangeSchema,
    PersonaEnum,
    StatusEnum,
)
from utils.auth import CurrentUser, get_current_user, require_admin


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user. Only administrators can create users."
)
async def create_user(
    user_data: UserCreateSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user

    - **email**: User email (must be unique)
    - **first_name**: User first name
    - **last_name**: User last name
    - **persona**: User role (administrator, teacher, student, parent, vendor)
    - **password**: Password (optional if using SSO)
    - **school_id**: School UUID
    """
    service = UserService(db)

    try:
        user = await service.create_user(user_data, current_user.id)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=UserListResponseSchema,
    summary="List users",
    description="Search and list users with filters and pagination. Only administrators can list users."
)
async def list_users(
    search: Optional[str] = Query(None, description="Search in name and email"),
    persona: Optional[PersonaEnum] = Query(None, description="Filter by persona"),
    status_filter: Optional[StatusEnum] = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: str = Query("created_at", description="Sort field"),
    order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List users with filtering and pagination

    Returns a paginated list of users with metadata
    """
    service = UserService(db)

    search_params = UserSearchSchema(
        search=search,
        persona=persona,
        status=status_filter,
        page=page,
        limit=limit,
        sort=sort,
        order=order
    )

    try:
        users, pagination = await service.search_users(
            school_id=current_user.school_id,
            search_params=search_params,
            requesting_user_persona=current_user.persona
        )

        return {
            "data": users,
            "pagination": pagination
        }
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get(
    "/{user_id}",
    response_model=UserResponseSchema,
    summary="Get a user",
    description="Get a user by ID. Administrators can view any user, others can only view themselves."
)
async def get_user(
    user_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID

    - **user_id**: User UUID
    """
    service = UserService(db)

    try:
        user = await service.get_user(
            user_id=user_id,
            requesting_user_id=current_user.id,
            requesting_user_persona=current_user.persona
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.put(
    "/{user_id}",
    response_model=UserResponseSchema,
    summary="Update a user",
    description="Update a user. Administrators can update any user, others can only update themselves (limited fields)."
)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdateSchema,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user

    - **user_id**: User UUID
    - **first_name**: New first name (optional)
    - **last_name**: New last name (optional)
    - **phone**: New phone number (optional)
    - **avatar_url**: New avatar URL (optional)
    """
    service = UserService(db)

    try:
        user = await service.update_user(
            user_id=user_id,
            user_data=user_data,
            updated_by_id=current_user.id,
            requesting_user_persona=current_user.persona
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Soft delete a user. Only administrators can delete users."
)
async def delete_user(
    user_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user (soft delete)

    - **user_id**: User UUID
    """
    service = UserService(db)

    try:
        success = await service.delete_user(
            user_id=user_id,
            deleted_by_id=current_user.id,
            requesting_user_persona=current_user.persona
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return None
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.patch(
    "/{user_id}/status",
    response_model=UserResponseSchema,
    summary="Change user status",
    description="Change user status. Only administrators can change status."
)
async def change_user_status(
    user_id: uuid.UUID,
    status_data: UserStatusChangeSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user status

    - **user_id**: User UUID
    - **status**: New status (active, inactive, suspended)
    """
    service = UserService(db)

    try:
        user = await service.change_user_status(
            user_id=user_id,
            new_status=status_data.status.value,
            updated_by_id=current_user.id,
            requesting_user_persona=current_user.persona
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user
    except (PermissionError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN if isinstance(e, PermissionError) else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{user_id}/persona",
    response_model=UserResponseSchema,
    summary="Change user persona",
    description="Change user persona/role. Only administrators can change persona."
)
async def change_user_persona(
    user_id: uuid.UUID,
    persona_data: UserPersonaChangeSchema,
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user persona

    - **user_id**: User UUID
    - **persona**: New persona (administrator, teacher, student, parent, vendor)
    """
    service = UserService(db)

    try:
        user = await service.change_user_persona(
            user_id=user_id,
            new_persona=persona_data.persona.value,
            updated_by_id=current_user.id,
            requesting_user_persona=current_user.persona
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user
    except (PermissionError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN if isinstance(e, PermissionError) else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/statistics/summary",
    response_model=UserStatisticsSchema,
    summary="Get user statistics",
    description="Get user statistics for the school. Only administrators can view statistics."
)
async def get_user_statistics(
    current_user: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user statistics

    Returns counts by persona and status
    """
    service = UserService(db)

    try:
        stats = await service.get_statistics(
            school_id=current_user.school_id,
            requesting_user_persona=current_user.persona
        )
        return stats
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
