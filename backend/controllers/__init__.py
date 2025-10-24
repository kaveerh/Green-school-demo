"""
Controllers Package
API endpoint handlers
"""
from controllers.user_controller import router as user_router
from controllers.school_controller import router as school_router
from controllers.teacher_controller import router as teacher_router
from controllers.student_controller import router as student_router
from controllers.parent_controller import router as parent_router
from controllers.subject_controller import router as subject_router
from controllers.room_controller import router as room_router
from controllers.class_controller import router as class_router
from controllers.lesson_controller import router as lesson_router
from controllers.assessment_controller import router as assessment_router

# Export all routers
__all__ = [
    "user_router",
    "school_router",
    "teacher_router",
    "student_router",
    "parent_router",
    "subject_router",
    "room_router",
    "class_router",
    "lesson_router",
    "assessment_router",
]
