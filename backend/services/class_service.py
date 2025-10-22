"""
Class Service

Business logic for Class operations.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple, Dict, Any
import uuid
import re
from datetime import date, datetime

from models.class_model import Class, StudentClass
from models.subject import Subject
from models.teacher import Teacher
from models.room import Room
from models.student import Student
from repositories.class_repository import ClassRepository, StudentClassRepository


class ClassService:
    """Service for Class business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ClassRepository(db)

    async def create_class(
        self,
        school_id: uuid.UUID,
        code: str,
        name: str,
        subject_id: uuid.UUID,
        teacher_id: uuid.UUID,
        grade_level: int,
        quarter: str,
        academic_year: str,
        max_students: int,
        room_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        schedule: Optional[Dict[str, Any]] = None,
        color: Optional[str] = None,
        display_order: int = 0
    ) -> Class:
        """Create a new class with validation"""

        # Validate code format
        code = code.strip().upper()
        if not self._validate_class_code(code):
            raise ValueError(
                "Invalid class code format. Expected format: SUBJECT-GRADE-QUARTER-SECTION "
                "(e.g., MATH-5-Q1-A)"
            )

        # Check if code already exists
        if await self.repository.code_exists(school_id, code):
            raise ValueError(f"Class code '{code}' already exists in this school")

        # Validate grade level
        if not self._validate_grade_level(grade_level):
            raise ValueError("Grade level must be between 1 and 7")

        # Validate quarter
        if not self._validate_quarter(quarter):
            raise ValueError("Quarter must be Q1, Q2, Q3, or Q4")

        # Validate academic year
        if not self._validate_academic_year(academic_year):
            raise ValueError("Academic year must be in format YYYY-YYYY (e.g., 2024-2025)")

        # Validate max_students
        if max_students <= 0:
            raise ValueError("Maximum students must be greater than 0")

        # Validate schedule if provided
        if schedule:
            self._validate_schedule(schedule)

        # Validate color if provided
        if color and not self._validate_hex_color(color):
            raise ValueError("Color must be a valid hex color (e.g., #FF5733)")

        # Verify subject exists and belongs to school
        subject = await self._get_subject(subject_id)
        if not subject:
            raise ValueError(f"Subject with ID {subject_id} not found")
        if subject.school_id != school_id:
            raise ValueError("Subject does not belong to this school")

        # Verify teacher exists and belongs to school
        teacher = await self._get_teacher(teacher_id)
        if not teacher:
            raise ValueError(f"Teacher with ID {teacher_id} not found")
        if teacher.school_id != school_id:
            raise ValueError("Teacher does not belong to this school")

        # Verify room exists and belongs to school (if provided)
        if room_id:
            room = await self._get_room(room_id)
            if not room:
                raise ValueError(f"Room with ID {room_id} not found")
            if room.school_id != school_id:
                raise ValueError("Room does not belong to this school")

        # Create class
        class_obj = Class(
            school_id=school_id,
            code=code,
            name=name.strip(),
            subject_id=subject_id,
            teacher_id=teacher_id,
            room_id=room_id,
            grade_level=grade_level,
            quarter=quarter.upper(),
            academic_year=academic_year,
            max_students=max_students,
            description=description.strip() if description else None,
            schedule=schedule,
            color=color,
            display_order=display_order
        )

        return await self.repository.create(class_obj)

    async def get_class_by_id(self, class_id: uuid.UUID) -> Optional[Class]:
        """Get class by ID"""
        return await self.repository.get_by_id(class_id)

    async def get_class_by_code(self, school_id: uuid.UUID, code: str) -> Optional[Class]:
        """Get class by code"""
        return await self.repository.get_by_code(school_id, code.upper())

    async def get_classes_by_school(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 50,
        subject_id: Optional[uuid.UUID] = None,
        teacher_id: Optional[uuid.UUID] = None,
        room_id: Optional[uuid.UUID] = None,
        grade_level: Optional[int] = None,
        quarter: Optional[str] = None,
        academic_year: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Class], int]:
        """Get classes for a school with filters"""

        # Validate filters
        if grade_level is not None and not self._validate_grade_level(grade_level):
            raise ValueError("Grade level must be between 1 and 7")

        if quarter and not self._validate_quarter(quarter):
            raise ValueError("Quarter must be Q1, Q2, Q3, or Q4")

        if academic_year and not self._validate_academic_year(academic_year):
            raise ValueError("Academic year must be in format YYYY-YYYY")

        return await self.repository.get_by_school(
            school_id=school_id,
            page=page,
            limit=limit,
            subject_id=subject_id,
            teacher_id=teacher_id,
            room_id=room_id,
            grade_level=grade_level,
            quarter=quarter.upper() if quarter else None,
            academic_year=academic_year,
            is_active=is_active
        )

    async def get_classes_by_teacher(
        self,
        school_id: uuid.UUID,
        teacher_id: uuid.UUID,
        quarter: Optional[str] = None,
        academic_year: Optional[str] = None
    ) -> List[Class]:
        """Get all classes for a teacher"""

        if quarter and not self._validate_quarter(quarter):
            raise ValueError("Quarter must be Q1, Q2, Q3, or Q4")

        if academic_year and not self._validate_academic_year(academic_year):
            raise ValueError("Academic year must be in format YYYY-YYYY")

        return await self.repository.get_by_teacher(
            school_id=school_id,
            teacher_id=teacher_id,
            quarter=quarter.upper() if quarter else None,
            academic_year=academic_year
        )

    async def get_classes_by_subject(
        self,
        school_id: uuid.UUID,
        subject_id: uuid.UUID,
        grade_level: Optional[int] = None,
        quarter: Optional[str] = None
    ) -> List[Class]:
        """Get all classes for a subject"""

        if grade_level is not None and not self._validate_grade_level(grade_level):
            raise ValueError("Grade level must be between 1 and 7")

        if quarter and not self._validate_quarter(quarter):
            raise ValueError("Quarter must be Q1, Q2, Q3, or Q4")

        return await self.repository.get_by_subject(
            school_id=school_id,
            subject_id=subject_id,
            grade_level=grade_level,
            quarter=quarter.upper() if quarter else None
        )

    async def get_classes_by_room(
        self,
        school_id: uuid.UUID,
        room_id: uuid.UUID
    ) -> List[Class]:
        """Get all classes for a room"""
        return await self.repository.get_by_room(school_id, room_id)

    async def search_classes(
        self,
        school_id: uuid.UUID,
        query: str,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Class], int]:
        """Search classes by code, name, or description"""
        if not query or len(query.strip()) < 2:
            raise ValueError("Search query must be at least 2 characters")

        return await self.repository.search(school_id, query.strip(), page, limit)

    async def update_class(
        self,
        class_id: uuid.UUID,
        code: Optional[str] = None,
        name: Optional[str] = None,
        subject_id: Optional[uuid.UUID] = None,
        teacher_id: Optional[uuid.UUID] = None,
        room_id: Optional[uuid.UUID] = None,
        grade_level: Optional[int] = None,
        quarter: Optional[str] = None,
        academic_year: Optional[str] = None,
        max_students: Optional[int] = None,
        description: Optional[str] = None,
        schedule: Optional[Dict[str, Any]] = None,
        color: Optional[str] = None,
        display_order: Optional[int] = None
    ) -> Class:
        """Update class"""

        class_obj = await self.repository.get_by_id(class_id)
        if not class_obj:
            raise ValueError(f"Class with ID {class_id} not found")

        # Validate and update code
        if code is not None:
            code = code.strip().upper()
            if not self._validate_class_code(code):
                raise ValueError("Invalid class code format")

            if await self.repository.code_exists(class_obj.school_id, code, class_id):
                raise ValueError(f"Class code '{code}' already exists in this school")

            class_obj.code = code

        # Validate and update name
        if name is not None:
            class_obj.name = name.strip()

        # Validate and update subject
        if subject_id is not None:
            subject = await self._get_subject(subject_id)
            if not subject:
                raise ValueError(f"Subject with ID {subject_id} not found")
            if subject.school_id != class_obj.school_id:
                raise ValueError("Subject does not belong to this school")
            class_obj.subject_id = subject_id

        # Validate and update teacher
        if teacher_id is not None:
            teacher = await self._get_teacher(teacher_id)
            if not teacher:
                raise ValueError(f"Teacher with ID {teacher_id} not found")
            if teacher.school_id != class_obj.school_id:
                raise ValueError("Teacher does not belong to this school")
            class_obj.teacher_id = teacher_id

        # Validate and update room
        if room_id is not None:
            if room_id:  # Allow setting to null
                room = await self._get_room(room_id)
                if not room:
                    raise ValueError(f"Room with ID {room_id} not found")
                if room.school_id != class_obj.school_id:
                    raise ValueError("Room does not belong to this school")
            class_obj.room_id = room_id

        # Validate and update grade level
        if grade_level is not None:
            if not self._validate_grade_level(grade_level):
                raise ValueError("Grade level must be between 1 and 7")
            class_obj.grade_level = grade_level

        # Validate and update quarter
        if quarter is not None:
            if not self._validate_quarter(quarter):
                raise ValueError("Quarter must be Q1, Q2, Q3, or Q4")
            class_obj.quarter = quarter.upper()

        # Validate and update academic year
        if academic_year is not None:
            if not self._validate_academic_year(academic_year):
                raise ValueError("Academic year must be in format YYYY-YYYY")
            class_obj.academic_year = academic_year

        # Validate and update max_students
        if max_students is not None:
            if max_students <= 0:
                raise ValueError("Maximum students must be greater than 0")
            if max_students < class_obj.current_enrollment:
                raise ValueError(
                    f"Cannot set max_students to {max_students}. "
                    f"Current enrollment is {class_obj.current_enrollment}"
                )
            class_obj.max_students = max_students

        # Update description
        if description is not None:
            class_obj.description = description.strip() if description else None

        # Validate and update schedule
        if schedule is not None:
            if schedule:  # Allow setting to null
                self._validate_schedule(schedule)
            class_obj.schedule = schedule

        # Validate and update color
        if color is not None:
            if color and not self._validate_hex_color(color):
                raise ValueError("Color must be a valid hex color")
            class_obj.color = color

        # Update display_order
        if display_order is not None:
            class_obj.display_order = display_order

        return await self.repository.update(class_obj)

    async def delete_class(self, class_id: uuid.UUID) -> None:
        """Soft delete class"""
        class_obj = await self.repository.get_by_id(class_id)
        if not class_obj:
            raise ValueError(f"Class with ID {class_id} not found")

        await self.repository.delete(class_obj)

    async def toggle_status(self, class_id: uuid.UUID) -> Class:
        """Toggle class active status"""
        class_obj = await self.repository.get_by_id(class_id)
        if not class_obj:
            raise ValueError(f"Class with ID {class_id} not found")

        class_obj.is_active = not class_obj.is_active
        return await self.repository.update(class_obj)

    async def get_statistics(self, school_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Get class statistics"""
        return await self.repository.get_statistics(school_id)

    # Validation helpers
    def _validate_class_code(self, code: str) -> bool:
        """Validate class code format (SUBJECT-GRADE-QUARTER-SECTION)"""
        pattern = r'^[A-Z]+-[1-7]-(Q[1-4])-[A-Z0-9]+$'
        return bool(re.match(pattern, code))

    def _validate_grade_level(self, grade: int) -> bool:
        """Validate grade level (1-7)"""
        return 1 <= grade <= 7

    def _validate_quarter(self, quarter: str) -> bool:
        """Validate quarter (Q1, Q2, Q3, Q4)"""
        return quarter.upper() in ['Q1', 'Q2', 'Q3', 'Q4']

    def _validate_academic_year(self, year: str) -> bool:
        """Validate academic year format (YYYY-YYYY)"""
        pattern = r'^\d{4}-\d{4}$'
        if not re.match(pattern, year):
            return False

        start_year, end_year = year.split('-')
        return int(end_year) == int(start_year) + 1

    def _validate_hex_color(self, color: str) -> bool:
        """Validate hex color format"""
        pattern = r'^#[0-9A-Fa-f]{6}$'
        return bool(re.match(pattern, color))

    def _validate_schedule(self, schedule: Dict[str, Any]) -> None:
        """Validate schedule structure"""
        if not isinstance(schedule, dict):
            raise ValueError("Schedule must be a dictionary")

        if 'days' not in schedule or 'start_time' not in schedule or 'end_time' not in schedule:
            raise ValueError("Schedule must include 'days', 'start_time', and 'end_time'")

        # Validate days
        if not isinstance(schedule['days'], list) or not schedule['days']:
            raise ValueError("Schedule days must be a non-empty list")

        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in schedule['days']:
            if day not in valid_days:
                raise ValueError(f"Invalid day: {day}")

        # Validate times
        time_pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'
        if not re.match(time_pattern, schedule['start_time']):
            raise ValueError("Invalid start_time format. Use HH:MM (e.g., 09:00)")
        if not re.match(time_pattern, schedule['end_time']):
            raise ValueError("Invalid end_time format. Use HH:MM (e.g., 10:30)")

        # Validate start < end
        start_hours, start_mins = map(int, schedule['start_time'].split(':'))
        end_hours, end_mins = map(int, schedule['end_time'].split(':'))

        if (start_hours * 60 + start_mins) >= (end_hours * 60 + end_mins):
            raise ValueError("start_time must be before end_time")

    async def _get_subject(self, subject_id: uuid.UUID) -> Optional[Subject]:
        """Get subject by ID"""
        result = await self.db.execute(
            select(Subject).where(Subject.id == subject_id)
        )
        return result.scalar_one_or_none()

    async def _get_teacher(self, teacher_id: uuid.UUID) -> Optional[Teacher]:
        """Get teacher by ID"""
        result = await self.db.execute(
            select(Teacher).where(Teacher.id == teacher_id)
        )
        return result.scalar_one_or_none()

    async def _get_room(self, room_id: uuid.UUID) -> Optional[Room]:
        """Get room by ID"""
        result = await self.db.execute(
            select(Room).where(Room.id == room_id)
        )
        return result.scalar_one_or_none()


class StudentClassService:
    """Service for StudentClass business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = StudentClassRepository(db)
        self.class_repository = ClassRepository(db)

    async def enroll_student(
        self,
        student_id: uuid.UUID,
        class_id: uuid.UUID,
        enrollment_date: Optional[date] = None
    ) -> StudentClass:
        """Enroll a student in a class"""

        # Check if student exists
        student = await self._get_student(student_id)
        if not student:
            raise ValueError(f"Student with ID {student_id} not found")

        # Check if class exists
        class_obj = await self.class_repository.get_by_id(class_id)
        if not class_obj:
            raise ValueError(f"Class with ID {class_id} not found")

        # Verify student and class belong to same school
        if student.school_id != class_obj.school_id:
            raise ValueError("Student and class must belong to the same school")

        # Check if already enrolled
        if await self.repository.enrollment_exists(student_id, class_id):
            raise ValueError("Student is already enrolled in this class")

        # Check if class can accept more students
        if not class_obj.can_enroll_student():
            if class_obj.is_full():
                raise ValueError(
                    f"Class is at capacity ({class_obj.current_enrollment}/{class_obj.max_students})"
                )
            else:
                raise ValueError("Class is not active and cannot accept new enrollments")

        # Create enrollment
        student_class = StudentClass(
            student_id=student_id,
            class_id=class_id,
            enrollment_date=enrollment_date or date.today(),
            status='enrolled'
        )

        result = await self.repository.create(student_class)

        # Increment class enrollment count
        class_obj.increment_enrollment()
        await self.class_repository.update(class_obj)

        return result

    async def get_enrollment_by_id(self, enrollment_id: uuid.UUID) -> Optional[StudentClass]:
        """Get enrollment by ID"""
        return await self.repository.get_by_id(enrollment_id)

    async def get_students_in_class(self, class_id: uuid.UUID) -> List[StudentClass]:
        """Get all students enrolled in a class"""
        return await self.repository.get_students_in_class(class_id)

    async def get_classes_for_student(
        self,
        student_id: uuid.UUID,
        status: Optional[str] = None
    ) -> List[StudentClass]:
        """Get all classes for a student"""
        if status and status not in ['enrolled', 'dropped', 'completed', 'withdrawn']:
            raise ValueError("Invalid status. Must be: enrolled, dropped, completed, or withdrawn")

        return await self.repository.get_classes_for_student(student_id, status)

    async def drop_student(self, enrollment_id: uuid.UUID) -> StudentClass:
        """Drop a student from a class"""
        enrollment = await self.repository.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment with ID {enrollment_id} not found")

        if enrollment.status != 'enrolled':
            raise ValueError(f"Cannot drop student with status '{enrollment.status}'")

        # Update enrollment status
        enrollment.drop()
        result = await self.repository.update(enrollment)

        # Decrement class enrollment count
        class_obj = await self.class_repository.get_by_id(enrollment.class_id)
        if class_obj:
            class_obj.decrement_enrollment()
            await self.class_repository.update(class_obj)

        return result

    async def withdraw_student(self, enrollment_id: uuid.UUID) -> StudentClass:
        """Withdraw a student from a class"""
        enrollment = await self.repository.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment with ID {enrollment_id} not found")

        if enrollment.status != 'enrolled':
            raise ValueError(f"Cannot withdraw student with status '{enrollment.status}'")

        # Update enrollment status
        enrollment.withdraw()
        result = await self.repository.update(enrollment)

        # Decrement class enrollment count
        class_obj = await self.class_repository.get_by_id(enrollment.class_id)
        if class_obj:
            class_obj.decrement_enrollment()
            await self.class_repository.update(class_obj)

        return result

    async def complete_enrollment(
        self,
        enrollment_id: uuid.UUID,
        final_grade: Optional[str] = None,
        final_score: Optional[float] = None
    ) -> StudentClass:
        """Mark enrollment as completed with final grade"""
        enrollment = await self.repository.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment with ID {enrollment_id} not found")

        if enrollment.status != 'enrolled':
            raise ValueError(f"Cannot complete enrollment with status '{enrollment.status}'")

        # Validate final score
        if final_score is not None:
            if not (0 <= final_score <= 100):
                raise ValueError("Final score must be between 0 and 100")

        # Update enrollment
        enrollment.complete()
        if final_grade:
            enrollment.final_grade = final_grade
        if final_score is not None:
            enrollment.final_score = final_score

        result = await self.repository.update(enrollment)

        # Decrement class enrollment count
        class_obj = await self.class_repository.get_by_id(enrollment.class_id)
        if class_obj:
            class_obj.decrement_enrollment()
            await self.class_repository.update(class_obj)

        return result

    async def update_grades(
        self,
        enrollment_id: uuid.UUID,
        final_grade: Optional[str] = None,
        final_score: Optional[float] = None
    ) -> StudentClass:
        """Update student's final grade and score"""
        enrollment = await self.repository.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment with ID {enrollment_id} not found")

        # Validate final score
        if final_score is not None:
            if not (0 <= final_score <= 100):
                raise ValueError("Final score must be between 0 and 100")

        # Update grades
        if final_grade is not None:
            enrollment.final_grade = final_grade
        if final_score is not None:
            enrollment.final_score = final_score

        return await self.repository.update(enrollment)

    async def delete_enrollment(self, enrollment_id: uuid.UUID) -> None:
        """Delete an enrollment (hard delete)"""
        enrollment = await self.repository.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment with ID {enrollment_id} not found")

        # Decrement class enrollment if status is enrolled
        if enrollment.status == 'enrolled':
            class_obj = await self.class_repository.get_by_id(enrollment.class_id)
            if class_obj:
                class_obj.decrement_enrollment()
                await self.class_repository.update(class_obj)

        await self.repository.delete(enrollment)

    async def _get_student(self, student_id: uuid.UUID) -> Optional[Student]:
        """Get student by ID"""
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        return result.scalar_one_or_none()
