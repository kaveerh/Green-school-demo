"""
Merit Model

Positive behavior reinforcement and achievement recognition system.
"""

from sqlalchemy import Column, String, Integer, Date, Boolean, Text, CheckConstraint, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from models.base import BaseModel
from datetime import date as date_type
import uuid


class Merit(BaseModel):
    """Merit model for student achievement recognition and rewards"""
    __tablename__ = "merits"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    awarded_by_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(PG_UUID(as_uuid=True), ForeignKey("classes.id", ondelete="SET NULL"), nullable=True)
    subject_id = Column(PG_UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)

    # Merit Details
    category = Column(String(50), nullable=False)  # academic, behavior, participation, leadership, attendance, other
    points = Column(Integer, nullable=False)  # 1-10
    reason = Column(Text, nullable=False)  # Description of why merit was awarded

    # Context
    quarter = Column(String(10), nullable=True)  # Q1, Q2, Q3, Q4
    academic_year = Column(String(20), nullable=True)  # 2024-2025
    awarded_date = Column(Date, nullable=False, default=date_type.today)

    # Metadata
    is_class_award = Column(Boolean, default=False, nullable=False)
    batch_id = Column(PG_UUID(as_uuid=True), nullable=True)

    # Relationships
    school = relationship("School", foreign_keys=[school_id])
    student = relationship("Student", foreign_keys=[student_id])
    awarded_by = relationship("User", foreign_keys=[awarded_by_id])
    class_obj = relationship("Class", foreign_keys=[class_id])
    subject = relationship("Subject", foreign_keys=[subject_id])

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "category IN ('academic', 'behavior', 'participation', 'leadership', 'attendance', 'other')",
            name="chk_merits_category"
        ),
        CheckConstraint(
            "points >= 1 AND points <= 10",
            name="chk_merits_points"
        ),
        CheckConstraint(
            "quarter IS NULL OR quarter IN ('Q1', 'Q2', 'Q3', 'Q4')",
            name="chk_merits_quarter"
        ),
        Index('idx_merits_school_id', 'school_id'),
        Index('idx_merits_student_id', 'student_id'),
        Index('idx_merits_awarded_by_id', 'awarded_by_id'),
        Index('idx_merits_class_id', 'class_id'),
        Index('idx_merits_category', 'category'),
        Index('idx_merits_awarded_date', 'awarded_date'),
        Index('idx_merits_quarter', 'quarter'),
        Index('idx_merits_deleted_at', 'deleted_at'),
    )

    def __repr__(self):
        return f"<Merit(id={self.id}, student_id={self.student_id}, category={self.category}, points={self.points})>"

    @property
    def category_display(self) -> str:
        """Get formatted category name"""
        categories = {
            'academic': 'Academic Excellence',
            'behavior': 'Good Behavior',
            'participation': 'Class Participation',
            'leadership': 'Leadership',
            'attendance': 'Perfect Attendance',
            'other': 'Other Achievement'
        }
        return categories.get(self.category, self.category)

    @property
    def points_tier(self) -> str:
        """Get merit tier based on points"""
        if self.points <= 2:
            return 'bronze'
        elif self.points <= 5:
            return 'silver'
        elif self.points <= 8:
            return 'gold'
        else:
            return 'platinum'

    @property
    def is_recent(self) -> bool:
        """Check if merit was awarded in last 7 days"""
        if not self.awarded_date:
            return False
        days_ago = (date_type.today() - self.awarded_date).days
        return 0 <= days_ago <= 7

    def to_dict(self, include_relationships: bool = False):
        """Convert merit to dictionary"""
        data = super().to_dict()

        # Convert date objects to strings
        if self.awarded_date:
            data['awarded_date'] = self.awarded_date.isoformat()
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()

        # Add computed properties
        data['category_display'] = self.category_display
        data['points_tier'] = self.points_tier
        data['is_recent'] = self.is_recent

        if include_relationships:
            try:
                if self.student:
                    data["student"] = {
                        "id": str(self.student.id),
                        "name": f"{self.student.first_name} {self.student.last_name}",
                        "grade_level": self.student.grade_level
                    }
                if self.awarded_by:
                    data["awarded_by"] = {
                        "id": str(self.awarded_by.id),
                        "name": f"{self.awarded_by.first_name} {self.awarded_by.last_name}"
                    }
                if self.class_obj:
                    data["class"] = {
                        "id": str(self.class_obj.id),
                        "name": self.class_obj.name
                    }
                if self.subject:
                    data["subject"] = {
                        "id": str(self.subject.id),
                        "name": self.subject.name,
                        "code": self.subject.code
                    }
            except:
                pass

        return data
