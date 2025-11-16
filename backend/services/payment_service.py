"""
Payment Service

Business logic layer for Payment operations with payment processing and receipt generation.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.payment_repository import PaymentRepository
from repositories.student_fee_repository import StudentFeeRepository
from repositories.student_repository import StudentRepository
from models.payment import Payment
from models.student_fee import StudentFee
from decimal import Decimal
from datetime import date, datetime
import uuid


class PaymentService:
    """Service layer for Payment business logic"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PaymentRepository(session)
        self.student_fee_repository = StudentFeeRepository(session)
        self.student_repository = StudentRepository(session)

    async def create_payment(
        self,
        school_id: uuid.UUID,
        student_fee_id: uuid.UUID,
        amount: Decimal,
        payment_method: str,
        processed_by_id: uuid.UUID,
        payment_date: Optional[date] = None,
        transaction_reference: Optional[str] = None,
        allocation_notes: Optional[str] = None,
        notes: Optional[str] = None,
        auto_generate_receipt: bool = True
    ) -> Payment:
        """Create a new payment and update student fee"""

        # Validate student fee exists
        student_fee = await self.student_fee_repository.get_by_id(student_fee_id)
        if not student_fee:
            raise ValueError("Student fee record not found")

        # Validate payment amount
        if amount <= 0:
            raise ValueError("Payment amount must be greater than 0")

        # Check for overpayment
        if amount > student_fee.balance_due:
            raise ValueError(
                f"Payment amount ${float(amount):.2f} exceeds balance due "
                f"${float(student_fee.balance_due):.2f}"
            )

        # Generate receipt number
        receipt_number = None
        if auto_generate_receipt:
            year = payment_date.year if payment_date else datetime.now().year
            receipt_number = await self.repository.get_next_receipt_number(school_id, year)
        else:
            # Generate temporary receipt number (should be updated later)
            receipt_number = f"TEMP-{uuid.uuid4().hex[:8].upper()}"

        # Create payment record
        payment_data = {
            'school_id': school_id,
            'student_fee_id': student_fee_id,
            'student_id': student_fee.student_id,
            'amount': amount,
            'payment_date': payment_date or date.today(),
            'payment_method': payment_method,
            'transaction_reference': transaction_reference,
            'receipt_number': receipt_number,
            'allocation_notes': allocation_notes,
            'status': 'completed',
            'processed_by': processed_by_id,
            'notes': notes
        }

        payment = await self.repository.create(payment_data)

        # Update student fee with payment
        student_fee.record_payment(amount, payment_date or date.today())
        await self.session.flush()

        return payment

    async def create_pending_payment(
        self,
        school_id: uuid.UUID,
        student_fee_id: uuid.UUID,
        amount: Decimal,
        payment_method: str,
        processed_by_id: uuid.UUID,
        transaction_reference: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Payment:
        """
        Create a pending payment (e.g., for authorization holds, pending checks)
        Does not update student fee balance until confirmed
        """

        # Validate student fee
        student_fee = await self.student_fee_repository.get_by_id(student_fee_id)
        if not student_fee:
            raise ValueError("Student fee record not found")

        if amount <= 0:
            raise ValueError("Payment amount must be greater than 0")

        # Generate temp receipt
        receipt_number = f"PENDING-{uuid.uuid4().hex[:8].upper()}"

        payment_data = {
            'school_id': school_id,
            'student_fee_id': student_fee_id,
            'student_id': student_fee.student_id,
            'amount': amount,
            'payment_date': date.today(),
            'payment_method': payment_method,
            'transaction_reference': transaction_reference,
            'receipt_number': receipt_number,
            'status': 'pending',
            'processed_by': processed_by_id,
            'notes': notes
        }

        return await self.repository.create(payment_data)

    async def confirm_payment(
        self,
        payment_id: uuid.UUID,
        updated_by_id: uuid.UUID,
        transaction_reference: Optional[str] = None
    ) -> Optional[Payment]:
        """Confirm a pending payment and update student fee"""

        payment = await self.repository.get_by_id(payment_id)
        if not payment:
            return None

        if payment.status != 'pending':
            raise ValueError(f"Payment is not pending (current status: {payment.status})")

        # Update payment status
        update_data = {'status': 'completed'}

        # Generate proper receipt number
        year = payment.payment_date.year
        receipt_number = await self.repository.get_next_receipt_number(payment.school_id, year)
        update_data['receipt_number'] = receipt_number

        if transaction_reference:
            update_data['transaction_reference'] = transaction_reference

        updated_payment = await self.repository.update(payment_id, update_data, updated_by_id)

        # Update student fee
        student_fee = await self.student_fee_repository.get_by_id(payment.student_fee_id)
        if student_fee:
            student_fee.record_payment(payment.amount, payment.payment_date)
            await self.session.flush()

        return updated_payment

    async def refund_payment(
        self,
        payment_id: uuid.UUID,
        refund_reason: str,
        updated_by_id: uuid.UUID
    ) -> Optional[Payment]:
        """Process a payment refund"""

        payment = await self.repository.get_by_id(payment_id)
        if not payment:
            return None

        if not payment.can_be_refunded:
            raise ValueError(f"Payment cannot be refunded (status: {payment.status})")

        # Process refund on payment
        payment.process_refund(refund_reason)

        # Update student fee - reverse the payment
        student_fee = await self.student_fee_repository.get_by_id(payment.student_fee_id)
        if student_fee:
            student_fee.total_paid = (student_fee.total_paid or Decimal('0.00')) - payment.amount
            student_fee.balance_due = student_fee.total_amount_due - student_fee.total_paid
            student_fee.update_payment_status()
            await self.session.flush()

        return payment

    async def get_payment(
        self,
        payment_id: uuid.UUID,
        include_relationships: bool = True
    ) -> Optional[Payment]:
        """Get payment by ID"""
        if include_relationships:
            return await self.repository.get_with_relationships(payment_id)
        return await self.repository.get_by_id(payment_id)

    async def get_payment_by_receipt(self, receipt_number: str) -> Optional[Payment]:
        """Get payment by receipt number"""
        return await self.repository.get_by_receipt_number(receipt_number)

    async def list_payments(
        self,
        school_id: uuid.UUID,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Payment], int]:
        """List payments with filters"""
        return await self.repository.get_by_school(
            school_id=school_id,
            status=status,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )

    async def get_student_payments(
        self,
        student_id: uuid.UUID,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Payment], int]:
        """Get all payments for a student"""
        return await self.repository.get_by_student(
            student_id=student_id,
            status=status,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )

    async def get_fee_payments(
        self,
        student_fee_id: uuid.UUID,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Payment], int]:
        """Get all payments for a specific student fee"""
        return await self.repository.get_by_student_fee(
            student_fee_id=student_fee_id,
            page=page,
            limit=limit
        )

    async def get_pending_payments(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Payment], int]:
        """Get all pending payments"""
        return await self.repository.get_pending_payments(
            school_id=school_id,
            page=page,
            limit=limit
        )

    async def get_revenue_report(
        self,
        school_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        group_by: str = "month"
    ) -> Dict[str, Any]:
        """Get revenue report with analytics"""
        return await self.repository.get_revenue_report(
            school_id=school_id,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )

    async def update_payment(
        self,
        payment_id: uuid.UUID,
        updated_by_id: uuid.UUID,
        transaction_reference: Optional[str] = None,
        allocation_notes: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Payment]:
        """Update payment details (limited fields)"""

        update_data = {}

        if transaction_reference is not None:
            update_data['transaction_reference'] = transaction_reference
        if allocation_notes is not None:
            update_data['allocation_notes'] = allocation_notes
        if notes is not None:
            update_data['notes'] = notes

        if not update_data:
            return await self.repository.get_by_id(payment_id)

        return await self.repository.update(payment_id, update_data, updated_by_id)

    async def delete_payment(
        self,
        payment_id: uuid.UUID,
        deleted_by_id: uuid.UUID
    ) -> bool:
        """
        Delete payment (soft delete) - only for pending payments
        Completed payments should be refunded instead
        """
        payment = await self.repository.get_by_id(payment_id)
        if not payment:
            return False

        if payment.status == 'completed':
            raise ValueError("Cannot delete completed payment. Use refund instead.")

        return await self.repository.delete(payment_id, deleted_by_id)

    async def generate_receipt_data(self, payment_id: uuid.UUID) -> Dict[str, Any]:
        """Generate receipt data for printing/PDF"""
        payment = await self.repository.get_with_relationships(payment_id)
        if not payment:
            raise ValueError("Payment not found")

        student_fee = payment.student_fee
        student = payment.student

        return {
            "receipt_number": payment.receipt_number,
            "payment_date": payment.payment_date.isoformat(),
            "payment_method": payment.payment_method_display,
            "amount": float(payment.amount),
            "display_amount": payment.display_amount,

            # Student info
            "student": {
                "id": str(student.id),
                "name": f"{student.user.first_name} {student.user.last_name}" if student.user else "Unknown",
                "student_id": student.student_id,
                "grade_level": student.grade_level
            },

            # Fee info
            "fee": {
                "academic_year": student_fee.academic_year,
                "payment_frequency": student_fee.payment_frequency,
                "total_amount_due": float(student_fee.total_amount_due),
                "total_paid": float(student_fee.total_paid),
                "balance_due": float(student_fee.balance_due),
                "status": student_fee.status
            },

            # Transaction details
            "transaction_reference": payment.transaction_reference,
            "allocation_notes": payment.allocation_notes,
            "notes": payment.notes,

            # Processor
            "processed_by": {
                "id": str(payment.processor.id),
                "name": f"{payment.processor.first_name} {payment.processor.last_name}"
            } if payment.processor else None,

            # Status
            "status": payment.status,
            "is_refunded": payment.is_refunded,
            "refund_reason": payment.refund_reason if payment.is_refunded else None
        }
