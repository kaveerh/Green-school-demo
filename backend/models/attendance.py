"""
Attendance Model

Daily student attendance tracking with status, check-in/out times, and parent notifications.
"""

from sqlalchemy import Column, String, Date, Time, Boolean, Text, CheckConstraint, Index, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from models.base import BaseModel
from datetime import date as date_type, time as time_type, datetime
import uuid


class Attendance(BaseModel):
    """Attendance model for daily student attendance tracking"""
    __tablename__ = "attendance"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(PG_UUID(as_uuid=True), ForeignKey("classes.id", ondelete="SET NULL"), nullable=True)  # NULL for homeroom

    # Attendance Details
    attendance_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)  # present, absent, tardy, excused, sick

    # Time Tracking
    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)

    # Additional Information
    notes = Column(Text, nullable=True)
    recorded_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Parent Notification
    parent_notified = Column(Boolean, default=False, nullable=True)
    notified_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    school = relationship("School", foreign_keys=[school_id])
    student = relationship("Student", back_populates="attendance_records")
    class_obj = relationship("Class", foreign_keys=[class_id])
    recorder = relationship("User", foreign_keys=[recorded_by])

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('present', 'absent', 'tardy', 'excused', 'sick')",
            name="chk_attendance_status"
        ),
        Index('idx_attendance_school_id', 'school_id'),
        Index('idx_attendance_student_id', 'student_id'),
        Index('idx_attendance_class_id', 'class_id'),
        Index('idx_attendance_date', 'attendance_date'),
        Index('idx_attendance_status', 'status'),
        Index('idx_attendance_student_date', 'student_id', 'attendance_date'),
        Index('idx_attendance_class_date', 'class_id', 'attendance_date'),
        Index('idx_attendance_school_date', 'school_id', 'attendance_date'),
        Index('idx_attendance_deleted_at', 'deleted_at'),
    )

    def __repr__(self):
        return f"<Attendance(id={self.id}, student_id={self.student_id}, date={self.attendance_date}, status={self.status})>"

    @property
    def is_present(self) -> bool:
        """Check if student was present"""
        return self.status == 'present'

    @property
    def is_absent(self) -> bool:
        """Check if student was absent"""
        return self.status in ('absent', 'sick')

    @property
    def needs_parent_notification(self) -> bool:
        """Check if parent needs to be notified"""
        return self.status in ('absent', 'tardy', 'sick') and not self.parent_notified

    @property
    def duration_minutes(self) -> int:
        """Calculate duration in minutes if both check-in and check-out times exist"""
        if self.check_in_time and self.check_out_time:
            # Convert time objects to datetime for calculation
            check_in_dt = datetime.combine(datetime.today(), self.check_in_time)
            check_out_dt = datetime.combine(datetime.today(), self.check_out_time)
            duration = check_out_dt - check_in_dt
            return int(duration.total_seconds() / 60)
        return 0

    def to_dict(self, include_relationships: bool = False):
        """Convert attendance to dictionary"""
        data = super().to_dict()

        # Add computed properties
        data['is_present'] = self.is_present
        data['is_absent'] = self.is_absent
        data['needs_parent_notification'] = self.needs_parent_notification
        data['duration_minutes'] = self.duration_minutes

        if include_relationships:
            # Only include relationships if already loaded
            try:
                if self.student and self.student.user:
                    data["student"] = {
                        "id": str(self.student.id),
                        "student_id": self.student.student_id,
                        "name": f"{self.student.user.first_name} {self.student.user.last_name}",
                        "grade_level": self.student.grade_level
                    }
            except:
                pass

            try:
                if self.class_obj:
                    data["class"] = {
                        "id": str(self.class_obj.id),
                        "name": self.class_obj.name,
                        "code": self.class_obj.code
                    }
            except:
                pass

            try:
                if self.recorder:
                    data["recorded_by_name"] = f"{self.recorder.first_name} {self.recorder.last_name}"
            except:
                pass

        return data
