"""
Payment Repository

Data access layer for Payment operations with transaction tracking.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, extract
from sqlalchemy.orm import selectinload
from models.payment import Payment
from models.student_fee import StudentFee
from models.student import Student
from models.user import User
from repositories.base_repository import BaseRepository
from decimal import Decimal
import uuid
from datetime import date, datetime


class PaymentRepository(BaseRepository[Payment]):
    """Repository for Payment data access"""

    def __init__(self, session: AsyncSession):
        super().__init__(Payment, session)

    async def get_with_relationships(self, payment_id: uuid.UUID) -> Optional[Payment]:
        """Get payment with all relationships loaded"""
        query = select(Payment).where(
            and_(
                Payment.id == payment_id,
                Payment.deleted_at.is_(None)
            )
        ).options(
            selectinload(Payment.student).selectinload(Student.user),
            selectinload(Payment.student_fee),
            selectinload(Payment.school),
            selectinload(Payment.processor)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_receipt_number(self, receipt_number: str) -> Optional[Payment]:
        """Get payment by receipt number"""
        query = select(Payment).where(
            and_(
                Payment.receipt_number == receipt_number,
                Payment.deleted_at.is_(None)
            )
        ).options(
            selectinload(Payment.student).selectinload(Student.user),
            selectinload(Payment.student_fee)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_student(
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
        offset = (page - 1) * limit

        conditions = [
            Payment.student_id == student_id,
            Payment.deleted_at.is_(None)
        ]

        if status:
            conditions.append(Payment.status == status)
        if payment_method:
            conditions.append(Payment.payment_method == payment_method)
        if start_date:
            conditions.append(Payment.payment_date >= start_date)
        if end_date:
            conditions.append(Payment.payment_date <= end_date)

        # Count query
        count_query = select(func.count(Payment.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Payment).where(and_(*conditions)).options(
            selectinload(Payment.student_fee),
            selectinload(Payment.processor)
        ).offset(offset).limit(limit).order_by(Payment.payment_date.desc())

        result = await self.session.execute(query)
        payments = result.scalars().all()

        return list(payments), total

    async def get_by_student_fee(
        self,
        student_fee_id: uuid.UUID,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Payment], int]:
        """Get all payments for a specific student fee"""
        offset = (page - 1) * limit

        conditions = [
            Payment.student_fee_id == student_fee_id,
            Payment.deleted_at.is_(None)
        ]

        # Count query
        count_query = select(func.count(Payment.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Payment).where(and_(*conditions)).options(
            selectinload(Payment.processor)
        ).offset(offset).limit(limit).order_by(Payment.payment_date.desc())

        result = await self.session.execute(query)
        payments = result.scalars().all()

        return list(payments), total

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Payment], int]:
        """Get payments for a school with optional filters"""
        offset = (page - 1) * limit

        conditions = [
            Payment.school_id == school_id,
            Payment.deleted_at.is_(None)
        ]

        if status:
            conditions.append(Payment.status == status)
        if payment_method:
            conditions.append(Payment.payment_method == payment_method)
        if start_date:
            conditions.append(Payment.payment_date >= start_date)
        if end_date:
            conditions.append(Payment.payment_date <= end_date)

        # Count query
        count_query = select(func.count(Payment.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Payment).where(and_(*conditions)).options(
            selectinload(Payment.student).selectinload(Student.user),
            selectinload(Payment.student_fee)
        ).offset(offset).limit(limit).order_by(Payment.payment_date.desc())

        result = await self.session.execute(query)
        payments = result.scalars().all()

        return list(payments), total

    async def get_next_receipt_number(
        self,
        school_id: uuid.UUID,
        year: Optional[int] = None
    ) -> str:
        """Generate next receipt number for the year"""
        if year is None:
            year = datetime.now().year

        # Get count of receipts for this year
        pattern = f"RCPT-{year}-%"
        query = select(func.count(Payment.id)).where(
            and_(
                Payment.school_id == school_id,
                Payment.receipt_number.like(pattern)
            )
        )

        result = await self.session.execute(query)
        count = result.scalar() or 0

        # Next sequence number
        sequence = count + 1

        return Payment.generate_receipt_number(year, sequence)

    async def get_revenue_report(
        self,
        school_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        group_by: str = "month"  # day, month, year
    ) -> Dict[str, Any]:
        """Get revenue report with grouping"""
        conditions = [
            Payment.school_id == school_id,
            Payment.status == 'completed',
            Payment.deleted_at.is_(None)
        ]

        if start_date:
            conditions.append(Payment.payment_date >= start_date)
        if end_date:
            conditions.append(Payment.payment_date <= end_date)

        # Total revenue
        total_query = select(func.sum(Payment.amount)).where(and_(*conditions))
        total_result = await self.session.execute(total_query)
        total_revenue = total_result.scalar() or Decimal('0.00')

        # Count of payments
        count_query = select(func.count(Payment.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total_payments = count_result.scalar()

        # By payment method
        method_query = select(
            Payment.payment_method,
            func.count(Payment.id).label('count'),
            func.sum(Payment.amount).label('total')
        ).where(and_(*conditions)).group_by(Payment.payment_method)
        method_result = await self.session.execute(method_query)
        by_method = {
            row[0]: {"count": row[1], "total": float(row[2] or 0)}
            for row in method_result
        }

        # By time period
        if group_by == "day":
            time_group = Payment.payment_date
        elif group_by == "month":
            time_group = func.date_trunc('month', Payment.payment_date)
        else:  # year
            time_group = extract('year', Payment.payment_date)

        period_query = select(
            time_group.label('period'),
            func.count(Payment.id).label('count'),
            func.sum(Payment.amount).label('total')
        ).where(and_(*conditions)).group_by('period').order_by('period')

        period_result = await self.session.execute(period_query)
        by_period = [
            {
                "period": str(row[0]),
                "count": row[1],
                "total": float(row[2] or 0)
            }
            for row in period_result
        ]

        return {
            "total_revenue": float(total_revenue),
            "total_payments": total_payments,
            "average_payment": float(total_revenue / total_payments) if total_payments > 0 else 0,
            "by_payment_method": by_method,
            "by_period": by_period
        }

    async def get_pending_payments(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Payment], int]:
        """Get all pending payments"""
        offset = (page - 1) * limit

        conditions = [
            Payment.school_id == school_id,
            Payment.status == 'pending',
            Payment.deleted_at.is_(None)
        ]

        # Count query
        count_query = select(func.count(Payment.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Payment).where(and_(*conditions)).options(
            selectinload(Payment.student).selectinload(Student.user),
            selectinload(Payment.student_fee)
        ).offset(offset).limit(limit).order_by(Payment.payment_date.desc())

        result = await self.session.execute(query)
        payments = result.scalars().all()

        return list(payments), total

    async def get_refunded_payments(
        self,
        school_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Payment], int]:
        """Get all refunded payments"""
        offset = (page - 1) * limit

        conditions = [
            Payment.school_id == school_id,
            Payment.status == 'refunded',
            Payment.deleted_at.is_(None)
        ]

        if start_date:
            conditions.append(Payment.refunded_at >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            conditions.append(Payment.refunded_at <= datetime.combine(end_date, datetime.max.time()))

        # Count query
        count_query = select(func.count(Payment.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Payment).where(and_(*conditions)).options(
            selectinload(Payment.student).selectinload(Student.user)
        ).offset(offset).limit(limit).order_by(desc(Payment.refunded_at))

        result = await self.session.execute(query)
        payments = result.scalars().all()

        return list(payments), total

    async def receipt_number_exists(
        self,
        receipt_number: str,
        exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if receipt number already exists"""
        conditions = [Payment.receipt_number == receipt_number]

        if exclude_id:
            conditions.append(Payment.id != exclude_id)

        query = select(func.count(Payment.id)).where(and_(*conditions))
        result = await self.session.execute(query)
        count = result.scalar()

        return count > 0
