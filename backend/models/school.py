"""
School Model
School entity for multi-tenant architecture
"""
from sqlalchemy import Column, String, Boolean, Index
from sqlalchemy.dialects.postgresql import JSONB
from models.base import BaseModel


class School(BaseModel):
    """School model for multi-tenant support"""
    __tablename__ = "schools"

    # Basic Information
    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(255), unique=True, nullable=False)

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
    website = Column(String(255), nullable=True)

    # Status
    status = Column(String(20), default="active", nullable=False)

    # Settings
    settings = Column(JSONB, default={}, nullable=False, server_default='{}')

    # Indexes
    __table_args__ = (
        Index('idx_schools_slug', 'slug'),
        Index('idx_schools_status', 'status'),
    )

    def __repr__(self):
        return f"<School(id={self.id}, name={self.name})>"

    def is_active(self) -> bool:
        """Check if school is active"""
        return self.status == "active" and not self.is_deleted()
