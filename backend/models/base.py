"""
Base Model
Common fields and functionality for all models
"""
from sqlalchemy import Column, DateTime, UUID, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from config.database import Base
import uuid


class BaseModel(Base):
    """Abstract base model with common fields"""
    __abstract__ = True

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(PG_UUID(as_uuid=True), nullable=True)

    def soft_delete(self, deleted_by_id: uuid.UUID = None):
        """Soft delete this record"""
        self.deleted_at = func.now()
        if deleted_by_id:
            self.deleted_by = deleted_by_id

    def is_deleted(self) -> bool:
        """Check if record is soft deleted"""
        return self.deleted_at is not None

    def to_dict(self):
        """Convert model to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Convert UUID to string
            if isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result
