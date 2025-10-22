"""
Room ORM Model

Facility management for classrooms, labs, and specialized rooms.
"""

from sqlalchemy import Column, String, Integer, Boolean, DECIMAL, ARRAY, ForeignKey, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from typing import Optional, List
import uuid

from .base import BaseModel


class Room(BaseModel):
    """Room model for facility management"""

    __tablename__ = "rooms"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Room Identification
    room_number = Column(String(50), nullable=False)
    building = Column(String(100), nullable=True)
    floor = Column(Integer, nullable=True)

    # Room Classification
    room_type = Column(String(50), nullable=False, index=True)  # classroom, lab, gym, library, office, cafeteria
    room_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)

    # Capacity and Features
    capacity = Column(Integer, nullable=False, default=30)
    area_sqft = Column(DECIMAL(10, 2), nullable=True)
    equipment = Column(ARRAY(Text), nullable=False, default=[])
    features = Column(ARRAY(Text), nullable=False, default=[])

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_available = Column(Boolean, default=True)

    # Display
    color = Column(String(7), nullable=True)  # #RRGGBB
    icon = Column(String(50), nullable=True)
    display_order = Column(Integer, default=0)

    # Relationships
    school = relationship("School", back_populates="rooms")
    owner = relationship("User", foreign_keys=[owner_id])
    # classes = relationship("Class", back_populates="room")  # Will be added in Feature #8
    # events = relationship("Event", back_populates="room")  # Will be added in Feature #12

    # Constraints
    __table_args__ = (
        UniqueConstraint('school_id', 'room_number', name='uq_rooms_number_school'),
        CheckConstraint(
            "room_type IN ('classroom', 'lab', 'gym', 'library', 'office', 'cafeteria')",
            name='chk_rooms_type'
        ),
        CheckConstraint('capacity > 0', name='chk_rooms_capacity'),
        CheckConstraint('floor >= -2 AND floor <= 10', name='chk_rooms_floor'),
        # Composite index for common queries
        {'extend_existing': True}
    )

    def __repr__(self) -> str:
        return f"<Room {self.room_number} ({self.room_type}) - {self.school_id}>"

    def to_dict(self) -> dict:
        """Convert room to dictionary with computed fields"""
        base_dict = super().to_dict()

        # Add computed fields
        base_dict['location'] = self.get_location()
        base_dict['capacity_label'] = self.get_capacity_label()
        base_dict['equipment_count'] = len(self.equipment) if self.equipment else 0
        base_dict['owner_name'] = f"{self.owner.first_name} {self.owner.last_name}" if self.owner else None

        return base_dict

    def get_location(self) -> Optional[str]:
        """Get formatted location string"""
        if not self.building and self.floor is None:
            return None

        parts = []

        if self.building:
            parts.append(self.building)

        if self.floor is not None:
            if self.floor == 0:
                floor_label = "Ground Floor"
            elif self.floor < 0:
                floor_label = f"Basement {abs(self.floor)}"
            else:
                floor_label = f"Floor {self.floor}"
            parts.append(floor_label)

        return " - ".join(parts) if parts else None

    def get_capacity_label(self) -> str:
        """Get formatted capacity label"""
        return f"{self.capacity} {'person' if self.capacity == 1 else 'people'}"

    def is_classroom_type(self) -> bool:
        """Check if room is a classroom"""
        return self.room_type == 'classroom'

    def is_lab_type(self) -> bool:
        """Check if room is a laboratory"""
        return self.room_type == 'lab'

    def has_equipment(self, equipment_name: str) -> bool:
        """Check if room has specific equipment"""
        if not self.equipment:
            return False
        return equipment_name.lower() in [e.lower() for e in self.equipment]

    def has_feature(self, feature_name: str) -> bool:
        """Check if room has specific feature"""
        if not self.features:
            return False
        return feature_name.lower() in [f.lower() for f in self.features]

    def add_equipment(self, equipment_name: str) -> None:
        """Add equipment to room"""
        if not self.equipment:
            self.equipment = []
        if equipment_name not in self.equipment:
            self.equipment.append(equipment_name)

    def remove_equipment(self, equipment_name: str) -> None:
        """Remove equipment from room"""
        if self.equipment and equipment_name in self.equipment:
            self.equipment.remove(equipment_name)

    def add_feature(self, feature_name: str) -> None:
        """Add feature to room"""
        if not self.features:
            self.features = []
        if feature_name not in self.features:
            self.features.append(feature_name)

    def remove_feature(self, feature_name: str) -> None:
        """Remove feature from room"""
        if self.features and feature_name in self.features:
            self.features.remove(feature_name)

    def get_default_icon(self) -> str:
        """Get default icon based on room type"""
        icons = {
            'classroom': '🏫',
            'lab': '🔬',
            'gym': '⚽',
            'library': '📚',
            'office': '💼',
            'cafeteria': '🍽️'
        }
        return icons.get(self.room_type, '🏫')

    def get_default_color(self) -> str:
        """Get default color based on room type"""
        colors = {
            'classroom': '#4CAF50',
            'lab': '#9C27B0',
            'gym': '#F44336',
            'library': '#795548',
            'office': '#607D8B',
            'cafeteria': '#FF9800'
        }
        return colors.get(self.room_type, '#757575')

    @property
    def is_large_capacity(self) -> bool:
        """Check if room has large capacity (>50)"""
        return self.capacity > 50

    @property
    def is_small_capacity(self) -> bool:
        """Check if room has small capacity (<15)"""
        return self.capacity < 15
