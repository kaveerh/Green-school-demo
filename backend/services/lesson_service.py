"""
Lesson Service

Business logic for lesson planning and curriculum management.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, timedelta
import uuid

from models.lesson import Lesson
from models.teacher import Teacher
from models.class_model import Class
from models.subject import Subject
from repositories.lesson_repository import LessonRepository
from repositories.teacher_repository import TeacherRepository
from repositories.class_repository import ClassRepository
from repositories.subject_repository import SubjectRepository


class LessonService:
    """Service for lesson operations"""

    def __init__(
        self,
        lesson_repository: LessonRepository,
        teacher_repository: TeacherRepository,
        class_repository: ClassRepository,
        subject_repository: SubjectRepository
    ):
        self.lesson_repository = lesson_repository
        self.teacher_repository = teacher_repository
        self.class_repository = class_repository
        self.subject_repository = subject_repository

    async def create_lesson(
        self,
        school_id: uuid.UUID,
        class_id: uuid.UUID,
        teacher_id: uuid.UUID,
        subject_id: uuid.UUID,
        title: str,
        scheduled_date: date,
        duration_minutes: int = 45,
        lesson_number: Optional[int] = None,
        description: Optional[str] = None,
        learning_objectives: Optional[List[str]] = None,
        materials_needed: Optional[List[str]] = None,
        curriculum_standards: Optional[List[str]] = None,
        introduction: Optional[str] = None,
        main_activity: Optional[str] = None,
        assessment: Optional[str] = None,
        homework: Optional[str] = None,
        notes: Optional[str] = None,
        links: Optional[List[str]] = None,
        color: Optional[str] = None,
        is_template: bool = False,
        template_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> Lesson:
        """
        Create a new lesson with validation

        Args:
            school_id: School UUID
            class_id: Class UUID
            teacher_id: Teacher UUID
            subject_id: Subject UUID
            title: Lesson title (1-200 characters)
            scheduled_date: Date the lesson is scheduled
            duration_minutes: Duration in minutes (1-240)
            lesson_number: Lesson number (auto-generated if not provided)
            description: Lesson description
            learning_objectives: List of learning objectives
            materials_needed: List of materials needed
            curriculum_standards: List of curriculum standards
            introduction: Introduction section
            main_activity: Main activity section
            assessment: Assessment section
            homework: Homework section
            notes: Additional notes
            links: List of resource links
            color: Color code for calendar display
            is_template: Whether this is a template
            template_id: Template this lesson was created from

        Returns:
            Created Lesson object

        Raises:
            ValueError: If validation fails
        """
        # Validate title
        if not title or len(title) < 1 or len(title) > 200:
            raise ValueError("Title must be between 1 and 200 characters")

        # Validate duration
        if duration_minutes < 1 or duration_minutes > 240:
            raise ValueError("Duration must be between 1 and 240 minutes")

        # Validate scheduled date
        if scheduled_date < date(2020, 1, 1):
            raise ValueError("Scheduled date must be after 2020-01-01")
        if scheduled_date > date(2099, 12, 31):
            raise ValueError("Scheduled date must be before 2100-01-01")

        # Validate color format if provided
        if color and not self._is_valid_color(color):
            raise ValueError("Color must be in format #RRGGBB")

        # Validate teacher exists and belongs to school
        teacher = await self.teacher_repository.get_by_id(teacher_id)
        if not teacher:
            raise ValueError(f"Teacher {teacher_id} not found")
        if teacher.school_id != school_id:
            raise ValueError("Teacher does not belong to this school")

        # Validate class exists and belongs to school
        class_obj = await self.class_repository.get_by_id(class_id)
        if not class_obj:
            raise ValueError(f"Class {class_id} not found")
        if class_obj.school_id != school_id:
            raise ValueError("Class does not belong to this school")

        # Validate subject exists and belongs to school
        subject = await self.subject_repository.get_by_id(subject_id)
        if not subject:
            raise ValueError(f"Subject {subject_id} not found")
        if subject.school_id != school_id:
            raise ValueError("Subject does not belong to this school")

        # Validate template if provided
        if template_id:
            template = await self.lesson_repository.get_by_id(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            if not template.is_template:
                raise ValueError("Referenced lesson is not a template")
            if template.school_id != school_id:
                raise ValueError("Template does not belong to this school")

        # Get next lesson number if not provided
        if lesson_number is None:
            lesson_number = await self.lesson_repository.get_next_lesson_number(class_id)
        else:
            # Validate lesson number is positive
            if lesson_number < 1:
                raise ValueError("Lesson number must be positive")

            # Check if lesson number already exists for this class
            exists = await self.lesson_repository.lesson_number_exists(class_id, lesson_number)
            if exists:
                raise ValueError(f"Lesson number {lesson_number} already exists for this class")

        # Create lesson data
        lesson_data = {
            "school_id": school_id,
            "class_id": class_id,
            "teacher_id": teacher_id,
            "subject_id": subject_id,
            "title": title,
            "lesson_number": lesson_number,
            "scheduled_date": scheduled_date,
            "duration_minutes": duration_minutes,
            "description": description,
            "learning_objectives": learning_objectives or [],
            "materials_needed": materials_needed or [],
            "curriculum_standards": curriculum_standards or [],
            "introduction": introduction,
            "main_activity": main_activity,
            "assessment": assessment,
            "homework": homework,
            "notes": notes,
            "links": links or [],
            "color": color,
            "is_template": is_template,
            "template_id": template_id,
            "status": "draft"
        }

        # Create lesson
        lesson = await self.lesson_repository.create(lesson_data)
        return lesson

    async def create_from_template(
        self,
        template_id: uuid.UUID,
        class_id: uuid.UUID,
        scheduled_date: date,
        lesson_number: Optional[int] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Lesson:
        """
        Create a lesson from a template

        Args:
            template_id: Template UUID
            class_id: Class UUID to create lesson for
            scheduled_date: Date to schedule the lesson
            lesson_number: Lesson number (auto-generated if not provided)
            overrides: Optional field overrides

        Returns:
            Created Lesson object

        Raises:
            ValueError: If validation fails
        """
        # Get template
        template = await self.lesson_repository.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        if not template.is_template:
            raise ValueError("Referenced lesson is not a template")

        # Get class to get school_id
        class_obj = await self.class_repository.get_by_id(class_id)
        if not class_obj:
            raise ValueError(f"Class {class_id} not found")

        # Validate template belongs to same school
        if template.school_id != class_obj.school_id:
            raise ValueError("Template does not belong to this school")

        # Clone template data
        lesson_data = template.clone_as_template()

        # Set required fields
        lesson_data['class_id'] = class_id
        lesson_data['scheduled_date'] = scheduled_date
        lesson_data['school_id'] = class_obj.school_id
        lesson_data['teacher_id'] = template.teacher_id
        lesson_data['subject_id'] = template.subject_id

        # Apply overrides
        if overrides:
            lesson_data.update(overrides)

        # Create lesson using create_lesson for full validation
        return await self.create_lesson(**lesson_data)

    async def get_lesson(self, lesson_id: uuid.UUID) -> Optional[Lesson]:
        """Get lesson by ID"""
        return await self.lesson_repository.get_by_id(lesson_id)

    async def get_lessons(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 50,
        class_id: Optional[uuid.UUID] = None,
        teacher_id: Optional[uuid.UUID] = None,
        subject_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        is_template: Optional[bool] = None
    ) -> Tuple[List[Lesson], int]:
        """
        Get lessons with pagination and filters

        Returns:
            Tuple of (lessons list, total count)
        """
        return await self.lesson_repository.get_by_school(
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

    async def get_lessons_by_date_range(
        self,
        school_id: uuid.UUID,
        start_date: date,
        end_date: date,
        teacher_id: Optional[uuid.UUID] = None,
        class_id: Optional[uuid.UUID] = None,
        subject_id: Optional[uuid.UUID] = None
    ) -> List[Lesson]:
        """Get lessons within a date range (for calendar view)"""
        return await self.lesson_repository.get_by_date_range(
            school_id=school_id,
            start_date=start_date,
            end_date=end_date,
            teacher_id=teacher_id,
            class_id=class_id,
            subject_id=subject_id
        )

    async def get_upcoming_lessons(
        self,
        school_id: uuid.UUID,
        teacher_id: Optional[uuid.UUID] = None,
        days: int = 7,
        limit: int = 50
    ) -> List[Lesson]:
        """Get upcoming lessons (within next N days)"""
        return await self.lesson_repository.get_upcoming_lessons(
            school_id=school_id,
            teacher_id=teacher_id,
            days=days,
            limit=limit
        )

    async def get_past_due_lessons(
        self,
        school_id: uuid.UUID,
        teacher_id: Optional[uuid.UUID] = None,
        limit: int = 50
    ) -> List[Lesson]:
        """Get lessons that are past their scheduled date but not completed"""
        return await self.lesson_repository.get_past_due_lessons(
            school_id=school_id,
            teacher_id=teacher_id,
            limit=limit
        )

    async def search_lessons(
        self,
        school_id: uuid.UUID,
        query: str,
        teacher_id: Optional[uuid.UUID] = None,
        subject_id: Optional[uuid.UUID] = None,
        limit: int = 50
    ) -> List[Lesson]:
        """Search lessons by title, description, or content"""
        lessons, _ = await self.lesson_repository.search(
            school_id=school_id,
            search_query=query,
            teacher_id=teacher_id,
            limit=limit
        )
        return lessons

    async def get_templates(
        self,
        school_id: uuid.UUID,
        teacher_id: Optional[uuid.UUID] = None,
        subject_id: Optional[uuid.UUID] = None
    ) -> List[Lesson]:
        """Get all lesson templates"""
        return await self.lesson_repository.get_templates(
            school_id=school_id,
            teacher_id=teacher_id,
            subject_id=subject_id
        )

    async def update_lesson(
        self,
        lesson_id: uuid.UUID,
        updates: Dict[str, Any]
    ) -> Optional[Lesson]:
        """
        Update lesson with validation

        Args:
            lesson_id: Lesson UUID
            updates: Dictionary of fields to update

        Returns:
            Updated Lesson object or None if not found

        Raises:
            ValueError: If validation fails
        """
        # Get existing lesson
        lesson = await self.lesson_repository.get_by_id(lesson_id)
        if not lesson:
            return None

        # Validate title if being updated
        if 'title' in updates:
            title = updates['title']
            if not title or len(title) < 1 or len(title) > 200:
                raise ValueError("Title must be between 1 and 200 characters")

        # Validate duration if being updated
        if 'duration_minutes' in updates:
            duration = updates['duration_minutes']
            if duration < 1 or duration > 240:
                raise ValueError("Duration must be between 1 and 240 minutes")

        # Validate scheduled_date if being updated
        if 'scheduled_date' in updates:
            scheduled_date = updates['scheduled_date']
            if scheduled_date < date(2020, 1, 1):
                raise ValueError("Scheduled date must be after 2020-01-01")
            if scheduled_date > date(2099, 12, 31):
                raise ValueError("Scheduled date must be before 2100-01-01")

        # Validate color if being updated
        if 'color' in updates and updates['color']:
            if not self._is_valid_color(updates['color']):
                raise ValueError("Color must be in format #RRGGBB")

        # Validate completion_percentage if being updated
        if 'completion_percentage' in updates:
            percentage = updates['completion_percentage']
            if percentage < 0 or percentage > 100:
                raise ValueError("Completion percentage must be between 0 and 100")

        # Validate status if being updated
        if 'status' in updates:
            status = updates['status']
            valid_statuses = ['draft', 'scheduled', 'in_progress', 'completed', 'cancelled']
            if status not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")

        # Validate lesson_number if being updated
        if 'lesson_number' in updates:
            new_number = updates['lesson_number']
            if new_number < 1:
                raise ValueError("Lesson number must be positive")

            # Check if new lesson number conflicts with existing
            if new_number != lesson.lesson_number:
                exists = await self.lesson_repository.lesson_number_exists(
                    lesson.class_id,
                    new_number
                )
                if exists:
                    raise ValueError(f"Lesson number {new_number} already exists for this class")

        # Validate relationships if being updated
        if 'teacher_id' in updates:
            teacher = await self.teacher_repository.get_by_id(updates['teacher_id'])
            if not teacher:
                raise ValueError(f"Teacher {updates['teacher_id']} not found")
            if teacher.school_id != lesson.school_id:
                raise ValueError("Teacher does not belong to this school")

        if 'class_id' in updates:
            class_obj = await self.class_repository.get_by_id(updates['class_id'])
            if not class_obj:
                raise ValueError(f"Class {updates['class_id']} not found")
            if class_obj.school_id != lesson.school_id:
                raise ValueError("Class does not belong to this school")

        if 'subject_id' in updates:
            subject = await self.subject_repository.get_by_id(updates['subject_id'])
            if not subject:
                raise ValueError(f"Subject {updates['subject_id']} not found")
            if subject.school_id != lesson.school_id:
                raise ValueError("Subject does not belong to this school")

        # Update lesson
        return await self.lesson_repository.update(lesson_id, updates)

    async def start_lesson(self, lesson_id: uuid.UUID) -> Optional[Lesson]:
        """
        Start a lesson (set status to in_progress)

        Raises:
            ValueError: If lesson cannot be started
        """
        lesson = await self.lesson_repository.get_by_id(lesson_id)
        if not lesson:
            return None

        if not lesson.can_start():
            raise ValueError(
                f"Lesson cannot be started. Current status: {lesson.status}. "
                "Lesson must be in 'draft' or 'scheduled' status and not past due."
            )

        lesson.start()
        return await self.lesson_repository.update(lesson_id, {"status": lesson.status})

    async def complete_lesson(
        self,
        lesson_id: uuid.UUID,
        completion_percentage: int = 100,
        actual_duration_minutes: Optional[int] = None,
        reflection: Optional[str] = None,
        what_went_well: Optional[str] = None,
        what_to_improve: Optional[str] = None,
        modifications_needed: Optional[str] = None
    ) -> Optional[Lesson]:
        """
        Complete a lesson with reflection

        Raises:
            ValueError: If lesson cannot be completed or validation fails
        """
        lesson = await self.lesson_repository.get_by_id(lesson_id)
        if not lesson:
            return None

        if not lesson.can_complete():
            raise ValueError(
                f"Lesson cannot be completed. Current status: {lesson.status}. "
                "Lesson must be in 'scheduled' or 'in_progress' status."
            )

        # Validate completion_percentage
        if completion_percentage < 0 or completion_percentage > 100:
            raise ValueError("Completion percentage must be between 0 and 100")

        # Validate actual_duration_minutes if provided
        if actual_duration_minutes and (actual_duration_minutes < 1 or actual_duration_minutes > 240):
            raise ValueError("Actual duration must be between 1 and 240 minutes")

        # Complete lesson
        lesson.complete(
            completion_percentage=completion_percentage,
            actual_duration_minutes=actual_duration_minutes,
            reflection=reflection,
            what_went_well=what_went_well,
            what_to_improve=what_to_improve,
            modifications_needed=modifications_needed
        )

        # Update in database
        updates = {
            "status": lesson.status,
            "completion_percentage": lesson.completion_percentage
        }
        if actual_duration_minutes:
            updates["actual_duration_minutes"] = actual_duration_minutes
        if reflection:
            updates["reflection"] = reflection
        if what_went_well:
            updates["what_went_well"] = what_went_well
        if what_to_improve:
            updates["what_to_improve"] = what_to_improve
        if modifications_needed:
            updates["modifications_needed"] = modifications_needed

        return await self.lesson_repository.update(lesson_id, updates)

    async def cancel_lesson(self, lesson_id: uuid.UUID) -> Optional[Lesson]:
        """
        Cancel a lesson

        Raises:
            ValueError: If lesson cannot be cancelled
        """
        lesson = await self.lesson_repository.get_by_id(lesson_id)
        if not lesson:
            return None

        if not lesson.can_cancel():
            raise ValueError(
                f"Lesson cannot be cancelled. Current status: {lesson.status}. "
                "Lesson must be in 'draft', 'scheduled', or 'in_progress' status."
            )

        lesson.cancel()
        return await self.lesson_repository.update(lesson_id, {"status": lesson.status})

    async def delete_lesson(self, lesson_id: uuid.UUID) -> bool:
        """Soft delete a lesson"""
        return await self.lesson_repository.delete(lesson_id)

    async def get_statistics(
        self,
        school_id: Optional[uuid.UUID] = None,
        teacher_id: Optional[uuid.UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get lesson statistics"""
        return await self.lesson_repository.get_statistics(
            school_id=school_id,
            teacher_id=teacher_id,
            start_date=start_date,
            end_date=end_date
        )

    async def convert_to_template(self, lesson_id: uuid.UUID) -> Optional[Lesson]:
        """
        Convert a lesson to a template

        This keeps the original lesson but marks it as a template
        """
        lesson = await self.lesson_repository.get_by_id(lesson_id)
        if not lesson:
            return None

        return await self.lesson_repository.update(lesson_id, {"is_template": True})

    async def duplicate_lesson(
        self,
        lesson_id: uuid.UUID,
        new_scheduled_date: date,
        new_class_id: Optional[uuid.UUID] = None,
        new_lesson_number: Optional[int] = None
    ) -> Optional[Lesson]:
        """
        Duplicate a lesson to a new date (and optionally new class)

        Args:
            lesson_id: Lesson to duplicate
            new_scheduled_date: New scheduled date
            new_class_id: Optional new class (uses original if not provided)
            new_lesson_number: Optional new lesson number (auto-generated if not provided)

        Returns:
            New Lesson object
        """
        # Get original lesson
        original = await self.lesson_repository.get_by_id(lesson_id)
        if not original:
            return None

        # Clone lesson data
        lesson_data = original.clone_as_template()

        # Set new values
        lesson_data['scheduled_date'] = new_scheduled_date
        lesson_data['class_id'] = new_class_id or original.class_id
        lesson_data['school_id'] = original.school_id
        lesson_data['teacher_id'] = original.teacher_id
        lesson_data['subject_id'] = original.subject_id
        lesson_data['status'] = 'draft'  # Reset to draft
        lesson_data['completion_percentage'] = 0
        lesson_data['actual_duration_minutes'] = None
        lesson_data['reflection'] = None
        lesson_data['what_went_well'] = None
        lesson_data['what_to_improve'] = None
        lesson_data['modifications_needed'] = None

        # Create new lesson
        return await self.create_lesson(**lesson_data)

    def _is_valid_color(self, color: str) -> bool:
        """Validate color format (#RRGGBB)"""
        if not color:
            return False
        if not color.startswith('#'):
            return False
        if len(color) != 7:
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
