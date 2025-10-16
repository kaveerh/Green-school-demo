"""
Parent ORM Model

Manages parent/guardian accounts and their relationships with students.
Supports multiple parents per student and multiple students per parent.
"""

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import uuid


class Parent(BaseModel):
    """
    Parent model representing a parent or guardian account.

    Links to a User with 'parent' persona and can be associated with multiple students.
    Tracks contact preferences, emergency contact status, and pickup authorization.
    """
    __tablename__ = "parents"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Employment Information
    occupation = Column(String(100), nullable=True)
    workplace = Column(String(200), nullable=True)

    # Contact Information
    phone_mobile = Column(String(20), nullable=True)
    phone_work = Column(String(20), nullable=True)
    preferred_contact_method = Column(String(20), nullable=True)  # email, phone, sms, app_notification

    # Flags and Preferences
    emergency_contact = Column(Boolean, default=False, nullable=False)
    pickup_authorized = Column(Boolean, default=False, nullable=False)
    receives_newsletter = Column(Boolean, default=True, nullable=False)

    # Relationships
    school = relationship("School", back_populates="parents")
    user = relationship("User", back_populates="parent_profile")

    # Many-to-many with students through parent_student_relationships
    # Note: This relationship is defined in student.py as ParentStudentRelationship
    student_relationships = relationship(
        "ParentStudentRelationship",
        back_populates="parent",
        foreign_keys="ParentStudentRelationship.parent_id",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Parent(id={self.id}, user_id={self.user_id}, school_id={self.school_id})>"

    def to_dict(self, include_relationships=False):
        """Convert parent to dictionary representation."""
        data = {
            "id": str(self.id),
            "school_id": str(self.school_id),
            "user_id": str(self.user_id),
            "occupation": self.occupation,
            "workplace": self.workplace,
            "phone_mobile": self.phone_mobile,
            "phone_work": self.phone_work,
            "preferred_contact_method": self.preferred_contact_method,
            "emergency_contact": self.emergency_contact,
            "pickup_authorized": self.pickup_authorized,
            "receives_newsletter": self.receives_newsletter,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_relationships:
            if self.user:
                data["user"] = {
                    "id": str(self.user.id),
                    "email": self.user.email,
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                    "persona": self.user.persona,
                }

            if self.student_relationships:
                data["children"] = [
                    {
                        "student_id": str(rel.student_id),
                        "relationship_type": rel.relationship_type,
                        "is_primary_contact": rel.is_primary_contact,
                        "has_legal_custody": rel.has_legal_custody,
                        "has_pickup_permission": rel.has_pickup_permission,
                        "student": {
                            "id": str(rel.student.id),
                            "student_id": rel.student.student_id,
                            "grade_level": rel.student.grade_level,
                            "user": {
                                "first_name": rel.student.user.first_name,
                                "last_name": rel.student.user.last_name,
                            } if rel.student.user else None
                        } if rel.student else None
                    }
                    for rel in self.student_relationships
                    if rel.deleted_at is None
                ]

        return data

    def has_custody_of(self, student_id: uuid.UUID) -> bool:
        """Check if parent has legal custody of a student."""
        for rel in self.student_relationships:
            if rel.student_id == student_id and rel.has_legal_custody and rel.deleted_at is None:
                return True
        return False

    def can_pickup(self, student_id: uuid.UUID) -> bool:
        """Check if parent is authorized to pick up a student."""
        for rel in self.student_relationships:
            if rel.student_id == student_id and rel.has_pickup_permission and rel.deleted_at is None:
                return True
        return False

    def is_primary_for(self, student_id: uuid.UUID) -> bool:
        """Check if parent is primary contact for a student."""
        for rel in self.student_relationships:
            if rel.student_id == student_id and rel.is_primary_contact and rel.deleted_at is None:
                return True
        return False

    def get_children_count(self) -> int:
        """Get count of active child relationships."""
        return sum(1 for rel in self.student_relationships if rel.deleted_at is None)

    def get_children(self):
        """Get list of active children (students)."""
        return [
            rel.student
            for rel in self.student_relationships
            if rel.deleted_at is None and rel.student and rel.student.deleted_at is None
        ]
