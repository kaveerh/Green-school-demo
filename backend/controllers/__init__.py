"""
Controllers Package
API endpoint handlers
"""
from controllers.user_controller import router as user_router

# Export all routers
__all__ = [
    "user_router",
]
