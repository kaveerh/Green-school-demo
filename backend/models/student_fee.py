"""
Student Fee Model

Individual student fee records with calculated amounts, discounts, and payment tracking.
Tracks tuition, activity fees, discounts (payment frequency + sibling), and bursary support.
"""

from sqlalchemy import Column, String, Integer, Numeric, Text, Date, CheckConstraint, Index, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from models.base import BaseModel
from decimal import Decimal
from datetime import date


class StudentFee(BaseModel):
    """Student fee model for individual student fee records and payment tracking"""
    __tablename__ = "student_fees"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    bursary_id = Column(PG_UUID(as_uuid=True), ForeignKey("bursaries.id"), nullable=True)

    # Academic Year
    academic_year = Column(String(9), nullable=False)  # e.g., "2025-2026"

    # Payment Configuration
    payment_frequency = Column(String(20), nullable=False)  # yearly, monthly, weekly

    # Base Fee Components
    base_tuition_amount = Column(Numeric(10, 2), nullable=False)
    activity_fees_amount = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=True)
    material_fees_amount = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=True)
    other_fees_amount = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=True)

    # Payment Frequency Discount
    payment_discount_percent = Column(Numeric(5, 2), default=Decimal('0.00'), nullable=True)
    payment_discount_amount = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=True)

    # Sibling Discount
    sibling_discount_percent = Column(Numeric(5, 2), default=Decimal('0.00'), nullable=True)
    sibling_discount_amount = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=True)
    sibling_order = Column(Integer, nullable=True)  # 1st, 2nd, 3rd, 4th+ child

    # Bursary
    bursary_amount = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=True)

    # Calculated Totals
    total_before_discounts = Column(Numeric(10, 2), nullable=False)
    total_discounts = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=True)
    total_amount_due = Column(Numeric(10, 2), nullable=False)
    total_paid = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=True)
    balance_due = Column(Numeric(10, 2), nullable=False)

    # Status Tracking
    status = Column(String(20), default='pending', nullable=True)  # pending, partial, paid, overdue, waived
    due_date = Column(Date, nullable=True)
    last_payment_date = Column(Date, nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)

    # Relationships
    school = relationship("School", back_populates="student_fees")
    student = relationship("Student", back_populates="student_fees")
    bursary = relationship("Bursary", back_populates="student_fees")
    payments = relationship("Payment", back_populates="student_fee", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "payment_frequency IN ('yearly', 'monthly', 'weekly')",
            name="chk_student_fees_payment_frequency"
        ),
        CheckConstraint(
            "status IN ('pending', 'partial', 'paid', 'overdue', 'waived')",
            name="chk_student_fees_status"
        ),
        CheckConstraint("base_tuition_amount >= 0", name="chk_student_fees_base_tuition"),
        CheckConstraint("activity_fees_amount >= 0", name="chk_student_fees_activity_fees"),
        CheckConstraint("material_fees_amount >= 0", name="chk_student_fees_material_fees"),
        CheckConstraint("other_fees_amount >= 0", name="chk_student_fees_other_fees"),
        CheckConstraint("payment_discount_percent BETWEEN 0 AND 100", name="chk_student_fees_payment_discount_percent"),
        CheckConstraint("payment_discount_amount >= 0", name="chk_student_fees_payment_discount_amount"),
        CheckConstraint("sibling_discount_percent BETWEEN 0 AND 100", name="chk_student_fees_sibling_discount_percent"),
        CheckConstraint("sibling_discount_amount >= 0", name="chk_student_fees_sibling_discount_amount"),
        CheckConstraint("bursary_amount >= 0", name="chk_student_fees_bursary_amount"),
        CheckConstraint("total_before_discounts >= 0", name="chk_student_fees_total_before_discounts"),
        CheckConstraint("total_discounts >= 0", name="chk_student_fees_total_discounts"),
        CheckConstraint("total_amount_due >= 0", name="chk_student_fees_total_amount_due"),
        CheckConstraint("total_paid >= 0", name="chk_student_fees_total_paid"),
        CheckConstraint("balance_due >= 0", name="chk_student_fees_balance_due"),
        Index('idx_student_fees_school_student', 'school_id', 'student_id'),
        Index('idx_student_fees_status', 'status'),
        Index('idx_student_fees_year', 'academic_year'),
        Index('idx_student_fees_overdue', 'due_date'),
        Index('idx_student_fees_bursary', 'bursary_id'),
        Index('idx_student_fees_deleted_at', 'deleted_at'),
    )

    def __repr__(self):
        return f"<StudentFee(id={self.id}, student_id={self.student_id}, year={self.academic_year}, status={self.status})>"

    @property
    def is_fully_paid(self) -> bool:
        """Check if fee is fully paid"""
        return self.status == 'paid' and self.balance_due <= 0

    @property
    def is_overdue(self) -> bool:
        """Check if fee is overdue"""
        if not self.due_date or self.status in ('paid', 'waived'):
            return False
        return self.due_date < date.today() and self.balance_due > 0

    @property
    def payment_progress_percent(self) -> float:
        """Calculate payment progress as percentage"""
        if self.total_amount_due <= 0:
            return 100.0
        return min(100.0, (float(self.total_paid) / float(self.total_amount_due)) * 100)

    @property
    def has_bursary(self) -> bool:
        """Check if student has bursary assigned"""
        return self.bursary_id is not None and self.bursary_amount > 0

    @property
    def total_fees(self) -> Decimal:
        """Calculate total fees before any discounts or bursaries"""
        return (
            self.base_tuition_amount +
            (self.activity_fees_amount or Decimal('0.00')) +
            (self.material_fees_amount or Decimal('0.00')) +
            (self.other_fees_amount or Decimal('0.00'))
        )

    def recalculate_totals(self):
        """Recalculate all totals based on current values"""
        # Total before discounts
        self.total_before_discounts = self.total_fees

        # Total discounts
        self.total_discounts = (
            (self.payment_discount_amount or Decimal('0.00')) +
            (self.sibling_discount_amount or Decimal('0.00'))
        )

        # Total amount due (after discounts, before bursary)
        amount_after_discounts = self.total_before_discounts - self.total_discounts

        # Apply bursary
        self.total_amount_due = amount_after_discounts - (self.bursary_amount or Decimal('0.00'))

        # Ensure total_amount_due is not negative
        if self.total_amount_due < 0:
            self.total_amount_due = Decimal('0.00')

        # Calculate balance due
        self.balance_due = self.total_amount_due - (self.total_paid or Decimal('0.00'))

        # Ensure balance_due is not negative
        if self.balance_due < 0:
            self.balance_due = Decimal('0.00')

    def update_payment_status(self):
        """Update status based on balance due"""
        if self.balance_due <= 0 or self.total_paid >= self.total_amount_due:
            self.status = 'paid'
        elif self.total_paid > 0:
            self.status = 'partial'
        elif self.is_overdue:
            self.status = 'overdue'
        else:
            self.status = 'pending'

    def record_payment(self, amount: Decimal, payment_date: date = None):
        """Record a payment and update totals"""
        self.total_paid = (self.total_paid or Decimal('0.00')) + amount
        self.balance_due = self.total_amount_due - self.total_paid

        if self.balance_due < 0:
            self.balance_due = Decimal('0.00')

        if payment_date:
            self.last_payment_date = payment_date

        self.update_payment_status()

    def to_dict(self, include_relationships: bool = False):
        """Convert student fee to dictionary"""
        data = super().to_dict()

        # Convert Decimal to float for JSON serialization
        decimal_fields = [
            'base_tuition_amount', 'activity_fees_amount', 'material_fees_amount', 'other_fees_amount',
            'payment_discount_percent', 'payment_discount_amount',
            'sibling_discount_percent', 'sibling_discount_amount',
            'bursary_amount',
            'total_before_discounts', 'total_discounts', 'total_amount_due',
            'total_paid', 'balance_due'
        ]
        for field in decimal_fields:
            value = getattr(self, field)
            if value is not None:
                data[field] = float(value)

        # Add computed properties
        data['is_fully_paid'] = self.is_fully_paid
        data['is_overdue'] = self.is_overdue
        data['payment_progress_percent'] = self.payment_progress_percent
        data['has_bursary'] = self.has_bursary

        if include_relationships:
            try:
                if self.student and self.student.user:
                    data["student"] = {
                        "id": str(self.student.id),
                        "student_id": self.student.student_id,
                        "name": f"{self.student.user.first_name} {self.student.user.last_name}",
                        "grade_level": self.student.grade_level
                    }
            except:
                pass

            try:
                if self.bursary:
                    data["bursary"] = {
                        "id": str(self.bursary.id),
                        "name": self.bursary.name,
                        "type": self.bursary.bursary_type
                    }
            except:
                pass

        return data
