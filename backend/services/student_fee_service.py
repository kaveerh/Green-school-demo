"""
Student Fee Service

Business logic layer for StudentFee operations with fee calculation, discount, and bursary logic.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.student_fee_repository import StudentFeeRepository
from repositories.fee_structure_repository import FeeStructureRepository
from repositories.bursary_repository import BursaryRepository
from repositories.activity_fee_repository import ActivityFeeRepository
from repositories.student_repository import StudentRepository
from repositories.school_repository import SchoolRepository
from models.student_fee import StudentFee
from models.fee_structure import FeeStructure
from models.bursary import Bursary
from decimal import Decimal
from datetime import date, timedelta
import uuid


class StudentFeeService:
    """Service layer for StudentFee business logic with calculation engine"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = StudentFeeRepository(session)
        self.fee_structure_repository = FeeStructureRepository(session)
        self.bursary_repository = BursaryRepository(session)
        self.activity_fee_repository = ActivityFeeRepository(session)
        self.student_repository = StudentRepository(session)
        self.school_repository = SchoolRepository(session)

    async def calculate_fee_preview(
        self,
        school_id: uuid.UUID,
        student_id: uuid.UUID,
        academic_year: str,
        payment_frequency: str,
        bursary_id: Optional[uuid.UUID] = None,
        include_activities: bool = True,
        material_fees: Decimal = Decimal('0.00'),
        other_fees: Decimal = Decimal('0.00')
    ) -> Dict[str, Any]:
        """
        Calculate fee preview without saving to database
        Shows all calculations step-by-step
        """
        # Get student
        student = await self.student_repository.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

        # Get fee structure for student's grade
        fee_structure = await self.fee_structure_repository.get_by_school_and_grade(
            school_id=school_id,
            grade_level=student.grade_level,
            academic_year=academic_year
        )
        if not fee_structure:
            raise ValueError(f"No fee structure found for grade {student.grade_level} in {academic_year}")

        # Step 1: Base tuition based on payment frequency
        base_tuition = fee_structure.get_base_amount(payment_frequency)

        # Step 2: Payment frequency discount
        payment_discount_percent = fee_structure.get_payment_discount(payment_frequency)
        payment_discount_amount = fee_structure.calculate_discount_amount(
            base_tuition, payment_discount_percent
        )

        # Step 3: Calculate sibling order and discount
        sibling_order = await self.repository.calculate_sibling_order(
            student_id=student_id,
            school_id=school_id,
            academic_year=academic_year
        )
        sibling_discount_percent = fee_structure.get_sibling_discount(sibling_order)
        sibling_discount_amount = fee_structure.calculate_discount_amount(
            base_tuition, sibling_discount_percent
        )

        # Step 4: Activity fees
        activity_fees_amount = Decimal('0.00')
        activities = []
        if include_activities:
            activity_data = await self.activity_fee_repository.get_total_fees_for_student_activities(
                student_id=student_id,
                academic_year=academic_year,
                school_id=school_id
            )
            activity_fees_amount = Decimal(str(activity_data['total_activity_fees']))
            activities = activity_data['activities']

        # Step 5: Calculate totals before bursary
        total_before_discounts = base_tuition + activity_fees_amount + material_fees + other_fees
        total_discounts = payment_discount_amount + sibling_discount_amount
        total_after_discounts = total_before_discounts - total_discounts

        # Step 6: Apply bursary if provided
        bursary_amount = Decimal('0.00')
        bursary_info = None
        if bursary_id:
            bursary = await self.bursary_repository.get_by_id(bursary_id)
            if bursary:
                # Validate bursary eligibility
                if not bursary.can_accept_applications:
                    raise ValueError(f"Bursary '{bursary.name}' is not accepting applications")

                if not bursary.is_grade_eligible(student.grade_level):
                    raise ValueError(f"Student grade {student.grade_level} is not eligible for this bursary")

                bursary_amount = bursary.calculate_bursary_amount(total_after_discounts)
                bursary_info = {
                    "id": str(bursary.id),
                    "name": bursary.name,
                    "type": bursary.bursary_type,
                    "coverage_type": bursary.coverage_type,
                    "coverage_value": float(bursary.coverage_value),
                    "amount": float(bursary_amount)
                }

        # Step 7: Final calculations
        total_amount_due = total_after_discounts - bursary_amount
        if total_amount_due < 0:
            total_amount_due = Decimal('0.00')

        # Calculate due date based on payment frequency
        due_date = self._calculate_due_date(payment_frequency)

        return {
            "student_id": str(student_id),
            "student_name": f"{student.user.first_name} {student.user.last_name}" if student.user else "Unknown",
            "grade_level": student.grade_level,
            "academic_year": academic_year,
            "payment_frequency": payment_frequency,
            "sibling_order": sibling_order,

            # Fee breakdown
            "base_tuition": float(base_tuition),
            "activity_fees": float(activity_fees_amount),
            "material_fees": float(material_fees),
            "other_fees": float(other_fees),
            "total_before_discounts": float(total_before_discounts),

            # Discounts
            "payment_discount": {
                "percent": float(payment_discount_percent),
                "amount": float(payment_discount_amount)
            },
            "sibling_discount": {
                "percent": float(sibling_discount_percent),
                "amount": float(sibling_discount_amount)
            },
            "total_discounts": float(total_discounts),

            # After discounts
            "total_after_discounts": float(total_after_discounts),

            # Bursary
            "bursary": bursary_info,
            "bursary_amount": float(bursary_amount),

            # Final
            "total_amount_due": float(total_amount_due),
            "balance_due": float(total_amount_due),
            "due_date": due_date.isoformat() if due_date else None,

            # Additional info
            "activities": activities,
            "fee_structure_id": str(fee_structure.id)
        }

    async def create_student_fee(
        self,
        school_id: uuid.UUID,
        student_id: uuid.UUID,
        academic_year: str,
        payment_frequency: str,
        created_by_id: uuid.UUID,
        bursary_id: Optional[uuid.UUID] = None,
        material_fees: Decimal = Decimal('0.00'),
        other_fees: Decimal = Decimal('0.00'),
        notes: Optional[str] = None
    ) -> StudentFee:
        """Create a new student fee with full calculation"""

        # Check if fee already exists
        existing = await self.repository.get_by_student_and_year(student_id, academic_year)
        if existing:
            raise ValueError(f"Fee record already exists for student in {academic_year}")

        # Calculate fee preview to get all values
        preview = await self.calculate_fee_preview(
            school_id=school_id,
            student_id=student_id,
            academic_year=academic_year,
            payment_frequency=payment_frequency,
            bursary_id=bursary_id,
            include_activities=True,
            material_fees=material_fees,
            other_fees=other_fees
        )

        # Create student fee record
        fee_data = {
            'school_id': school_id,
            'student_id': student_id,
            'academic_year': academic_year,
            'payment_frequency': payment_frequency,
            'base_tuition_amount': Decimal(str(preview['base_tuition'])),
            'activity_fees_amount': Decimal(str(preview['activity_fees'])),
            'material_fees_amount': material_fees,
            'other_fees_amount': other_fees,
            'payment_discount_percent': Decimal(str(preview['payment_discount']['percent'])),
            'payment_discount_amount': Decimal(str(preview['payment_discount']['amount'])),
            'sibling_discount_percent': Decimal(str(preview['sibling_discount']['percent'])),
            'sibling_discount_amount': Decimal(str(preview['sibling_discount']['amount'])),
            'sibling_order': preview['sibling_order'],
            'bursary_id': bursary_id,
            'bursary_amount': Decimal(str(preview['bursary_amount'])),
            'total_before_discounts': Decimal(str(preview['total_before_discounts'])),
            'total_discounts': Decimal(str(preview['total_discounts'])),
            'total_amount_due': Decimal(str(preview['total_amount_due'])),
            'total_paid': Decimal('0.00'),
            'balance_due': Decimal(str(preview['total_amount_due'])),
            'status': 'pending',
            'due_date': date.fromisoformat(preview['due_date']) if preview['due_date'] else None,
            'notes': notes
        }

        student_fee = await self.repository.create(fee_data, created_by_id)

        # Increment bursary recipients if bursary assigned
        if bursary_id:
            await self.bursary_repository.increment_recipients(bursary_id)
            await self.session.flush()

        return student_fee

    async def update_student_fee(
        self,
        fee_id: uuid.UUID,
        updated_by_id: uuid.UUID,
        payment_frequency: Optional[str] = None,
        bursary_id: Optional[uuid.UUID] = None,
        material_fees: Optional[Decimal] = None,
        other_fees: Optional[Decimal] = None,
        notes: Optional[str] = None,
        recalculate: bool = True
    ) -> Optional[StudentFee]:
        """Update student fee and optionally recalculate"""

        fee = await self.repository.get_by_id(fee_id)
        if not fee:
            return None

        old_bursary_id = fee.bursary_id
        update_data = {}

        if payment_frequency is not None:
            update_data['payment_frequency'] = payment_frequency
        if material_fees is not None:
            update_data['material_fees_amount'] = material_fees
        if other_fees is not None:
            update_data['other_fees_amount'] = other_fees
        if notes is not None:
            update_data['notes'] = notes

        # Handle bursary change
        if bursary_id is not None and bursary_id != old_bursary_id:
            # Validate new bursary
            if bursary_id:
                bursary = await self.bursary_repository.get_by_id(bursary_id)
                if not bursary:
                    raise ValueError("Bursary not found")
                if not bursary.can_accept_applications:
                    raise ValueError(f"Bursary '{bursary.name}' is not accepting applications")

            update_data['bursary_id'] = bursary_id

        if recalculate and update_data:
            # Recalculate fees
            preview = await self.calculate_fee_preview(
                school_id=fee.school_id,
                student_id=fee.student_id,
                academic_year=fee.academic_year,
                payment_frequency=payment_frequency or fee.payment_frequency,
                bursary_id=bursary_id if bursary_id is not None else fee.bursary_id,
                material_fees=material_fees or fee.material_fees_amount,
                other_fees=other_fees or fee.other_fees_amount
            )

            # Update with recalculated values
            update_data.update({
                'base_tuition_amount': Decimal(str(preview['base_tuition'])),
                'activity_fees_amount': Decimal(str(preview['activity_fees'])),
                'payment_discount_percent': Decimal(str(preview['payment_discount']['percent'])),
                'payment_discount_amount': Decimal(str(preview['payment_discount']['amount'])),
                'sibling_discount_percent': Decimal(str(preview['sibling_discount']['percent'])),
                'sibling_discount_amount': Decimal(str(preview['sibling_discount']['amount'])),
                'bursary_amount': Decimal(str(preview['bursary_amount'])),
                'total_before_discounts': Decimal(str(preview['total_before_discounts'])),
                'total_discounts': Decimal(str(preview['total_discounts'])),
                'total_amount_due': Decimal(str(preview['total_amount_due'])),
                'balance_due': Decimal(str(preview['total_amount_due'])) - (fee.total_paid or Decimal('0.00'))
            })

        updated_fee = await self.repository.update(fee_id, update_data, updated_by_id)

        # Handle bursary recipient counts
        if bursary_id is not None and bursary_id != old_bursary_id:
            if old_bursary_id:
                await self.bursary_repository.decrement_recipients(old_bursary_id)
            if bursary_id:
                await self.bursary_repository.increment_recipients(bursary_id)
            await self.session.flush()

        if updated_fee:
            updated_fee.update_payment_status()
            await self.session.flush()

        return updated_fee

    async def get_student_fee(
        self,
        fee_id: uuid.UUID,
        include_relationships: bool = True
    ) -> Optional[StudentFee]:
        """Get student fee by ID"""
        if include_relationships:
            return await self.repository.get_with_relationships(fee_id)
        return await self.repository.get_by_id(fee_id)

    async def list_student_fees(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None,
        status: Optional[str] = None,
        payment_frequency: Optional[str] = None,
        has_bursary: Optional[bool] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[StudentFee], int]:
        """List student fees with filters"""
        return await self.repository.get_by_school(
            school_id=school_id,
            academic_year=academic_year,
            status=status,
            payment_frequency=payment_frequency,
            has_bursary=has_bursary,
            page=page,
            limit=limit
        )

    async def get_overdue_fees(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[StudentFee], int]:
        """Get all overdue fees"""
        return await self.repository.get_overdue(
            school_id=school_id,
            academic_year=academic_year,
            page=page,
            limit=limit
        )

    async def mark_fees_overdue(self, school_id: uuid.UUID) -> int:
        """Mark pending/partial fees as overdue if past due date"""
        return await self.repository.mark_overdue(school_id)

    async def get_statistics(
        self,
        school_id: uuid.UUID,
        academic_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get fee statistics for school"""
        return await self.repository.get_statistics(school_id, academic_year)

    async def delete_student_fee(
        self,
        fee_id: uuid.UUID,
        deleted_by_id: uuid.UUID
    ) -> bool:
        """Delete student fee (soft delete)"""
        fee = await self.repository.get_by_id(fee_id)
        if not fee:
            return False

        # Decrement bursary recipients if applicable
        if fee.bursary_id:
            await self.bursary_repository.decrement_recipients(fee.bursary_id)

        return await self.repository.delete(fee_id, deleted_by_id)

    def _calculate_due_date(self, payment_frequency: str) -> date:
        """Calculate due date based on payment frequency"""
        today = date.today()

        if payment_frequency == 'yearly':
            # Due 30 days from now for yearly
            return today + timedelta(days=30)
        elif payment_frequency == 'monthly':
            # Due on 1st of next month
            if today.month == 12:
                return date(today.year + 1, 1, 1)
            else:
                return date(today.year, today.month + 1, 1)
        else:  # weekly
            # Due next week
            return today + timedelta(days=7)
