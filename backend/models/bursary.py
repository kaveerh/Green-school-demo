"""
Bursary Model

Bursary and scholarship programs for financial aid support.
Supports both percentage-based and fixed-amount coverage with eligibility criteria.
"""

from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text, Date, CheckConstraint, Index, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from models.base import BaseModel
from decimal import Decimal
from datetime import date


class Bursary(BaseModel):
    """Bursary model for scholarship and financial aid programs"""
    __tablename__ = "bursaries"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)

    # Program Details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    bursary_type = Column(String(20), nullable=False)  # merit, need, sports, academic, other

    # Coverage Configuration
    coverage_type = Column(String(20), nullable=False)  # percentage, fixed_amount
    coverage_value = Column(Numeric(10, 2), nullable=False)  # percentage (0-100) or dollar amount
    max_coverage_amount = Column(Numeric(10, 2), nullable=True)  # cap for percentage-based bursaries

    # Eligibility
    academic_year = Column(String(9), nullable=False)
    eligible_grades = Column(ARRAY(Integer), nullable=False)  # array of grades 1-7
    max_recipients = Column(Integer, nullable=True)  # null = unlimited
    current_recipients = Column(Integer, default=0, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=True)
    application_deadline = Column(Date, nullable=True)

    # Sponsor Information
    sponsor_name = Column(String(255), nullable=True)
    sponsor_contact = Column(Text, nullable=True)
    terms_and_conditions = Column(Text, nullable=True)

    # Relationships
    school = relationship("School", back_populates="bursaries")
    student_fees = relationship("StudentFee", back_populates="bursary")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "bursary_type IN ('merit', 'need', 'sports', 'academic', 'other')",
            name="chk_bursaries_type"
        ),
        CheckConstraint(
            "coverage_type IN ('percentage', 'fixed_amount')",
            name="chk_bursaries_coverage_type"
        ),
        CheckConstraint("coverage_value > 0", name="chk_bursaries_coverage_value"),
        CheckConstraint("max_coverage_amount IS NULL OR max_coverage_amount > 0", name="chk_bursaries_max_coverage"),
        CheckConstraint("max_recipients IS NULL OR max_recipients > 0", name="chk_bursaries_max_recipients"),
        CheckConstraint("current_recipients >= 0", name="chk_bursaries_current_recipients"),
        Index('idx_bursaries_school_year', 'school_id', 'academic_year'),
        Index('idx_bursaries_type', 'bursary_type'),
        Index('idx_bursaries_active', 'is_active'),
        Index('idx_bursaries_deleted_at', 'deleted_at'),
    )

    def __repr__(self):
        return f"<Bursary(id={self.id}, name={self.name}, type={self.bursary_type}, year={self.academic_year})>"

    @property
    def is_percentage_based(self) -> bool:
        """Check if bursary uses percentage coverage"""
        return self.coverage_type == 'percentage'

    @property
    def is_fixed_amount(self) -> bool:
        """Check if bursary uses fixed amount coverage"""
        return self.coverage_type == 'fixed_amount'

    @property
    def has_capacity(self) -> bool:
        """Check if bursary has capacity for more recipients"""
        if self.max_recipients is None:
            return True  # Unlimited
        return self.current_recipients < self.max_recipients

    @property
    def is_deadline_passed(self) -> bool:
        """Check if application deadline has passed"""
        if not self.application_deadline:
            return False
        return self.application_deadline < date.today()

    @property
    def can_accept_applications(self) -> bool:
        """Check if bursary can accept new applications"""
        return self.is_active and self.has_capacity and not self.is_deadline_passed

    def calculate_bursary_amount(self, total_amount: Decimal) -> Decimal:
        """Calculate bursary amount based on coverage type and value"""
        if self.is_fixed_amount:
            # Fixed amount: return coverage_value directly
            return Decimal(str(self.coverage_value)).quantize(Decimal('0.01'))
        else:
            # Percentage: calculate percentage of total_amount
            bursary_amount = (total_amount * Decimal(str(self.coverage_value)) / Decimal('100')).quantize(Decimal('0.01'))

            # Apply max coverage cap if set
            if self.max_coverage_amount is not None:
                max_cap = Decimal(str(self.max_coverage_amount))
                bursary_amount = min(bursary_amount, max_cap)

            return bursary_amount

    def increment_recipients(self):
        """Increment current recipients count"""
        self.current_recipients = (self.current_recipients or 0) + 1

    def decrement_recipients(self):
        """Decrement current recipients count"""
        if self.current_recipients > 0:
            self.current_recipients -= 1

    def is_grade_eligible(self, grade_level: int) -> bool:
        """Check if a grade level is eligible for this bursary"""
        if not self.eligible_grades:
            return False
        return grade_level in self.eligible_grades

    def to_dict(self, include_relationships: bool = False):
        """Convert bursary to dictionary"""
        data = super().to_dict()

        # Convert Decimal to float for JSON serialization
        if self.coverage_value is not None:
            data['coverage_value'] = float(self.coverage_value)
        if self.max_coverage_amount is not None:
            data['max_coverage_amount'] = float(self.max_coverage_amount)

        # Add computed properties
        data['is_percentage_based'] = self.is_percentage_based
        data['is_fixed_amount'] = self.is_fixed_amount
        data['has_capacity'] = self.has_capacity
        data['is_deadline_passed'] = self.is_deadline_passed
        data['can_accept_applications'] = self.can_accept_applications

        if include_relationships and self.school:
            try:
                data["school"] = {
                    "id": str(self.school.id),
                    "name": self.school.name
                }
            except:
                pass

        return data
