"""
Subject ORM Model

Manages academic subjects/courses offered at the school.
Subjects are the foundation for classes, assessments, and lesson planning.
"""

from sqlalchemy import Column, String, Text, Integer, Numeric, Boolean, CheckConstraint, Index, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Subject(BaseModel):
    """
    Subject model representing academic subjects/courses.

    Core subjects: MATH, ELA, SCIENCE, SOCIAL_STUDIES, ART, PE
    Additional subjects: MUSIC, LIBRARY, TECHNOLOGY, FOREIGN_LANGUAGE, etc.
    """
    __tablename__ = "subjects"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)

    # Subject Information
    code = Column(String(50), nullable=False, index=True)  # e.g., "MATH", "ELA", "SCI"
    name = Column(String(200), nullable=False)  # e.g., "Mathematics"
    description = Column(Text, nullable=True)

    # Categorization
    category = Column(String(50), default="core", nullable=False)  # core, elective, enrichment, remedial, other
    subject_type = Column(String(50), nullable=True)  # academic, arts, physical, technical, other

    # Grade Levels (array of integers 1-7)
    grade_levels = Column(ARRAY(Integer), nullable=False, default=[1, 2, 3, 4, 5, 6, 7])

    # Display Properties
    color = Column(String(7), nullable=True)  # Hex color code (e.g., "#FF5733")
    icon = Column(String(50), nullable=True)  # Emoji or icon identifier
    display_order = Column(Integer, default=0, nullable=False)  # Sort order in UI

    # Academic Properties
    credits = Column(Numeric(4, 2), nullable=True)  # Credit hours (optional)
    is_required = Column(Boolean, default=True, nullable=False)  # Required vs elective

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    school = relationship("School", back_populates="subjects")
    # classes = relationship("Class", back_populates="subject")  # To be added when Class model exists
    # assessments = relationship("Assessment", back_populates="subject")  # Future
    # lessons = relationship("Lesson", back_populates="subject")  # Future

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "category IN ('core', 'elective', 'enrichment', 'remedial', 'other')",
            name="chk_subjects_category"
        ),
        CheckConstraint(
            "subject_type IS NULL OR subject_type IN ('academic', 'arts', 'physical', 'technical', 'other')",
            name="chk_subjects_type"
        ),
        CheckConstraint(
            "grade_levels <@ ARRAY[1,2,3,4,5,6,7]",
            name="chk_subjects_grade_levels"
        ),
        CheckConstraint(
            "credits IS NULL OR credits >= 0",
            name="chk_subjects_credits"
        ),
        CheckConstraint(
            "color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'",
            name="chk_subjects_color_format"
        ),
        Index('idx_subjects_school_id', 'school_id'),
        Index('idx_subjects_school_code', 'school_id', 'code', unique=True),
        Index('idx_subjects_category', 'category'),
        Index('idx_subjects_active', 'is_active'),
        Index('idx_subjects_deleted', 'deleted_at'),
        Index('idx_subjects_grade_levels', 'grade_levels', postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<Subject(id={self.id}, code={self.code}, name={self.name})>"

    def is_available(self) -> bool:
        """Check if subject is available (active and not deleted)."""
        return self.is_active and not self.is_deleted()

    def teaches_grade(self, grade: int) -> bool:
        """Check if this subject is taught at a specific grade level."""
        return grade in (self.grade_levels or [])

    def is_core_subject(self) -> bool:
        """Check if this is a core/required subject."""
        return self.category == "core" and self.is_required

    def get_grade_range(self) -> str:
        """Get formatted grade range string (e.g., '1-7', '3-5')."""
        if not self.grade_levels:
            return ""

        sorted_grades = sorted(self.grade_levels)

        if len(sorted_grades) == 1:
            return str(sorted_grades[0])

        # Check if consecutive
        if sorted_grades == list(range(sorted_grades[0], sorted_grades[-1] + 1)):
            return f"{sorted_grades[0]}-{sorted_grades[-1]}"

        # Non-consecutive, return comma-separated
        return ", ".join(map(str, sorted_grades))

    def to_dict(self, include_relationships=False):
        """Convert subject to dictionary representation."""
        data = {
            "id": str(self.id),
            "school_id": str(self.school_id),
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "subject_type": self.subject_type,
            "grade_levels": self.grade_levels or [],
            "color": self.color,
            "icon": self.icon,
            "display_order": self.display_order,
            "credits": float(self.credits) if self.credits else None,
            "is_required": self.is_required,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        # Add computed fields
        data["is_available"] = self.is_available()
        data["is_core"] = self.is_core_subject()
        data["grade_range"] = self.get_grade_range()

        if include_relationships:
            if self.school:
                data["school"] = {
                    "id": str(self.school.id),
                    "name": self.school.name,
                }

        return data
