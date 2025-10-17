"""
School Model
School entity for multi-tenant architecture
"""
from sqlalchemy import Column, String, Boolean, Index, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from models.base import BaseModel


class School(BaseModel):
    """School model for multi-tenant support"""
    __tablename__ = "schools"

    # Basic Information
    name = Column(String(255), unique=True, nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)

    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="USA", nullable=False)

    # Contact
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    website_url = Column(String(500), nullable=True)

    # Social Media
    facebook_url = Column(String(500), nullable=True)
    twitter_url = Column(String(500), nullable=True)
    instagram_url = Column(String(500), nullable=True)

    # Branding
    logo_url = Column(String(500), nullable=True)

    # Leadership
    principal_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    hod_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Localization
    timezone = Column(String(50), default="America/New_York", nullable=False)
    locale = Column(String(10), default="en_US", nullable=False)

    # Status
    status = Column(String(20), default="active", nullable=False, index=True)

    # Settings
    settings = Column(JSONB, default={}, nullable=False, server_default='{}')

    # Relationships
    users = relationship("User", back_populates="school", foreign_keys="User.school_id")
    teachers = relationship("Teacher", back_populates="school")
    students = relationship("Student", back_populates="school")
    parents = relationship("Parent", back_populates="school")
    subjects = relationship("Subject", back_populates="school")
    principal = relationship("User", foreign_keys=[principal_id])
    hod = relationship("User", foreign_keys=[hod_id])

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended')",
            name="schools_status_check"
        ),
        Index('idx_schools_slug', 'slug'),
        Index('idx_schools_status', 'status'),
        Index('idx_schools_deleted_at', 'deleted_at'),
    )

    def __repr__(self):
        return f"<School(id={self.id}, name={self.name}, slug={self.slug})>"

    def is_active(self) -> bool:
        """Check if school is active"""
        return self.status == "active" and not self.is_deleted()

    def get_full_address(self) -> str:
        """Get formatted full address"""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ", ".join(filter(None, parts))

    def to_dict(self, include_sensitive: bool = False):
        """
        Convert school to dictionary

        Args:
            include_sensitive: Include deleted_by and other sensitive fields
        """
        data = super().to_dict()

        # Remove sensitive fields unless explicitly requested
        if not include_sensitive:
            data.pop('deleted_by', None)

        # Add computed fields
        data['is_active'] = self.is_active()
        data['full_address'] = self.get_full_address()

        return data
