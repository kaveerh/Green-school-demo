"""
User Model
User entity with multi-persona support and Keycloak integration
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from models.base import BaseModel
import uuid


class User(BaseModel):
    """User model supporting multiple personas"""
    __tablename__ = "users"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)

    # Basic Information
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # NULL if using SSO only
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    # Role & Status
    persona = Column(
        String(50),
        nullable=False,
        index=True
    )
    status = Column(
        String(20),
        nullable=False,
        default="active",
        index=True
    )

    # Contact & Profile
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Authentication
    email_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    keycloak_id = Column(String(255), unique=True, nullable=True, index=True)

    # Additional Data
    user_metadata = Column('metadata', JSONB, default={}, nullable=False, server_default='{}')

    # Relationships
    school = relationship("School", back_populates="users")
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False)
    student_profile = relationship("Student", back_populates="user", uselist=False)
    parent_profile = relationship("Parent", back_populates="user", uselist=False)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "persona IN ('administrator', 'teacher', 'student', 'parent', 'vendor')",
            name="check_persona_valid"
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended')",
            name="check_status_valid"
        ),
        Index('idx_users_school_id', 'school_id'),
        Index('idx_users_email', 'email'),
        Index('idx_users_persona', 'persona'),
        Index('idx_users_status', 'status'),
        Index('idx_users_keycloak_id', 'keycloak_id'),
        Index('idx_users_deleted_at', 'deleted_at'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, persona={self.persona})>"

    def get_full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"

    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == "active" and not self.is_deleted()

    def is_admin(self) -> bool:
        """Check if user is an administrator"""
        return self.persona == "administrator"

    def is_teacher(self) -> bool:
        """Check if user is a teacher"""
        return self.persona == "teacher"

    def is_student(self) -> bool:
        """Check if user is a student"""
        return self.persona == "student"

    def is_parent(self) -> bool:
        """Check if user is a parent"""
        return self.persona == "parent"

    def is_vendor(self) -> bool:
        """Check if user is a vendor"""
        return self.persona == "vendor"

    def can_access_school(self, school_id: uuid.UUID) -> bool:
        """Check if user can access a specific school"""
        return self.school_id == school_id

    def to_dict(self, include_sensitive: bool = False):
        """
        Convert user to dictionary

        Args:
            include_sensitive: Include password_hash and other sensitive fields
        """
        data = super().to_dict()

        # Remove sensitive fields unless explicitly requested
        if not include_sensitive:
            data.pop('password_hash', None)
            data.pop('deleted_by', None)

        # Add computed fields
        data['full_name'] = self.get_full_name()
        data['is_active'] = self.is_active()

        return data
