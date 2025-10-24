"""
Student Model
Student profiles with grade levels, parent relationships, and academic tracking
"""
from sqlalchemy import Column, String, Date, Integer, Boolean, CheckConstraint, Index, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from models.base import BaseModel
from datetime import date
import uuid


class Student(BaseModel):
    """Student model for managing student profiles and academic records"""
    __tablename__ = "students"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Student-specific fields
    student_id = Column(String(50), nullable=False)
    grade_level = Column(Integer, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=True)
    enrollment_date = Column(Date, nullable=False)
    graduation_date = Column(Date, nullable=True)

    # Medical and emergency information
    allergies = Column(Text, nullable=True)
    medical_notes = Column(Text, nullable=True)
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relation = Column(String(50), nullable=True)

    # Additional information
    photo_url = Column(String(500), nullable=True)
    status = Column(String(20), default="enrolled", nullable=True, index=True)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    school = relationship("School", back_populates="students")
    parent_relationships = relationship("ParentStudentRelationship", back_populates="student")
    assessments = relationship("Assessment", back_populates="student")
    # classes = relationship("ClassEnrollment", back_populates="student")
    # attendance = relationship("Attendance", back_populates="student")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "grade_level BETWEEN 1 AND 7",
            name="chk_students_grade_level"
        ),
        CheckConstraint(
            "status IN ('enrolled', 'graduated', 'transferred', 'withdrawn', 'suspended')",
            name="chk_students_status"
        ),
        CheckConstraint(
            "gender IS NULL OR gender IN ('male', 'female', 'other', 'prefer_not_to_say')",
            name="chk_students_gender"
        ),
        CheckConstraint(
            "date_of_birth < enrollment_date",
            name="chk_students_dob_before_enrollment"
        ),
        Index('idx_students_school_id', 'school_id'),
        Index('idx_students_user_id', 'user_id'),
        Index('idx_students_student_id', 'school_id', 'student_id', unique=True),
        Index('idx_students_grade_level', 'grade_level'),
        Index('idx_students_status', 'status'),
        Index('idx_students_deleted_at', 'deleted_at'),
    )

    def __repr__(self):
        return f"<Student(id={self.id}, student_id={self.student_id}, grade={self.grade_level})>"

    @property
    def is_currently_enrolled(self) -> bool:
        """Check if student is currently enrolled"""
        return (
            self.status == "enrolled" and
            not self.is_deleted() and
            (self.graduation_date is None or self.graduation_date > date.today())
        )

    @property
    def age(self) -> int:
        """Calculate student's current age"""
        if not self.date_of_birth:
            return 0
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def years_enrolled(self) -> int:
        """Calculate years since enrollment"""
        if not self.enrollment_date:
            return 0
        end_date = self.graduation_date or date.today()
        return (end_date - self.enrollment_date).days // 365

    @property
    def can_promote(self) -> bool:
        """Check if student can be promoted to next grade"""
        return (
            self.is_currently_enrolled and
            self.grade_level < 7 and
            self.status == "enrolled"
        )

    def promote_to_next_grade(self) -> int:
        """Promote student to next grade level"""
        if not self.can_promote:
            raise ValueError("Student cannot be promoted")
        self.grade_level += 1
        if self.grade_level == 7:
            # Mark as ready for graduation if promoted to grade 7
            pass
        return self.grade_level

    def to_dict(self, include_sensitive: bool = False):
        """
        Convert student to dictionary

        Args:
            include_sensitive: Include medical and emergency contact information
        """
        data = super().to_dict()

        # Remove sensitive fields unless explicitly requested
        if not include_sensitive:
            data.pop('allergies', None)
            data.pop('medical_notes', None)
            data.pop('emergency_contact_name', None)
            data.pop('emergency_contact_phone', None)
            data.pop('emergency_contact_relation', None)
            data.pop('deleted_by', None)

        # Add computed fields
        data['is_currently_enrolled'] = self.is_currently_enrolled
        data['age'] = self.age
        data['years_enrolled'] = self.years_enrolled
        data['can_promote'] = self.can_promote

        return data


class ParentStudentRelationship(BaseModel):
    """Model for managing parent-student relationships"""
    __tablename__ = "parent_student_relationships"

    # Foreign Keys
    parent_id = Column(PG_UUID(as_uuid=True), ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)

    # Relationship details
    relationship_type = Column(String(50), nullable=False)
    is_primary_contact = Column(Boolean, default=False, nullable=True)
    has_pickup_permission = Column(Boolean, default=True, nullable=True)

    # Relationships
    parent = relationship("Parent", foreign_keys=[parent_id], back_populates="student_relationships")
    student = relationship("Student", foreign_keys=[student_id], back_populates="parent_relationships")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "relationship_type IN ('mother', 'father', 'guardian', 'stepmother', 'stepfather', 'grandparent', 'foster_parent', 'other')",
            name="chk_parent_student_relationship_type"
        ),
        Index('idx_parent_student_parent_id', 'parent_id'),
        Index('idx_parent_student_student_id', 'student_id'),
        Index('idx_parent_student_unique', 'parent_id', 'student_id', unique=True),
        Index('idx_parent_student_primary', 'student_id', 'is_primary_contact'),
        Index('idx_parent_student_deleted_at', 'deleted_at'),
    )

    def __repr__(self):
        return f"<ParentStudentRelationship(parent_id={self.parent_id}, student_id={self.student_id}, type={self.relationship_type})>"

    def to_dict(self):
        """Convert relationship to dictionary"""
        data = super().to_dict()
        return data
