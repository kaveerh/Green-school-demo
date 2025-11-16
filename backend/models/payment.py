"""
Payment Model

Individual payment transactions for student fees with receipt tracking and reconciliation.
Supports multiple payment methods and statuses (completed, pending, refunded, etc.).
"""

from sqlalchemy import Column, String, Numeric, Text, Date, CheckConstraint, Index, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from models.base import BaseModel
from decimal import Decimal
from datetime import date, datetime


class Payment(BaseModel):
    """Payment model for tracking fee payments and transactions"""
    __tablename__ = "payments"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    student_fee_id = Column(PG_UUID(as_uuid=True), ForeignKey("student_fees.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    processed_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Payment Details
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, nullable=False, default=date.today)
    payment_method = Column(String(30), nullable=False)  # cash, card, bank_transfer, check, online, other

    # Transaction Tracking
    transaction_reference = Column(String(255), nullable=True)  # bank ref, check number, etc.
    receipt_number = Column(String(100), unique=True, nullable=False)

    # Payment Allocation
    allocation_notes = Column(Text, nullable=True)  # which fees this payment covers

    # Status
    status = Column(String(20), default='completed', nullable=True)  # pending, completed, failed, refunded, cancelled
    refund_reason = Column(Text, nullable=True)
    refunded_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)

    # Relationships
    school = relationship("School", back_populates="payments")
    student_fee = relationship("StudentFee", back_populates="payments")
    student = relationship("Student", back_populates="payments")
    processor = relationship("User", foreign_keys=[processed_by])

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "payment_method IN ('cash', 'card', 'bank_transfer', 'check', 'online', 'other')",
            name="chk_payments_method"
        ),
        CheckConstraint(
            "status IN ('pending', 'completed', 'failed', 'refunded', 'cancelled')",
            name="chk_payments_status"
        ),
        CheckConstraint("amount > 0", name="chk_payments_amount"),
        Index('idx_payments_student_fee', 'student_fee_id'),
        Index('idx_payments_student', 'student_id'),
        Index('idx_payments_date', 'payment_date'),
        Index('idx_payments_method', 'payment_method'),
        Index('idx_payments_status', 'status'),
        Index('idx_payments_receipt', 'receipt_number'),
        Index('idx_payments_deleted_at', 'deleted_at'),
    )

    def __repr__(self):
        return f"<Payment(id={self.id}, student_id={self.student_id}, amount={self.amount}, status={self.status})>"

    @property
    def is_completed(self) -> bool:
        """Check if payment is completed"""
        return self.status == 'completed'

    @property
    def is_pending(self) -> bool:
        """Check if payment is pending"""
        return self.status == 'pending'

    @property
    def is_refunded(self) -> bool:
        """Check if payment was refunded"""
        return self.status == 'refunded'

    @property
    def can_be_refunded(self) -> bool:
        """Check if payment can be refunded"""
        return self.status == 'completed' and not self.is_refunded

    @property
    def display_amount(self) -> str:
        """Format amount for display"""
        return f"${float(self.amount):,.2f}"

    @property
    def payment_method_display(self) -> str:
        """Human-readable payment method"""
        method_map = {
            'cash': 'Cash',
            'card': 'Credit/Debit Card',
            'bank_transfer': 'Bank Transfer',
            'check': 'Check',
            'online': 'Online Payment',
            'other': 'Other'
        }
        return method_map.get(self.payment_method, self.payment_method)

    def mark_as_completed(self):
        """Mark payment as completed"""
        self.status = 'completed'

    def mark_as_failed(self, reason: str = None):
        """Mark payment as failed"""
        self.status = 'failed'
        if reason:
            self.notes = f"Failed: {reason}"

    def process_refund(self, refund_reason: str):
        """Process refund for this payment"""
        if not self.can_be_refunded:
            raise ValueError(f"Payment {self.id} cannot be refunded (status: {self.status})")

        self.status = 'refunded'
        self.refund_reason = refund_reason
        self.refunded_at = datetime.now()

    @staticmethod
    def generate_receipt_number(year: int = None, sequence: int = 1) -> str:
        """Generate receipt number in format RCPT-YYYY-NNNN"""
        if year is None:
            year = date.today().year
        return f"RCPT-{year}-{sequence:04d}"

    def to_dict(self, include_relationships: bool = False):
        """Convert payment to dictionary"""
        data = super().to_dict()

        # Convert Decimal to float for JSON serialization
        if self.amount is not None:
            data['amount'] = float(self.amount)

        # Add computed properties
        data['is_completed'] = self.is_completed
        data['is_pending'] = self.is_pending
        data['is_refunded'] = self.is_refunded
        data['can_be_refunded'] = self.can_be_refunded
        data['display_amount'] = self.display_amount
        data['payment_method_display'] = self.payment_method_display

        if include_relationships:
            try:
                if self.student and self.student.user:
                    data["student"] = {
                        "id": str(self.student.id),
                        "student_id": self.student.student_id,
                        "name": f"{self.student.user.first_name} {self.student.user.last_name}"
                    }
            except:
                pass

            try:
                if self.student_fee:
                    data["student_fee"] = {
                        "id": str(self.student_fee.id),
                        "academic_year": self.student_fee.academic_year,
                        "total_amount_due": float(self.student_fee.total_amount_due),
                        "balance_due": float(self.student_fee.balance_due)
                    }
            except:
                pass

            try:
                if self.processor:
                    data["processed_by"] = {
                        "id": str(self.processor.id),
                        "name": f"{self.processor.first_name} {self.processor.last_name}"
                    }
            except:
                pass

        return data
