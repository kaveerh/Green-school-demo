"""
Authentication Utilities
Dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import uuid


# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


class CurrentUser:
    """Current authenticated user information"""
    def __init__(
        self,
        id: uuid.UUID,
        email: str,
        persona: str,
        school_id: uuid.UUID
    ):
        self.id = id
        self.email = email
        self.persona = persona
        self.school_id = school_id

    def is_admin(self) -> bool:
        """Check if user is administrator"""
        return self.persona == "administrator"


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> CurrentUser:
    """
    Get current authenticated user from token

    For now, this is a mock implementation that returns a test user.
    In production, this would validate the JWT token and extract user info.

    Args:
        credentials: HTTP Bearer token

    Returns:
        CurrentUser instance

    Raises:
        HTTPException: If authentication fails
    """
    # TODO: Implement actual JWT token validation with Keycloak
    # For now, return a mock admin user for testing

    if not credentials:
        # For testing purposes, return a default admin user
        # In production, this should raise an authentication error
        return CurrentUser(
            id=uuid.UUID("ea2ad94a-b077-48c2-ae25-6e3e8dc54499"),  # Admin user from seed data
            email="admin@greenschool.edu",
            persona="administrator",
            school_id=uuid.UUID("60da2256-81fc-4ca5-bf6b-467b8d371c61")
        )

    # In production, validate token here
    # token = credentials.credentials
    # Decode JWT, validate signature, extract user claims

    return CurrentUser(
        id=uuid.UUID("ea2ad94a-b077-48c2-ae25-6e3e8dc54499"),
        email="admin@greenschool.edu",
        persona="administrator",
        school_id=uuid.UUID("60da2256-81fc-4ca5-bf6b-467b8d371c61")
    )


async def require_admin(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Require administrator role

    Args:
        current_user: Current authenticated user

    Returns:
        CurrentUser instance

    Raises:
        HTTPException: If user is not an administrator
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )
    return current_user
