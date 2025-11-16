"""
Activity Fee Model

Fee structure for extracurricular activities.
Links activities to fee amounts with support for different frequencies and prorating.
"""

from sqlalchemy import Column, String, Numeric, Boolean, Text, CheckConstraint, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from models.base import BaseModel
from decimal import Decimal


class ActivityFee(BaseModel):
    """Activity fee model for extracurricular activity costs"""
    __tablename__ = "activity_fees"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    activity_id = Column(PG_UUID(as_uuid=True), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)

    # Fee Structure
    academic_year = Column(String(9), nullable=False)  # e.g., "2025-2026"
    fee_amount = Column(Numeric(10, 2), nullable=False)
    fee_frequency = Column(String(20), nullable=False)  # one_time, yearly, quarterly, monthly

    # Prorating Configuration
    allow_prorate = Column(Boolean, default=True, nullable=True)
    prorate_calculation = Column(Text, nullable=True)  # description of prorating method

    # Status
    is_active = Column(Boolean, default=True, nullable=True)

    # Metadata
    description = Column(Text, nullable=True)

    # Relationships
    school = relationship("School", back_populates="activity_fees")
    activity = relationship("Activity", back_populates="activity_fees")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "fee_frequency IN ('one_time', 'yearly', 'quarterly', 'monthly')",
            name="chk_activity_fees_frequency"
        ),
        CheckConstraint("fee_amount >= 0", name="chk_activity_fees_amount"),
        Index('idx_activity_fees_activity', 'activity_id'),
        Index('idx_activity_fees_year', 'academic_year'),
        Index('idx_activity_fees_active', 'is_active'),
        Index('idx_activity_fees_deleted_at', 'deleted_at'),
    )

    def __repr__(self):
        return f"<ActivityFee(id={self.id}, activity_id={self.activity_id}, amount={self.fee_amount}, frequency={self.fee_frequency})>"

    @property
    def is_one_time(self) -> bool:
        """Check if fee is one-time only"""
        return self.fee_frequency == 'one_time'

    @property
    def is_recurring(self) -> bool:
        """Check if fee is recurring"""
        return self.fee_frequency in ('yearly', 'quarterly', 'monthly')

    @property
    def can_prorate(self) -> bool:
        """Check if fee can be prorated"""
        return self.allow_prorate and self.is_recurring

    @property
    def display_frequency(self) -> str:
        """Human-readable frequency"""
        frequency_map = {
            'one_time': 'One-time',
            'yearly': 'Per Year',
            'quarterly': 'Per Quarter',
            'monthly': 'Per Month'
        }
        return frequency_map.get(self.fee_frequency, self.fee_frequency)

    def calculate_prorated_amount(self, months_remaining: int, total_months: int = 12) -> Decimal:
        """
        Calculate prorated fee amount based on months remaining

        Args:
            months_remaining: Number of months left in the period
            total_months: Total months in the period (default 12 for yearly)

        Returns:
            Prorated fee amount
        """
        if not self.can_prorate or months_remaining <= 0:
            return self.fee_amount

        if self.fee_frequency == 'yearly':
            # Prorate based on months remaining in year
            return (self.fee_amount * Decimal(months_remaining) / Decimal(total_months)).quantize(Decimal('0.01'))

        elif self.fee_frequency == 'quarterly':
            # Prorate based on months remaining in quarter (3 months per quarter)
            quarters_remaining = (months_remaining + 2) // 3  # Round up to next quarter
            return (self.fee_amount * Decimal(quarters_remaining)).quantize(Decimal('0.01'))

        elif self.fee_frequency == 'monthly':
            # Monthly fees: charge for remaining months
            return (self.fee_amount * Decimal(months_remaining)).quantize(Decimal('0.01'))

        else:
            # One-time: no prorating
            return self.fee_amount

    def get_annual_cost(self) -> Decimal:
        """Calculate total annual cost for this activity"""
        if self.fee_frequency == 'one_time':
            return self.fee_amount
        elif self.fee_frequency == 'yearly':
            return self.fee_amount
        elif self.fee_frequency == 'quarterly':
            return (self.fee_amount * Decimal('4')).quantize(Decimal('0.01'))
        elif self.fee_frequency == 'monthly':
            return (self.fee_amount * Decimal('12')).quantize(Decimal('0.01'))
        else:
            return self.fee_amount

    def to_dict(self, include_relationships: bool = False):
        """Convert activity fee to dictionary"""
        data = super().to_dict()

        # Convert Decimal to float for JSON serialization
        if self.fee_amount is not None:
            data['fee_amount'] = float(self.fee_amount)

        # Add computed properties
        data['is_one_time'] = self.is_one_time
        data['is_recurring'] = self.is_recurring
        data['can_prorate'] = self.can_prorate
        data['display_frequency'] = self.display_frequency
        data['annual_cost'] = float(self.get_annual_cost())

        if include_relationships:
            try:
                if self.activity:
                    data["activity"] = {
                        "id": str(self.activity.id),
                        "name": self.activity.name,
                        "type": self.activity.activity_type
                    }
            except:
                pass

            try:
                if self.school:
                    data["school"] = {
                        "id": str(self.school.id),
                        "name": self.school.name
                    }
            except:
                pass

        return data
