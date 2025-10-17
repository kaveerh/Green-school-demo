"""
Teacher Model
Teacher profiles with employment details and teaching assignments
"""
from sqlalchemy import Column, String, Date, Integer, Boolean, Numeric, ForeignKey, CheckConstraint, Index, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from models.base import BaseModel
from datetime import date
import uuid


class Teacher(BaseModel):
    """Teacher model for managing teacher profiles and assignments"""
    __tablename__ = "teachers"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Teacher-specific fields
    employee_id = Column(String(50), nullable=False)
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date, nullable=True)
    department = Column(String(100), nullable=True)
    job_title = Column(String(100), default="Teacher", nullable=True)

    # Teaching credentials
    certification_number = Column(String(100), nullable=True)
    certification_expiry = Column(Date, nullable=True)
    education_level = Column(String(50), nullable=True)
    university = Column(String(200), nullable=True)

    # Teaching assignments
    grade_levels = Column(ARRAY(Integer), nullable=False, default=[])
    specializations = Column(ARRAY(Text), default=[])

    # Employment details
    employment_type = Column(String(20), default="full-time", nullable=True)
    salary = Column(Numeric(10, 2), nullable=True)
    work_hours_per_week = Column(Integer, default=40, nullable=True)

    # Contact and emergency
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(50), nullable=True)

    # Status
    status = Column(String(20), default="active", nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=True)

    # Metadata and settings
    bio = Column(Text, nullable=True)
    office_room = Column(String(50), nullable=True)
    office_hours = Column(JSONB, default={}, nullable=True, server_default='{}')
    preferences = Column(JSONB, default={}, nullable=True, server_default='{}')

    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    school = relationship("School", back_populates="teachers")
    # classes = relationship("Class", back_populates="teacher")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'on_leave', 'terminated')",
            name="chk_teachers_status"
        ),
        CheckConstraint(
            "employment_type IN ('full-time', 'part-time', 'contract', 'substitute')",
            name="chk_teachers_employment_type"
        ),
        CheckConstraint(
            "grade_levels <@ ARRAY[1,2,3,4,5,6,7]",
            name="chk_teachers_grade_levels"
        ),
        CheckConstraint(
            "education_level IS NULL OR education_level IN ('High School', 'Associate', 'Bachelor''s', 'Master''s', 'PhD', 'Other')",
            name="chk_teachers_education_level"
        ),
        CheckConstraint(
            "salary IS NULL OR salary >= 0",
            name="chk_teachers_salary"
        ),
        CheckConstraint(
            "work_hours_per_week IS NULL OR work_hours_per_week > 0",
            name="chk_teachers_work_hours"
        ),
        Index('idx_teachers_school_id', 'school_id'),
        Index('idx_teachers_user_id', 'user_id'),
        Index('idx_teachers_employee_id', 'school_id', 'employee_id'),
        Index('idx_teachers_status', 'status'),
        Index('idx_teachers_employment_type', 'employment_type'),
        Index('idx_teachers_deleted_at', 'deleted_at'),
        Index('idx_teachers_grade_levels', 'grade_levels', postgresql_using='gin'),
        Index('idx_teachers_specializations', 'specializations', postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<Teacher(id={self.id}, employee_id={self.employee_id}, user_id={self.user_id})>"

    def is_currently_employed(self) -> bool:
        """Check if teacher is currently employed"""
        return (
            self.status == "active" and
            self.is_active and
            not self.is_deleted() and
            (self.termination_date is None or self.termination_date > date.today())
        )

    def is_full_time(self) -> bool:
        """Check if teacher is full-time"""
        return self.employment_type == "full-time"

    def teaches_grade(self, grade: int) -> bool:
        """Check if teacher teaches a specific grade"""
        return grade in (self.grade_levels or [])

    def has_specialization(self, specialization: str) -> bool:
        """Check if teacher has a specific specialization"""
        return specialization.lower() in [s.lower() for s in (self.specializations or [])]

    def years_of_service(self) -> int:
        """Calculate years of service"""
        if not self.hire_date:
            return 0
        end_date = self.termination_date or date.today()
        return (end_date - self.hire_date).days // 365

    def is_certification_valid(self) -> bool:
        """Check if certification is still valid"""
        if not self.certification_expiry:
            return False
        return self.certification_expiry > date.today()

    def to_dict(self, include_sensitive: bool = False):
        """
        Convert teacher to dictionary

        Args:
            include_sensitive: Include salary and other sensitive fields
        """
        data = super().to_dict()

        # Remove sensitive fields unless explicitly requested
        if not include_sensitive:
            data.pop('salary', None)
            data.pop('emergency_contact_name', None)
            data.pop('emergency_contact_phone', None)
            data.pop('emergency_contact_relationship', None)
            data.pop('deleted_by', None)

        # Add computed fields
        data['is_currently_employed'] = self.is_currently_employed()
        data['years_of_service'] = self.years_of_service()
        data['is_certification_valid'] = self.is_certification_valid()
        data['is_full_time'] = self.is_full_time()

        return data
