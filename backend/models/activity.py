"""
Activity and ActivityEnrollment Models

Extracurricular activities management including sports, clubs, art, music, and academic programs.
"""

from sqlalchemy import Column, String, Date, Boolean, Integer, Text, CheckConstraint, Index, ForeignKey, ARRAY, DECIMAL
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from models.base import BaseModel
from datetime import date as date_type
import uuid


class Activity(BaseModel):
    """Activity model for extracurricular activities management"""
    __tablename__ = "activities"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    coordinator_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    room_id = Column(PG_UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)

    # Identification
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True)

    # Classification
    activity_type = Column(String(50), nullable=False)
    category = Column(String(100), nullable=True)

    # Description
    description = Column(Text, nullable=True)

    # Eligibility
    grade_levels = Column(ARRAY(Integer), nullable=False)
    max_participants = Column(Integer, nullable=True)
    min_participants = Column(Integer, nullable=True)

    # Scheduling
    schedule = Column(JSONB, default={}, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    # Location
    location = Column(String(255), nullable=True)

    # Financial
    cost = Column(DECIMAL(10, 2), default=0.00, nullable=True)
    registration_fee = Column(DECIMAL(10, 2), default=0.00, nullable=True)
    equipment_fee = Column(DECIMAL(10, 2), default=0.00, nullable=True)

    # Requirements
    requirements = Column(ARRAY(Text), nullable=True)
    equipment_needed = Column(ARRAY(Text), nullable=True)
    uniform_required = Column(Boolean, default=False, nullable=True)

    # Contact & Communication
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    parent_info = Column(Text, nullable=True)

    # Status
    status = Column(String(20), default="active", nullable=False)
    is_featured = Column(Boolean, default=False, nullable=True)
    registration_open = Column(Boolean, default=True, nullable=True)

    # Display
    photo_url = Column(String(500), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color

    # Relationships
    school = relationship("School", foreign_keys=[school_id])
    coordinator = relationship("User", foreign_keys=[coordinator_id])
    room = relationship("Room", foreign_keys=[room_id])
    enrollments = relationship("ActivityEnrollment", back_populates="activity", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'full', 'cancelled', 'completed')",
            name="chk_activities_status"
        ),
        CheckConstraint(
            "activity_type IN ('sports', 'club', 'art', 'music', 'academic', 'other')",
            name="chk_activities_type"
        ),
        CheckConstraint(
            "cost >= 0",
            name="chk_activities_cost_positive"
        ),
        CheckConstraint(
            "registration_fee >= 0",
            name="chk_activities_registration_fee_positive"
        ),
        CheckConstraint(
            "equipment_fee >= 0",
            name="chk_activities_equipment_fee_positive"
        ),
        CheckConstraint(
            "max_participants IS NULL OR max_participants > 0",
            name="chk_activities_max_participants_positive"
        ),
        CheckConstraint(
            "min_participants IS NULL OR min_participants > 0",
            name="chk_activities_min_participants_positive"
        ),
        CheckConstraint(
            "end_date IS NULL OR start_date IS NULL OR end_date >= start_date",
            name="chk_activities_end_after_start"
        ),
        Index('idx_activities_school_id', 'school_id'),
        Index('idx_activities_coordinator_id', 'coordinator_id'),
        Index('idx_activities_activity_type', 'activity_type'),
        Index('idx_activities_status', 'status'),
        Index('idx_activities_deleted_at', 'deleted_at'),
    )

    def __repr__(self):
        return f"<Activity(id={self.id}, name={self.name}, type={self.activity_type})>"

    @property
    def total_cost(self) -> float:
        """Calculate total cost for participation"""
        cost = float(self.cost or 0)
        reg_fee = float(self.registration_fee or 0)
        equip_fee = float(self.equipment_fee or 0)
        return cost + reg_fee + equip_fee

    @property
    def enrollment_count(self) -> int:
        """Get count of active enrollments"""
        return len([e for e in self.enrollments if e.status == 'active']) if self.enrollments else 0

    @property
    def available_slots(self) -> int:
        """Calculate available enrollment slots"""
        if not self.max_participants:
            return 999  # Unlimited
        return max(0, self.max_participants - self.enrollment_count)

    @property
    def is_full(self) -> bool:
        """Check if activity has reached capacity"""
        if not self.max_participants:
            return False
        return self.enrollment_count >= self.max_participants

    @property
    def is_active(self) -> bool:
        """Check if activity is currently active"""
        if self.status != 'active':
            return False
        if not self.start_date or not self.end_date:
            return True
        today = date_type.today()
        return self.start_date <= today <= self.end_date

    @property
    def is_upcoming(self) -> bool:
        """Check if activity is upcoming"""
        if not self.start_date:
            return False
        return self.start_date > date_type.today() and self.status == 'active'

    @property
    def is_completed(self) -> bool:
        """Check if activity has completed"""
        if self.status == 'completed':
            return True
        if not self.end_date:
            return False
        return self.end_date < date_type.today()

    def to_dict(self, include_relationships: bool = False):
        """Convert activity to dictionary"""
        data = super().to_dict()

        # Convert date objects to strings
        if self.start_date:
            data['start_date'] = self.start_date.isoformat()
        if self.end_date:
            data['end_date'] = self.end_date.isoformat()
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()

        # Convert decimal to float
        if self.cost:
            data['cost'] = float(self.cost)
        if self.registration_fee:
            data['registration_fee'] = float(self.registration_fee)
        if self.equipment_fee:
            data['equipment_fee'] = float(self.equipment_fee)

        # Add computed properties that don't require relationships
        data['total_cost'] = self.total_cost
        data['is_active'] = self.is_active
        data['is_upcoming'] = self.is_upcoming
        data['is_completed'] = self.is_completed

        # Add computed properties that require relationships only if they're loaded
        if include_relationships:
            try:
                data['enrollment_count'] = self.enrollment_count
                data['available_slots'] = self.available_slots
                data['is_full'] = self.is_full
            except:
                # Relationships not loaded, skip these fields
                data['enrollment_count'] = 0
                data['available_slots'] = self.max_participants if self.max_participants else 999
                data['is_full'] = False
        else:
            # Don't access relationships when include_relationships is False
            data['enrollment_count'] = 0
            data['available_slots'] = self.max_participants if self.max_participants else 999
            data['is_full'] = False

        # Convert arrays to lists
        if self.grade_levels:
            data['grade_levels'] = list(self.grade_levels)
        if self.requirements:
            data['requirements'] = list(self.requirements)
        if self.equipment_needed:
            data['equipment_needed'] = list(self.equipment_needed)

        if include_relationships:
            try:
                if self.coordinator:
                    data["coordinator"] = {
                        "id": str(self.coordinator.id),
                        "name": f"{self.coordinator.first_name} {self.coordinator.last_name}",
                        "email": self.coordinator.email
                    }
            except:
                pass

            try:
                if self.room:
                    data["room"] = {
                        "id": str(self.room.id),
                        "name": self.room.name,
                        "room_number": self.room.room_number if hasattr(self.room, 'room_number') else None
                    }
            except:
                pass

        return data


class ActivityEnrollment(BaseModel):
    """Activity enrollment model for tracking student participation"""
    __tablename__ = "activity_enrollments"

    # Foreign Keys
    activity_id = Column(PG_UUID(as_uuid=True), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    withdrawn_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Enrollment Details
    enrollment_date = Column(Date, nullable=False, default=date_type.today)
    status = Column(String(20), default="active", nullable=False)

    # Payment
    payment_status = Column(String(20), default="pending", nullable=True)
    amount_paid = Column(DECIMAL(10, 2), default=0.00, nullable=True)
    payment_date = Column(Date, nullable=True)

    # Attendance
    attendance_count = Column(Integer, default=0, nullable=True)
    total_sessions = Column(Integer, nullable=True)

    # Performance
    performance_notes = Column(Text, nullable=True)
    achievements = Column(ARRAY(Text), nullable=True)

    # Consent & Requirements
    parent_consent = Column(Boolean, default=False, nullable=True)
    parent_consent_date = Column(Date, nullable=True)
    medical_clearance = Column(Boolean, default=False, nullable=True)
    emergency_contact_provided = Column(Boolean, default=False, nullable=True)

    # Withdrawal
    withdrawn_at = Column(Date, nullable=True)
    withdrawn_reason = Column(Text, nullable=True)

    # Relationships
    activity = relationship("Activity", back_populates="enrollments")
    student = relationship("Student", foreign_keys=[student_id])

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'waitlisted', 'withdrawn', 'completed')",
            name="chk_enrollments_status"
        ),
        CheckConstraint(
            "payment_status IN ('pending', 'partial', 'paid', 'waived')",
            name="chk_enrollments_payment_status"
        ),
        CheckConstraint(
            "amount_paid >= 0",
            name="chk_enrollments_amount_paid_positive"
        ),
        CheckConstraint(
            "attendance_count >= 0",
            name="chk_enrollments_attendance_count_positive"
        ),
        Index('idx_enrollments_activity_id', 'activity_id'),
        Index('idx_enrollments_student_id', 'student_id'),
        Index('idx_enrollments_status', 'status'),
        Index('idx_enrollments_payment_status', 'payment_status'),
        Index('idx_enrollments_enrollment_date', 'enrollment_date'),
    )

    def __repr__(self):
        return f"<ActivityEnrollment(id={self.id}, activity_id={self.activity_id}, student_id={self.student_id}, status={self.status})>"

    @property
    def attendance_percentage(self) -> float:
        """Calculate attendance percentage"""
        if not self.total_sessions or self.total_sessions == 0:
            return 0.0
        return (self.attendance_count / self.total_sessions) * 100

    @property
    def is_active(self) -> bool:
        """Check if enrollment is currently active"""
        return self.status == 'active'

    @property
    def payment_complete(self) -> bool:
        """Check if payment is complete"""
        return self.payment_status in ('paid', 'waived')

    def to_dict(self, include_relationships: bool = False):
        """Convert enrollment to dictionary"""
        data = super().to_dict()

        # Convert date objects to strings
        if self.enrollment_date:
            data['enrollment_date'] = self.enrollment_date.isoformat()
        if self.payment_date:
            data['payment_date'] = self.payment_date.isoformat()
        if self.parent_consent_date:
            data['parent_consent_date'] = self.parent_consent_date.isoformat()
        if self.withdrawn_at:
            data['withdrawn_at'] = self.withdrawn_at.isoformat()
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()

        # Convert decimal to float
        if self.amount_paid:
            data['amount_paid'] = float(self.amount_paid)

        # Add computed properties
        data['attendance_percentage'] = self.attendance_percentage
        data['is_active'] = self.is_active
        data['payment_complete'] = self.payment_complete

        # Convert arrays to lists
        if self.achievements:
            data['achievements'] = list(self.achievements)

        if include_relationships:
            try:
                if self.activity:
                    data["activity"] = {
                        "id": str(self.activity.id),
                        "name": self.activity.name,
                        "activity_type": self.activity.activity_type,
                        "cost": float(self.activity.cost or 0)
                    }
            except:
                pass

            try:
                if self.student:
                    data["student"] = {
                        "id": str(self.student.id),
                        "name": f"{self.student.user.first_name} {self.student.user.last_name}" if hasattr(self.student, 'user') else None,
                        "grade_level": self.student.grade_level if hasattr(self.student, 'grade_level') else None
                    }
            except:
                pass

        return data
