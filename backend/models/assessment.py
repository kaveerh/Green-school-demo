"""
Assessment Model

Student assessments with grades, scores, and teacher feedback.
Supports various assessment types (tests, quizzes, projects, etc.) organized by academic quarters.
"""

from sqlalchemy import Column, String, Date, Numeric, Boolean, Text, CheckConstraint, Index, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from models.base import BaseModel
from datetime import date
from decimal import Decimal
import uuid


class Assessment(BaseModel):
    """Assessment model for tracking student evaluations and grades"""
    __tablename__ = "assessments"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(PG_UUID(as_uuid=True), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(PG_UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(PG_UUID(as_uuid=True), ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)

    # Assessment Details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    assessment_type = Column(String(50), nullable=False)  # test, quiz, project, assignment, exam, etc.
    quarter = Column(String(2), nullable=False)  # Q1, Q2, Q3, Q4
    assessment_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)

    # Grading
    total_points = Column(Numeric(10, 2), nullable=False)
    points_earned = Column(Numeric(10, 2), nullable=True)
    percentage = Column(Numeric(5, 2), nullable=True)  # Computed: (points_earned / total_points) * 100
    letter_grade = Column(String(2), nullable=True)  # A+, A, A-, B+, B, etc.

    # Status and Feedback
    status = Column(String(20), default="pending", nullable=True)  # pending, graded, returned, late, etc.
    feedback = Column(Text, nullable=True)
    graded_at = Column(TIMESTAMP(timezone=True), nullable=True)
    returned_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Metadata
    weight = Column(Numeric(5, 2), default=1.0, nullable=True)  # Weight in final grade
    is_extra_credit = Column(Boolean, default=False, nullable=True)
    is_makeup = Column(Boolean, default=False, nullable=True)

    # Relationships
    school = relationship("School", back_populates="assessments")
    student = relationship("Student", back_populates="assessments")
    class_obj = relationship("Class", foreign_keys=[class_id], back_populates="assessments")
    subject = relationship("Subject", back_populates="assessments")
    teacher = relationship("Teacher", back_populates="assessments")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "quarter IN ('Q1', 'Q2', 'Q3', 'Q4')",
            name="chk_assessments_quarter"
        ),
        CheckConstraint(
            "assessment_type IN ('test', 'quiz', 'project', 'assignment', 'exam', 'presentation', 'homework', 'lab', 'other')",
            name="chk_assessments_type"
        ),
        CheckConstraint(
            "status IN ('pending', 'submitted', 'graded', 'returned', 'late', 'missing', 'excused')",
            name="chk_assessments_status"
        ),
        CheckConstraint(
            "letter_grade IS NULL OR letter_grade IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F')",
            name="chk_assessments_letter_grade"
        ),
        CheckConstraint("total_points > 0", name="chk_assessments_total_points"),
        CheckConstraint("points_earned IS NULL OR points_earned >= 0", name="chk_assessments_points_earned"),
        CheckConstraint("percentage IS NULL OR (percentage >= 0 AND percentage <= 100)", name="chk_assessments_percentage"),
        CheckConstraint("weight >= 0 AND weight <= 10", name="chk_assessments_weight"),
        Index('idx_assessments_school_id', 'school_id'),
        Index('idx_assessments_student_id', 'student_id'),
        Index('idx_assessments_class_id', 'class_id'),
        Index('idx_assessments_subject_id', 'subject_id'),
        Index('idx_assessments_teacher_id', 'teacher_id'),
        Index('idx_assessments_quarter', 'quarter'),
        Index('idx_assessments_type', 'assessment_type'),
        Index('idx_assessments_status', 'status'),
        Index('idx_assessments_assessment_date', 'assessment_date'),
        Index('idx_assessments_deleted_at', 'deleted_at'),
        Index('idx_assessments_student_quarter', 'student_id', 'quarter'),
        Index('idx_assessments_class_quarter', 'class_id', 'quarter'),
    )

    def __repr__(self):
        return f"<Assessment(id={self.id}, title={self.title}, student_id={self.student_id}, type={self.assessment_type})>"

    @property
    def is_graded(self) -> bool:
        """Check if assessment has been graded"""
        return self.status in ('graded', 'returned') and self.points_earned is not None

    @property
    def is_passing(self) -> bool:
        """Check if student passed (>= 60%)"""
        if not self.percentage:
            return False
        return float(self.percentage) >= 60.0

    @property
    def is_overdue(self) -> bool:
        """Check if assessment is overdue"""
        if not self.due_date or self.status in ('graded', 'returned', 'excused'):
            return False
        return self.due_date < date.today()

    @property
    def grade_display(self) -> str:
        """Display grade as letter (preferred) or percentage"""
        if self.letter_grade:
            return self.letter_grade
        if self.percentage:
            return f"{float(self.percentage):.1f}%"
        return "Not Graded"

    def calculate_percentage(self):
        """Calculate percentage from points earned and total points"""
        if self.points_earned is not None and self.total_points > 0:
            self.percentage = Decimal((float(self.points_earned) / float(self.total_points)) * 100)
            return self.percentage
        return None

    def assign_letter_grade(self, percentage: float = None) -> str:
        """Assign letter grade based on percentage"""
        pct = percentage if percentage is not None else (float(self.percentage) if self.percentage else None)

        if pct is None:
            return None

        if pct >= 97:
            return "A+"
        elif pct >= 93:
            return "A"
        elif pct >= 90:
            return "A-"
        elif pct >= 87:
            return "B+"
        elif pct >= 83:
            return "B"
        elif pct >= 80:
            return "B-"
        elif pct >= 77:
            return "C+"
        elif pct >= 73:
            return "C"
        elif pct >= 70:
            return "C-"
        elif pct >= 67:
            return "D+"
        elif pct >= 63:
            return "D"
        elif pct >= 60:
            return "D-"
        else:
            return "F"

    def to_dict(self, include_relationships: bool = False):
        """Convert assessment to dictionary"""
        data = super().to_dict()

        # Convert Decimal to float for JSON serialization
        if self.total_points:
            data['total_points'] = float(self.total_points)
        if self.points_earned:
            data['points_earned'] = float(self.points_earned)
        if self.percentage:
            data['percentage'] = float(self.percentage)
        if self.weight:
            data['weight'] = float(self.weight)

        # Add computed properties
        data['is_graded'] = self.is_graded
        data['is_passing'] = self.is_passing
        data['is_overdue'] = self.is_overdue
        data['grade_display'] = self.grade_display

        if include_relationships:
            # Only include relationships if already loaded (avoid lazy loading)
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
                if self.teacher and self.teacher.user:
                    data["teacher"] = {
                        "id": str(self.teacher.id),
                        "name": f"{self.teacher.user.first_name} {self.teacher.user.last_name}"
                    }
            except:
                pass

            try:
                if self.subject:
                    data["subject"] = {
                        "id": str(self.subject.id),
                        "name": self.subject.name,
                        "code": self.subject.code
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

        return data
