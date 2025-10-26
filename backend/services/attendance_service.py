"""
Attendance Service

Business logic layer for Attendance operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.attendance_repository import AttendanceRepository
from repositories.student_repository import StudentRepository
from repositories.class_repository import ClassRepository
from repositories.user_repository import UserRepository
from models.attendance import Attendance
from datetime import datetime, date, time
import uuid


class AttendanceService:
    """Service layer for Attendance business logic"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = AttendanceRepository(session)
        self.student_repository = StudentRepository(session)
        self.class_repository = ClassRepository(session)
        self.user_repository = UserRepository(session)

    async def create_attendance(
        self,
        school_id: uuid.UUID,
        student_id: uuid.UUID,
        attendance_date: date,
        status: str,
        created_by_id: uuid.UUID,
        class_id: Optional[uuid.UUID] = None,
        check_in_time: Optional[time] = None,
        check_out_time: Optional[time] = None,
        notes: Optional[str] = None,
        recorded_by: Optional[uuid.UUID] = None
    ) -> Attendance:
        """Create a new attendance record"""

        # Validate student exists
        student = await self.student_repository.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

        # Validate class if provided
        if class_id:
            class_obj = await self.class_repository.get_by_id(class_id)
            if not class_obj:
                raise ValueError("Class not found")

        # Check for duplicate attendance
        existing = await self.repository.check_duplicate(student_id, class_id, attendance_date)
        if existing:
            raise ValueError("Attendance record already exists for this student, class, and date")

        # Validate status
        valid_statuses = ['present', 'absent', 'tardy', 'excused', 'sick']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        attendance_data = {
            'school_id': school_id,
            'student_id': student_id,
            'class_id': class_id,
            'attendance_date': attendance_date,
            'status': status,
            'check_in_time': check_in_time,
            'check_out_time': check_out_time,
            'notes': notes,
            'recorded_by': recorded_by or created_by_id,
            'parent_notified': False
        }

        return await self.repository.create(attendance_data, created_by_id)

    async def bulk_create_attendance(
        self,
        school_id: uuid.UUID,
        class_id: uuid.UUID,
        attendance_date: date,
        student_statuses: List[Dict[str, Any]],
        created_by_id: uuid.UUID
    ) -> List[Attendance]:
        """
        Create attendance records for multiple students in a class

        Args:
            school_id: School UUID
            class_id: Class UUID
            attendance_date: Date of attendance
            student_statuses: List of dicts with keys: student_id, status, check_in_time, check_out_time, notes
            created_by_id: User creating the records

        Returns:
            List of created Attendance records
        """
        # Validate class exists
        class_obj = await self.class_repository.get_by_id(class_id)
        if not class_obj:
            raise ValueError("Class not found")

        created_records = []
        errors = []

        for student_data in student_statuses:
            try:
                attendance = await self.create_attendance(
                    school_id=school_id,
                    student_id=student_data['student_id'],
                    attendance_date=attendance_date,
                    status=student_data['status'],
                    created_by_id=created_by_id,
                    class_id=class_id,
                    check_in_time=student_data.get('check_in_time'),
                    check_out_time=student_data.get('check_out_time'),
                    notes=student_data.get('notes')
                )
                created_records.append(attendance)
            except ValueError as e:
                errors.append({
                    'student_id': student_data['student_id'],
                    'error': str(e)
                })

        if errors:
            # Log errors but continue with successful records
            print(f"Bulk attendance creation had {len(errors)} errors: {errors}")

        return created_records

    async def update_attendance(
        self,
        attendance_id: uuid.UUID,
        updated_by_id: uuid.UUID,
        status: Optional[str] = None,
        check_in_time: Optional[time] = None,
        check_out_time: Optional[time] = None,
        notes: Optional[str] = None
    ) -> Optional[Attendance]:
        """Update an existing attendance record"""
        attendance = await self.repository.get_by_id(attendance_id)
        if not attendance:
            return None

        update_data = {}

        if status is not None:
            valid_statuses = ['present', 'absent', 'tardy', 'excused', 'sick']
            if status not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            update_data['status'] = status

        if check_in_time is not None:
            update_data['check_in_time'] = check_in_time

        if check_out_time is not None:
            update_data['check_out_time'] = check_out_time

        if notes is not None:
            update_data['notes'] = notes

        if not update_data:
            return attendance

        return await self.repository.update(attendance_id, update_data, updated_by_id)

    async def mark_parent_notified(
        self,
        attendance_id: uuid.UUID,
        updated_by_id: uuid.UUID
    ) -> Optional[Attendance]:
        """Mark that parent has been notified of absence/tardiness"""
        update_data = {
            'parent_notified': True,
            'notified_at': datetime.now()
        }

        return await self.repository.update(attendance_id, update_data, updated_by_id)

    async def bulk_mark_parent_notified(
        self,
        attendance_ids: List[uuid.UUID],
        updated_by_id: uuid.UUID
    ) -> int:
        """Mark multiple attendance records as parent notified"""
        count = 0
        for attendance_id in attendance_ids:
            result = await self.mark_parent_notified(attendance_id, updated_by_id)
            if result:
                count += 1
        return count

    async def get_student_attendance(
        self,
        student_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Attendance], int]:
        """Get attendance records for a student"""
        return await self.repository.get_by_student(
            student_id, start_date, end_date, status, page, limit
        )

    async def get_class_attendance(
        self,
        class_id: uuid.UUID,
        attendance_date: date,
        page: int = 1,
        limit: int = 100
    ) -> tuple[List[Attendance], int]:
        """Get attendance records for a class on a specific date"""
        return await self.repository.get_by_class(class_id, attendance_date, page, limit)

    async def get_school_attendance(
        self,
        school_id: uuid.UUID,
        attendance_date: date,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 100
    ) -> tuple[List[Attendance], int]:
        """Get attendance records for a school on a specific date"""
        return await self.repository.get_by_school_date(
            school_id, attendance_date, status, page, limit
        )

    async def get_attendance_by_date_range(
        self,
        school_id: uuid.UUID,
        start_date: date,
        end_date: date,
        class_id: Optional[uuid.UUID] = None,
        student_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None
    ) -> List[Attendance]:
        """Get attendance records within a date range"""
        return await self.repository.get_by_date_range(
            school_id, start_date, end_date, class_id, student_id, status
        )

    async def get_unnotified_absences(
        self,
        school_id: uuid.UUID,
        attendance_date: Optional[date] = None
    ) -> List[Attendance]:
        """Get absence records that haven't been sent to parents yet"""
        return await self.repository.get_unnotified_absences(school_id, attendance_date)

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        start_date: date,
        end_date: date,
        class_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get attendance statistics for a school within a date range"""
        return await self.repository.get_statistics(school_id, start_date, end_date, class_id)

    async def delete_attendance(
        self,
        attendance_id: uuid.UUID,
        deleted_by_id: uuid.UUID
    ) -> bool:
        """Soft delete an attendance record"""
        return await self.repository.delete(attendance_id, deleted_by_id)
