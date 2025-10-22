"""
Class ORM Models

Class and StudentClass models for class management.
"""

from sqlalchemy import Column, String, Integer, Boolean, DECIMAL, ForeignKey, Date, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from typing import Optional, Dict, Any, List
import uuid

from .base import BaseModel


class Class(BaseModel):
    """Class model for class sections"""

    __tablename__ = "classes"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(PG_UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    teacher_id = Column(PG_UUID(as_uuid=True), ForeignKey("teachers.id", ondelete="RESTRICT"), nullable=False, index=True)
    room_id = Column(PG_UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True, index=True)

    # Identification
    code = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String, nullable=True)

    # Classification
    grade_level = Column(Integer, nullable=False, index=True)
    quarter = Column(String(10), nullable=False, index=True)
    academic_year = Column(String(20), nullable=False, index=True)

    # Capacity
    max_students = Column(Integer, nullable=False, default=30)
    current_enrollment = Column(Integer, default=0)

    # Schedule (JSONB)
    schedule = Column(JSONB, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Display
    color = Column(String(7), nullable=True)
    display_order = Column(Integer, default=0)

    # Relationships
    school = relationship("School", back_populates="classes")
    subject = relationship("Subject")
    teacher = relationship("Teacher")
    room = relationship("Room")
    student_enrollments = relationship("StudentClass", back_populates="class_obj", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint('school_id', 'code', name='uq_classes_code_school'),
        CheckConstraint('grade_level >= 1 AND grade_level <= 7', name='chk_classes_grade'),
        CheckConstraint("quarter IN ('Q1', 'Q2', 'Q3', 'Q4')", name='chk_classes_quarter'),
        CheckConstraint('max_students > 0', name='chk_classes_max_students'),
        CheckConstraint('current_enrollment >= 0 AND current_enrollment <= max_students', name='chk_classes_enrollment'),
        {'extend_existing': True}
    )

    def __repr__(self) -> str:
        return f"<Class {self.code} - Grade {self.grade_level} - {self.quarter}>"

    def to_dict(self) -> dict:
        """Convert class to dictionary with computed fields"""
        base_dict = super().to_dict()

        # Add relationship data only if already loaded (avoid lazy loading)
        try:
            if self.subject:
                base_dict['subject_name'] = self.subject.name
                base_dict['subject_code'] = self.subject.code
        except:
            pass

        try:
            if self.teacher and self.teacher.user:
                base_dict['teacher_name'] = f"{self.teacher.user.first_name} {self.teacher.user.last_name}"
        except:
            pass

        try:
            if self.room:
                base_dict['room_number'] = self.room.room_number
        except:
            pass

        # Add computed fields
        base_dict['is_full'] = self.is_full()
        base_dict['capacity_percent'] = self.get_capacity_percent()
        base_dict['available_seats'] = self.get_available_seats()

        return base_dict

    def is_full(self) -> bool:
        """Check if class is at capacity"""
        return self.current_enrollment >= self.max_students

    def get_capacity_percent(self) -> float:
        """Get capacity utilization percentage"""
        if self.max_students == 0:
            return 0.0
        return round((self.current_enrollment / self.max_students) * 100, 1)

    def get_available_seats(self) -> int:
        """Get number of available seats"""
        return max(0, self.max_students - self.current_enrollment)

    def can_enroll_student(self) -> bool:
        """Check if class can accept more students"""
        return not self.is_full() and self.is_active

    def increment_enrollment(self) -> None:
        """Increment current enrollment count"""
        if not self.is_full():
            self.current_enrollment += 1

    def decrement_enrollment(self) -> None:
        """Decrement current enrollment count"""
        if self.current_enrollment > 0:
            self.current_enrollment -= 1

    def get_schedule_display(self) -> Optional[str]:
        """Get formatted schedule string"""
        if not self.schedule:
            return None

        days = self.schedule.get('days', [])
        start_time = self.schedule.get('start_time')
        end_time = self.schedule.get('end_time')

        if not days or not start_time or not end_time:
            return None

        days_str = ', '.join(days)
        return f"{days_str} • {start_time}-{end_time}"


class StudentClass(BaseModel):
    """StudentClass model for student enrollment in classes"""

    __tablename__ = "student_classes"

    # Foreign Keys
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(PG_UUID(as_uuid=True), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Enrollment
    enrollment_date = Column(Date, nullable=False)
    drop_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default='enrolled', index=True)

    # Grades
    final_grade = Column(String(5), nullable=True)
    final_score = Column(DECIMAL(5, 2), nullable=True)

    # Relationships
    student = relationship("Student")
    class_obj = relationship("Class", back_populates="student_enrollments")

    # Constraints
    __table_args__ = (
        UniqueConstraint('student_id', 'class_id', name='uq_student_class'),
        CheckConstraint(
            "status IN ('enrolled', 'dropped', 'completed', 'withdrawn')",
            name='chk_student_classes_status'
        ),
        CheckConstraint(
            'final_score IS NULL OR (final_score >= 0 AND final_score <= 100)',
            name='chk_student_classes_score'
        ),
        {'extend_existing': True}
    )

    def __repr__(self) -> str:
        return f"<StudentClass student={self.student_id} class={self.class_id} status={self.status}>"

    def to_dict(self) -> dict:
        """Convert student class to dictionary"""
        base_dict = super().to_dict()

        # Add student name if available (avoid lazy loading)
        try:
            if self.student and self.student.user:
                base_dict['student_name'] = f"{self.student.user.first_name} {self.student.user.last_name}"
        except:
            pass

        return base_dict

    def is_active(self) -> bool:
        """Check if enrollment is currently active"""
        return self.status == 'enrolled'

    def complete(self) -> None:
        """Mark enrollment as completed"""
        self.status = 'completed'

    def drop(self) -> None:
        """Drop student from class"""
        from datetime import date
        self.status = 'dropped'
        self.drop_date = date.today()

    def withdraw(self) -> None:
        """Withdraw student from class"""
        from datetime import date
        self.status = 'withdrawn'
        self.drop_date = date.today()
