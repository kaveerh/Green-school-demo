"""
Payment Controller

API endpoints for Payment CRUD operations and payment processing.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from services.payment_service import PaymentService
from schemas.payment_schema import (
    PaymentCreateSchema,
    PaymentPendingCreateSchema,
    PaymentConfirmSchema,
    PaymentRefundSchema,
    PaymentUpdateSchema,
    PaymentResponseSchema,
    PaymentListResponseSchema,
    PaymentReceiptSchema,
    RevenueReportSchema,
    PaymentMethodEnum,
    PaymentStatusEnum
)
from config.database import get_db
import uuid
import math


router = APIRouter(prefix="/payments", tags=["payments"])


# Dependency
async def get_payment_service(session: AsyncSession = Depends(get_db)) -> PaymentService:
    return PaymentService(session)


# 1. Create Payment
@router.post("", response_model=PaymentResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreateSchema,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Create a new payment and update student fee balance.

    Automatically:
    - Generates receipt number (RCPT-YYYY-NNNN)
    - Updates student fee balance
    - Updates fee status (pending → partial → paid)

    **Prevents overpayment**

    **Permissions:** Administrator, Accountant
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()

        payment = await service.create_payment(
            school_id=payment_data.school_id,
            student_fee_id=payment_data.student_fee_id,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method.value,
            processed_by_id=current_user_id,
            payment_date=payment_data.payment_date,
            transaction_reference=payment_data.transaction_reference,
            allocation_notes=payment_data.allocation_notes,
            notes=payment_data.notes,
            auto_generate_receipt=payment_data.auto_generate_receipt
        )

        return PaymentResponseSchema(**payment.to_dict(include_relationships=True))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {str(e)}"
        )


# 2. Create Pending Payment
@router.post("/pending", response_model=PaymentResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_pending_payment(
    payment_data: PaymentPendingCreateSchema,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Create a pending payment (authorization hold, pending check, etc).

    Does NOT update student fee balance until confirmed.

    **Permissions:** Administrator, Accountant
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()

        payment = await service.create_pending_payment(
            school_id=payment_data.school_id,
            student_fee_id=payment_data.student_fee_id,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method.value,
            processed_by_id=current_user_id,
            transaction_reference=payment_data.transaction_reference,
            notes=payment_data.notes
        )

        return PaymentResponseSchema(**payment.to_dict(include_relationships=True))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pending payment: {str(e)}"
        )


# 3. Confirm Pending Payment
@router.post("/{payment_id}/confirm", response_model=PaymentResponseSchema)
async def confirm_payment(
    payment_id: uuid.UUID,
    confirm_data: PaymentConfirmSchema,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Confirm a pending payment.

    - Changes status to 'completed'
    - Generates proper receipt number
    - Updates student fee balance

    **Permissions:** Administrator, Accountant
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()

        payment = await service.confirm_payment(
            payment_id=payment_id,
            updated_by_id=current_user_id,
            transaction_reference=confirm_data.transaction_reference
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        return PaymentResponseSchema(**payment.to_dict(include_relationships=True))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm payment: {str(e)}"
        )


# 4. Refund Payment
@router.post("/{payment_id}/refund", response_model=PaymentResponseSchema)
async def refund_payment(
    payment_id: uuid.UUID,
    refund_data: PaymentRefundSchema,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Process a payment refund.

    - Changes status to 'refunded'
    - Reverses student fee balance
    - Updates fee status

    **Can only refund completed payments**

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()

        payment = await service.refund_payment(
            payment_id=payment_id,
            refund_reason=refund_data.refund_reason,
            updated_by_id=current_user_id
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        return PaymentResponseSchema(**payment.to_dict(include_relationships=True))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refund payment: {str(e)}"
        )


# 5. Get Payment by ID
@router.get("/{payment_id}", response_model=PaymentResponseSchema)
async def get_payment(
    payment_id: uuid.UUID,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Get a specific payment by ID with relationships.

    **Permissions:** Administrator, Accountant, Parent (own children), Student (own only)
    """
    try:
        payment = await service.get_payment(payment_id, include_relationships=True)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        return PaymentResponseSchema(**payment.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment: {str(e)}"
        )


# 6. Get Payment by Receipt Number
@router.get("/receipt/{receipt_number}", response_model=PaymentResponseSchema)
async def get_payment_by_receipt(
    receipt_number: str,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Get a payment by receipt number.

    **Permissions:** Administrator, Accountant
    """
    try:
        payment = await service.get_payment_by_receipt(receipt_number)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        return PaymentResponseSchema(**payment.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment: {str(e)}"
        )


# 7. Generate Receipt Data
@router.get("/{payment_id}/receipt-data", response_model=PaymentReceiptSchema)
async def generate_receipt(
    payment_id: uuid.UUID,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Generate receipt data for printing/PDF.

    Returns all data needed for receipt generation.

    **Permissions:** Administrator, Accountant, Parent (own children), Student (own only)
    """
    try:
        receipt_data = await service.generate_receipt_data(payment_id)
        return PaymentReceiptSchema(**receipt_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate receipt: {str(e)}"
        )


# 8. List Payments
@router.get("", response_model=PaymentListResponseSchema)
async def list_payments(
    school_id: uuid.UUID = Query(...),
    status: Optional[PaymentStatusEnum] = None,
    payment_method: Optional[PaymentMethodEnum] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: PaymentService = Depends(get_payment_service)
):
    """
    List payments with filtering and pagination.

    **Filters:**
    - status: pending, completed, failed, refunded, cancelled
    - payment_method: cash, card, bank_transfer, check, online, other
    - start_date / end_date: Date range

    **Permissions:** Administrator, Accountant
    """
    try:
        payments, total = await service.list_payments(
            school_id=school_id,
            status=status.value if status else None,
            payment_method=payment_method.value if payment_method else None,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )

        pages = math.ceil(total / limit) if total > 0 else 0

        return PaymentListResponseSchema(
            data=[PaymentResponseSchema(**payment.to_dict(include_relationships=True)) for payment in payments],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list payments: {str(e)}"
        )


# 9. Get Student Payments
@router.get("/student/{student_id}", response_model=PaymentListResponseSchema)
async def get_student_payments(
    student_id: uuid.UUID,
    status: Optional[PaymentStatusEnum] = None,
    payment_method: Optional[PaymentMethodEnum] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: PaymentService = Depends(get_payment_service)
):
    """
    Get all payments for a student.

    **Permissions:** Administrator, Accountant, Parent (own children), Student (own only)
    """
    try:
        payments, total = await service.get_student_payments(
            student_id=student_id,
            status=status.value if status else None,
            payment_method=payment_method.value if payment_method else None,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )

        pages = math.ceil(total / limit) if total > 0 else 0

        return PaymentListResponseSchema(
            data=[PaymentResponseSchema(**payment.to_dict(include_relationships=True)) for payment in payments],
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student payments: {str(e)}"
        )


# 10. Get Revenue Report
@router.get("/reports/revenue", response_model=RevenueReportSchema)
async def get_revenue_report(
    school_id: uuid.UUID = Query(...),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    group_by: str = Query("month", regex="^(day|month|year)$"),
    service: PaymentService = Depends(get_payment_service)
):
    """
    Get revenue report with analytics.

    **group_by:** day, month, or year

    Returns:
    - Total revenue
    - Payment count
    - Average payment
    - Breakdown by payment method
    - Time series data

    **Permissions:** Administrator, Accountant
    """
    try:
        report = await service.get_revenue_report(
            school_id=school_id,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )

        return RevenueReportSchema(**report)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate revenue report: {str(e)}"
        )


# 11. Update Payment
@router.put("/{payment_id}", response_model=PaymentResponseSchema)
async def update_payment(
    payment_id: uuid.UUID,
    payment_data: PaymentUpdateSchema,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Update payment details (limited fields).

    Can update: transaction_reference, allocation_notes, notes

    **Cannot update amount or payment_method**

    **Permissions:** Administrator, Accountant
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()

        updated_payment = await service.update_payment(
            payment_id=payment_id,
            updated_by_id=current_user_id,
            transaction_reference=payment_data.transaction_reference,
            allocation_notes=payment_data.allocation_notes,
            notes=payment_data.notes
        )

        if not updated_payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        return PaymentResponseSchema(**updated_payment.to_dict(include_relationships=True))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update payment: {str(e)}"
        )


# 12. Delete Payment (Pending Only)
@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: uuid.UUID,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Delete payment (soft delete).

    **Only for pending payments**
    Use refund endpoint for completed payments.

    **Permissions:** Administrator
    """
    try:
        # TODO: Get current_user_id from auth
        current_user_id = uuid.uuid4()

        success = await service.delete_payment(payment_id, current_user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete payment: {str(e)}"
        )
