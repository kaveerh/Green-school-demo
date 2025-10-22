"""
Lesson ORM Model

Lesson model for lesson planning and curriculum management.
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, Date, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from typing import Optional, Dict, Any, List
from datetime import date, datetime
import uuid

from .base import BaseModel


class Lesson(BaseModel):
    """Lesson model for lesson planning"""

    __tablename__ = "lessons"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(PG_UUID(as_uuid=True), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id = Column(PG_UUID(as_uuid=True), ForeignKey("teachers.id", ondelete="RESTRICT"), nullable=False, index=True)
    subject_id = Column(PG_UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Identification
    title = Column(String(200), nullable=False)
    lesson_number = Column(Integer, nullable=False)

    # Scheduling
    scheduled_date = Column(Date, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False, default=45)

    # Content
    description = Column(Text, nullable=True)
    learning_objectives = Column(ARRAY(Text), default=list, server_default='{}')
    materials_needed = Column(ARRAY(Text), default=list, server_default='{}')
    curriculum_standards = Column(ARRAY(Text), default=list, server_default='{}')

    # Lesson Plan
    introduction = Column(Text, nullable=True)
    main_activity = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    homework = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Resources
    attachments = Column(JSONB, default=list, server_default='[]')
    links = Column(ARRAY(Text), default=list, server_default='{}')

    # Status & Progress
    status = Column(String(20), nullable=False, default='draft', index=True)
    completion_percentage = Column(Integer, default=0)
    actual_duration_minutes = Column(Integer, nullable=True)

    # Reflection
    reflection = Column(Text, nullable=True)
    what_went_well = Column(Text, nullable=True)
    what_to_improve = Column(Text, nullable=True)
    modifications_needed = Column(Text, nullable=True)

    # Display
    color = Column(String(7), nullable=True)
    is_template = Column(Boolean, default=False, index=True)
    template_id = Column(PG_UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    school = relationship("School", back_populates="lessons")
    class_obj = relationship("Class")
    teacher = relationship("Teacher")
    subject = relationship("Subject")
    template = relationship("Lesson", remote_side="Lesson.id", foreign_keys=[template_id])

    # Constraints
    __table_args__ = (
        UniqueConstraint('class_id', 'lesson_number', 'deleted_at', name='uq_lessons_number_class'),
        CheckConstraint(
            "status IN ('draft', 'scheduled', 'in_progress', 'completed', 'cancelled')",
            name='chk_lessons_status'
        ),
        CheckConstraint('lesson_number > 0', name='chk_lessons_number_positive'),
        CheckConstraint('duration_minutes > 0', name='chk_lessons_duration_positive'),
        CheckConstraint(
            'completion_percentage >= 0 AND completion_percentage <= 100',
            name='chk_lessons_completion_percentage'
        ),
        {'extend_existing': True}
    )

    def __repr__(self) -> str:
        return f"<Lesson {self.title} - Lesson #{self.lesson_number} - {self.scheduled_date}>"

    def to_dict(self) -> dict:
        """Convert lesson to dictionary with computed fields"""
        base_dict = super().to_dict()

        # Add relationship data only if already loaded (avoid lazy loading)
        try:
            if self.class_obj:
                base_dict['class_name'] = self.class_obj.name
                base_dict['class_code'] = self.class_obj.code
        except:
            pass

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

        # Add computed fields
        base_dict['is_past_due'] = self.is_past_due()
        base_dict['is_upcoming'] = self.is_upcoming()
        base_dict['is_completed'] = self.is_completed()
        base_dict['duration_display'] = self.get_duration_display()

        return base_dict

    def is_completed(self) -> bool:
        """Check if lesson is completed"""
        return self.status == 'completed'

    def is_past_due(self) -> bool:
        """Check if lesson is past its scheduled date"""
        if not self.scheduled_date:
            return False
        return self.scheduled_date < date.today() and self.status not in ['completed', 'cancelled']

    def is_upcoming(self) -> bool:
        """Check if lesson is upcoming (within next 7 days)"""
        if not self.scheduled_date:
            return False
        days_until = (self.scheduled_date - date.today()).days
        return 0 <= days_until <= 7 and self.status in ['draft', 'scheduled']

    def can_start(self) -> bool:
        """Check if lesson can be started"""
        return self.status in ['draft', 'scheduled'] and not self.is_past_due()

    def can_complete(self) -> bool:
        """Check if lesson can be completed"""
        return self.status in ['scheduled', 'in_progress']

    def can_cancel(self) -> bool:
        """Check if lesson can be cancelled"""
        return self.status in ['draft', 'scheduled', 'in_progress']

    def start(self) -> None:
        """Start the lesson (set to in_progress)"""
        if self.can_start():
            self.status = 'in_progress'

    def complete(
        self,
        completion_percentage: int = 100,
        actual_duration_minutes: Optional[int] = None,
        reflection: Optional[str] = None,
        what_went_well: Optional[str] = None,
        what_to_improve: Optional[str] = None,
        modifications_needed: Optional[str] = None
    ) -> None:
        """Complete the lesson"""
        if self.can_complete():
            self.status = 'completed'
            self.completion_percentage = completion_percentage
            if actual_duration_minutes:
                self.actual_duration_minutes = actual_duration_minutes
            if reflection:
                self.reflection = reflection
            if what_went_well:
                self.what_went_well = what_went_well
            if what_to_improve:
                self.what_to_improve = what_to_improve
            if modifications_needed:
                self.modifications_needed = modifications_needed

    def cancel(self) -> None:
        """Cancel the lesson"""
        if self.can_cancel():
            self.status = 'cancelled'

    def get_duration_display(self) -> str:
        """Get formatted duration string"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60

        if hours > 0:
            if minutes > 0:
                return f"{hours}h {minutes}m"
            return f"{hours}h"
        return f"{minutes}m"

    def get_actual_duration_display(self) -> Optional[str]:
        """Get formatted actual duration string"""
        if not self.actual_duration_minutes:
            return None

        hours = self.actual_duration_minutes // 60
        minutes = self.actual_duration_minutes % 60

        if hours > 0:
            if minutes > 0:
                return f"{hours}h {minutes}m"
            return f"{hours}h"
        return f"{minutes}m"

    def has_attachments(self) -> bool:
        """Check if lesson has attachments"""
        return bool(self.attachments and len(self.attachments) > 0)

    def has_links(self) -> bool:
        """Check if lesson has resource links"""
        return bool(self.links and len(self.links) > 0)

    def has_learning_objectives(self) -> bool:
        """Check if lesson has learning objectives"""
        return bool(self.learning_objectives and len(self.learning_objectives) > 0)

    def has_materials(self) -> bool:
        """Check if lesson has materials needed"""
        return bool(self.materials_needed and len(self.materials_needed) > 0)

    def has_curriculum_standards(self) -> bool:
        """Check if lesson has curriculum standards"""
        return bool(self.curriculum_standards and len(self.curriculum_standards) > 0)

    def has_lesson_plan(self) -> bool:
        """Check if lesson has a complete lesson plan"""
        return bool(
            self.introduction or
            self.main_activity or
            self.assessment or
            self.homework
        )

    def has_reflection(self) -> bool:
        """Check if lesson has reflection"""
        return bool(
            self.reflection or
            self.what_went_well or
            self.what_to_improve or
            self.modifications_needed
        )

    def get_completion_status_display(self) -> str:
        """Get human-readable completion status"""
        if self.status == 'completed':
            return f"Completed ({self.completion_percentage}%)"
        elif self.status == 'in_progress':
            return f"In Progress ({self.completion_percentage}%)"
        elif self.status == 'cancelled':
            return "Cancelled"
        elif self.status == 'scheduled':
            return "Scheduled"
        else:
            return "Draft"

    def get_status_color(self) -> str:
        """Get color code for status"""
        status_colors = {
            'draft': '#9E9E9E',
            'scheduled': '#2196F3',
            'in_progress': '#FF9800',
            'completed': '#4CAF50',
            'cancelled': '#F44336'
        }
        return status_colors.get(self.status, '#9E9E9E')

    def clone_as_template(self) -> Dict[str, Any]:
        """Clone lesson data for creating from template"""
        return {
            'title': self.title,
            'description': self.description,
            'learning_objectives': self.learning_objectives.copy() if self.learning_objectives else [],
            'materials_needed': self.materials_needed.copy() if self.materials_needed else [],
            'curriculum_standards': self.curriculum_standards.copy() if self.curriculum_standards else [],
            'introduction': self.introduction,
            'main_activity': self.main_activity,
            'assessment': self.assessment,
            'homework': self.homework,
            'notes': self.notes,
            'links': self.links.copy() if self.links else [],
            'duration_minutes': self.duration_minutes,
            'color': self.color,
            'template_id': self.id if self.is_template else None
        }

    def add_attachment(self, attachment: Dict[str, Any]) -> None:
        """Add an attachment to the lesson"""
        if not self.attachments:
            self.attachments = []
        self.attachments.append(attachment)

    def remove_attachment(self, attachment_id: str) -> bool:
        """Remove an attachment by ID"""
        if not self.attachments:
            return False

        original_length = len(self.attachments)
        self.attachments = [a for a in self.attachments if a.get('id') != attachment_id]
        return len(self.attachments) < original_length

    def add_link(self, link: str) -> None:
        """Add a resource link"""
        if not self.links:
            self.links = []
        if link not in self.links:
            self.links.append(link)

    def remove_link(self, link: str) -> bool:
        """Remove a resource link"""
        if not self.links or link not in self.links:
            return False
        self.links.remove(link)
        return True

    def add_learning_objective(self, objective: str) -> None:
        """Add a learning objective"""
        if not self.learning_objectives:
            self.learning_objectives = []
        if objective not in self.learning_objectives:
            self.learning_objectives.append(objective)

    def remove_learning_objective(self, objective: str) -> bool:
        """Remove a learning objective"""
        if not self.learning_objectives or objective not in self.learning_objectives:
            return False
        self.learning_objectives.remove(objective)
        return True

    def add_material(self, material: str) -> None:
        """Add a material needed"""
        if not self.materials_needed:
            self.materials_needed = []
        if material not in self.materials_needed:
            self.materials_needed.append(material)

    def remove_material(self, material: str) -> bool:
        """Remove a material"""
        if not self.materials_needed or material not in self.materials_needed:
            return False
        self.materials_needed.remove(material)
        return True

    def add_curriculum_standard(self, standard: str) -> None:
        """Add a curriculum standard"""
        if not self.curriculum_standards:
            self.curriculum_standards = []
        if standard not in self.curriculum_standards:
            self.curriculum_standards.append(standard)

    def remove_curriculum_standard(self, standard: str) -> bool:
        """Remove a curriculum standard"""
        if not self.curriculum_standards or standard not in self.curriculum_standards:
            return False
        self.curriculum_standards.remove(standard)
        return True
