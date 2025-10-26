"""
Attendance Repository

Data access layer for Attendance operations with specialized queries.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from models.attendance import Attendance
from models.student import Student
from models.class_model import Class
from models.user import User
from repositories.base_repository import BaseRepository
from datetime import date, timedelta
import uuid


class AttendanceRepository(BaseRepository[Attendance]):
    """Repository for Attendance data access"""

    def __init__(self, session: AsyncSession):
        super().__init__(Attendance, session)

    async def get_with_relationships(self, attendance_id: uuid.UUID) -> Optional[Attendance]:
        """Get attendance record with all relationships loaded"""
        query = select(Attendance).where(
            and_(
                Attendance.id == attendance_id,
                Attendance.deleted_at.is_(None)
            )
        ).options(
            selectinload(Attendance.student).selectinload(Student.user),
            selectinload(Attendance.class_obj),
            selectinload(Attendance.recorder),
            selectinload(Attendance.school)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_student(
        self,
        student_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Attendance], int]:
        """Get attendance records for a student with optional filters"""
        offset = (page - 1) * limit

        # Build base conditions
        conditions = [
            Attendance.student_id == student_id,
            Attendance.deleted_at.is_(None)
        ]

        if start_date:
            conditions.append(Attendance.attendance_date >= start_date)
        if end_date:
            conditions.append(Attendance.attendance_date <= end_date)
        if status:
            conditions.append(Attendance.status == status)

        # Count query
        count_query = select(func.count(Attendance.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Attendance).where(and_(*conditions)).options(
            selectinload(Attendance.class_obj)
        ).offset(offset).limit(limit).order_by(desc(Attendance.attendance_date))

        result = await self.session.execute(query)
        attendance_records = result.scalars().all()

        return list(attendance_records), total

    async def get_by_class(
        self,
        class_id: uuid.UUID,
        attendance_date: date,
        page: int = 1,
        limit: int = 100
    ) -> tuple[List[Attendance], int]:
        """Get attendance records for a class on a specific date"""
        offset = (page - 1) * limit

        conditions = [
            Attendance.class_id == class_id,
            Attendance.attendance_date == attendance_date,
            Attendance.deleted_at.is_(None)
        ]

        # Count query
        count_query = select(func.count(Attendance.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Attendance).where(and_(*conditions)).options(
            selectinload(Attendance.student).selectinload(Student.user)
        ).offset(offset).limit(limit).order_by(asc(Attendance.student_id))

        result = await self.session.execute(query)
        attendance_records = result.scalars().all()

        return list(attendance_records), total

    async def get_by_school_date(
        self,
        school_id: uuid.UUID,
        attendance_date: date,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 100
    ) -> tuple[List[Attendance], int]:
        """Get attendance records for a school on a specific date"""
        offset = (page - 1) * limit

        conditions = [
            Attendance.school_id == school_id,
            Attendance.attendance_date == attendance_date,
            Attendance.deleted_at.is_(None)
        ]

        if status:
            conditions.append(Attendance.status == status)

        # Count query
        count_query = select(func.count(Attendance.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Attendance).where(and_(*conditions)).options(
            selectinload(Attendance.student).selectinload(Student.user),
            selectinload(Attendance.class_obj)
        ).offset(offset).limit(limit).order_by(asc(Attendance.student_id))

        result = await self.session.execute(query)
        attendance_records = result.scalars().all()

        return list(attendance_records), total

    async def get_by_date_range(
        self,
        school_id: uuid.UUID,
        start_date: date,
        end_date: date,
        class_id: Optional[uuid.UUID] = None,
        student_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None
    ) -> List[Attendance]:
        """Get attendance records within a date range"""
        conditions = [
            Attendance.school_id == school_id,
            Attendance.attendance_date >= start_date,
            Attendance.attendance_date <= end_date,
            Attendance.deleted_at.is_(None)
        ]

        if class_id:
            conditions.append(Attendance.class_id == class_id)
        if student_id:
            conditions.append(Attendance.student_id == student_id)
        if status:
            conditions.append(Attendance.status == status)

        query = select(Attendance).where(and_(*conditions)).options(
            selectinload(Attendance.student).selectinload(Student.user),
            selectinload(Attendance.class_obj)
        ).order_by(desc(Attendance.attendance_date))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_unnotified_absences(
        self,
        school_id: uuid.UUID,
        attendance_date: Optional[date] = None
    ) -> List[Attendance]:
        """Get absence records that haven't been sent to parents yet"""
        conditions = [
            Attendance.school_id == school_id,
            Attendance.status.in_(['absent', 'tardy', 'sick']),
            Attendance.parent_notified == False,
            Attendance.deleted_at.is_(None)
        ]

        if attendance_date:
            conditions.append(Attendance.attendance_date == attendance_date)
        else:
            # Default to today
            conditions.append(Attendance.attendance_date == date.today())

        query = select(Attendance).where(and_(*conditions)).options(
            selectinload(Attendance.student).selectinload(Student.user)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        start_date: date,
        end_date: date,
        class_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get attendance statistics for a school within a date range"""
        conditions = [
            Attendance.school_id == school_id,
            Attendance.attendance_date >= start_date,
            Attendance.attendance_date <= end_date,
            Attendance.deleted_at.is_(None)
        ]

        if class_id:
            conditions.append(Attendance.class_id == class_id)

        # Total records
        total_query = select(func.count(Attendance.id)).where(and_(*conditions))
        total_result = await self.session.execute(total_query)
        total_records = total_result.scalar()

        # By status
        status_query = select(
            Attendance.status,
            func.count(Attendance.id).label('count')
        ).where(and_(*conditions)).group_by(Attendance.status)
        status_result = await self.session.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result}

        # Calculate rates
        present_count = by_status.get('present', 0)
        absent_count = by_status.get('absent', 0) + by_status.get('sick', 0)
        tardy_count = by_status.get('tardy', 0)
        excused_count = by_status.get('excused', 0)

        attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
        absence_rate = (absent_count / total_records * 100) if total_records > 0 else 0

        # Unique students
        unique_students_query = select(func.count(func.distinct(Attendance.student_id))).where(and_(*conditions))
        unique_students_result = await self.session.execute(unique_students_query)
        unique_students = unique_students_result.scalar()

        # Average daily attendance
        days_query = select(func.count(func.distinct(Attendance.attendance_date))).where(and_(*conditions))
        days_result = await self.session.execute(days_query)
        days = days_result.scalar()
        avg_daily_attendance = (total_records / days) if days > 0 else 0

        return {
            "total_records": total_records,
            "unique_students": unique_students,
            "days_tracked": days,
            "avg_daily_attendance": float(avg_daily_attendance),
            "by_status": by_status,
            "present_count": present_count,
            "absent_count": absent_count,
            "tardy_count": tardy_count,
            "excused_count": excused_count,
            "attendance_rate": float(attendance_rate),
            "absence_rate": float(absence_rate)
        }

    async def check_duplicate(
        self,
        student_id: uuid.UUID,
        class_id: Optional[uuid.UUID],
        attendance_date: date
    ) -> Optional[Attendance]:
        """Check if attendance already exists for student, class, and date"""
        query = select(Attendance).where(
            and_(
                Attendance.student_id == student_id,
                Attendance.class_id == class_id if class_id else Attendance.class_id.is_(None),
                Attendance.attendance_date == attendance_date,
                Attendance.deleted_at.is_(None)
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
