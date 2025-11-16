"""
Fee Structure Model

Master fee structure per school/grade level with payment frequency and discount configurations.
Defines base tuition amounts and discount percentages for different payment plans.
"""

from sqlalchemy import Column, String, Integer, Numeric, Boolean, CheckConstraint, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from models.base import BaseModel
from decimal import Decimal


class FeeStructure(BaseModel):
    """Fee structure model for school-wide fee configuration"""
    __tablename__ = "fee_structures"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)

    # Grade and Academic Year
    grade_level = Column(Integer, nullable=False)
    academic_year = Column(String(9), nullable=False)  # e.g., "2025-2026"

    # Base fees for different payment frequencies
    yearly_amount = Column(Numeric(10, 2), nullable=False)
    monthly_amount = Column(Numeric(10, 2), nullable=False)
    weekly_amount = Column(Numeric(10, 2), nullable=False)

    # Payment frequency discounts (percentage 0-100)
    yearly_discount = Column(Numeric(5, 2), default=Decimal('0.00'), nullable=True)
    monthly_discount = Column(Numeric(5, 2), default=Decimal('0.00'), nullable=True)
    weekly_discount = Column(Numeric(5, 2), default=Decimal('0.00'), nullable=True)

    # Sibling discount configuration (percentage 0-100)
    sibling_2_discount = Column(Numeric(5, 2), default=Decimal('10.00'), nullable=True)
    sibling_3_discount = Column(Numeric(5, 2), default=Decimal('15.00'), nullable=True)
    sibling_4_plus_discount = Column(Numeric(5, 2), default=Decimal('20.00'), nullable=True)
    apply_sibling_to_all = Column(Boolean, default=False, nullable=True)  # true = all siblings, false = only younger

    # Status
    is_active = Column(Boolean, default=True, nullable=True)

    # Relationships
    school = relationship("School", back_populates="fee_structures")

    # Constraints
    __table_args__ = (
        CheckConstraint("grade_level BETWEEN 1 AND 7", name="chk_fee_structures_grade_level"),
        CheckConstraint("yearly_amount > 0", name="chk_fee_structures_yearly_amount"),
        CheckConstraint("monthly_amount > 0", name="chk_fee_structures_monthly_amount"),
        CheckConstraint("weekly_amount > 0", name="chk_fee_structures_weekly_amount"),
        CheckConstraint("yearly_discount BETWEEN 0 AND 100", name="chk_fee_structures_yearly_discount"),
        CheckConstraint("monthly_discount BETWEEN 0 AND 100", name="chk_fee_structures_monthly_discount"),
        CheckConstraint("weekly_discount BETWEEN 0 AND 100", name="chk_fee_structures_weekly_discount"),
        CheckConstraint("sibling_2_discount BETWEEN 0 AND 100", name="chk_fee_structures_sibling_2_discount"),
        CheckConstraint("sibling_3_discount BETWEEN 0 AND 100", name="chk_fee_structures_sibling_3_discount"),
        CheckConstraint("sibling_4_plus_discount BETWEEN 0 AND 100", name="chk_fee_structures_sibling_4_plus_discount"),
        Index('idx_fee_structures_school_year', 'school_id', 'academic_year'),
        Index('idx_fee_structures_active', 'is_active'),
        Index('idx_fee_structures_deleted_at', 'deleted_at'),
    )

    def __repr__(self):
        return f"<FeeStructure(id={self.id}, school_id={self.school_id}, grade={self.grade_level}, year={self.academic_year})>"

    def get_base_amount(self, payment_frequency: str) -> Decimal:
        """Get base tuition amount for specified payment frequency"""
        frequency_map = {
            'yearly': self.yearly_amount,
            'monthly': self.monthly_amount,
            'weekly': self.weekly_amount
        }
        return frequency_map.get(payment_frequency, self.yearly_amount)

    def get_payment_discount(self, payment_frequency: str) -> Decimal:
        """Get discount percentage for specified payment frequency"""
        discount_map = {
            'yearly': self.yearly_discount or Decimal('0.00'),
            'monthly': self.monthly_discount or Decimal('0.00'),
            'weekly': self.weekly_discount or Decimal('0.00')
        }
        return discount_map.get(payment_frequency, Decimal('0.00'))

    def get_sibling_discount(self, sibling_order: int) -> Decimal:
        """Get discount percentage based on sibling order (1=first child, 2=second, etc.)"""
        if sibling_order <= 1:
            return Decimal('0.00')
        elif sibling_order == 2:
            return self.sibling_2_discount or Decimal('10.00')
        elif sibling_order == 3:
            return self.sibling_3_discount or Decimal('15.00')
        else:  # 4+
            return self.sibling_4_plus_discount or Decimal('20.00')

    def calculate_discount_amount(self, base_amount: Decimal, discount_percent: Decimal) -> Decimal:
        """Calculate discount amount from percentage"""
        if discount_percent <= 0:
            return Decimal('0.00')
        return (base_amount * discount_percent / Decimal('100')).quantize(Decimal('0.01'))

    def to_dict(self, include_relationships: bool = False):
        """Convert fee structure to dictionary"""
        data = super().to_dict()

        # Convert Decimal to float for JSON serialization
        decimal_fields = [
            'yearly_amount', 'monthly_amount', 'weekly_amount',
            'yearly_discount', 'monthly_discount', 'weekly_discount',
            'sibling_2_discount', 'sibling_3_discount', 'sibling_4_plus_discount'
        ]
        for field in decimal_fields:
            value = getattr(self, field)
            if value is not None:
                data[field] = float(value)

        if include_relationships and self.school:
            try:
                data["school"] = {
                    "id": str(self.school.id),
                    "name": self.school.name
                }
            except:
                pass

        return data
