"""
Activity Service

Business logic layer for Activity and ActivityEnrollment operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.activity_repository import ActivityRepository, ActivityEnrollmentRepository
from repositories.student_repository import StudentRepository
from repositories.user_repository import UserRepository
from models.activity import Activity, ActivityEnrollment
from models.student import Student
from datetime import date
from decimal import Decimal
import uuid


class ActivityService:
    """Service layer for Activity business logic"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ActivityRepository(session)
        self.enrollment_repository = ActivityEnrollmentRepository(session)
        self.student_repository = StudentRepository(session)
        self.user_repository = UserRepository(session)

    async def create_activity(
        self,
        school_id: uuid.UUID,
        name: str,
        activity_type: str,
        grade_levels: List[int],
        created_by_id: uuid.UUID,
        code: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        coordinator_id: Optional[uuid.UUID] = None,
        max_participants: Optional[int] = None,
        min_participants: Optional[int] = None,
        schedule: Optional[Dict] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        location: Optional[str] = None,
        room_id: Optional[uuid.UUID] = None,
        cost: float = 0.00,
        registration_fee: float = 0.00,
        equipment_fee: float = 0.00,
        requirements: Optional[List[str]] = None,
        equipment_needed: Optional[List[str]] = None,
        uniform_required: bool = False,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None,
        parent_info: Optional[str] = None,
        status: str = "active",
        is_featured: bool = False,
        registration_open: bool = True,
        photo_url: Optional[str] = None,
        color: Optional[str] = None
    ) -> Activity:
        """Create a new activity"""

        # Validate activity type
        valid_types = ['sports', 'club', 'art', 'music', 'academic', 'other']
        if activity_type not in valid_types:
            raise ValueError(f"Invalid activity type. Must be one of: {', '.join(valid_types)}")

        # Validate status
        valid_statuses = ['active', 'full', 'cancelled', 'completed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        # Validate grade levels
        if not grade_levels or not all(1 <= g <= 7 for g in grade_levels):
            raise ValueError("Grade levels must be between 1 and 7")

        # Validate dates
        if start_date and end_date and end_date < start_date:
            raise ValueError("End date must be on or after start date")

        # Validate participant limits
        if max_participants and max_participants <= 0:
            raise ValueError("Max participants must be positive")
        if min_participants and min_participants <= 0:
            raise ValueError("Min participants must be positive")
        if max_participants and min_participants and min_participants > max_participants:
            raise ValueError("Min participants cannot exceed max participants")

        # Validate costs
        if cost < 0 or registration_fee < 0 or equipment_fee < 0:
            raise ValueError("Costs must be non-negative")

        # Validate coordinator
        if coordinator_id:
            coordinator = await self.user_repository.get_by_id(coordinator_id)
            if not coordinator:
                raise ValueError("Coordinator user not found")
            if coordinator.school_id != school_id:
                raise ValueError("Coordinator must belong to same school")

        # Check for duplicate code
        if code:
            existing = await self.repository.get_by_code(school_id, code)
            if existing:
                raise ValueError(f"Activity with code '{code}' already exists")

        activity_data = {
            'school_id': school_id,
            'name': name,
            'code': code,
            'activity_type': activity_type,
            'category': category,
            'description': description,
            'coordinator_id': coordinator_id,
            'grade_levels': grade_levels,
            'max_participants': max_participants,
            'min_participants': min_participants,
            'schedule': schedule or {},
            'start_date': start_date,
            'end_date': end_date,
            'location': location,
            'room_id': room_id,
            'cost': Decimal(str(cost)),
            'registration_fee': Decimal(str(registration_fee)),
            'equipment_fee': Decimal(str(equipment_fee)),
            'requirements': requirements,
            'equipment_needed': equipment_needed,
            'uniform_required': uniform_required,
            'contact_email': contact_email,
            'contact_phone': contact_phone,
            'parent_info': parent_info,
            'status': status,
            'is_featured': is_featured,
            'registration_open': registration_open,
            'photo_url': photo_url,
            'color': color
        }

        return await self.repository.create(activity_data, created_by_id)

    async def update_activity(
        self,
        activity_id: uuid.UUID,
        updated_by_id: uuid.UUID,
        **updates
    ) -> Optional[Activity]:
        """Update an activity"""
        activity = await self.repository.get_by_id(activity_id)
        if not activity:
            return None

        # Validate dates if being updated
        start_date = updates.get('start_date', activity.start_date)
        end_date = updates.get('end_date', activity.end_date)

        if start_date and end_date and end_date < start_date:
            raise ValueError("End date must be on or after start date")

        # Validate activity type if being updated
        if 'activity_type' in updates:
            valid_types = ['sports', 'club', 'art', 'music', 'academic', 'other']
            if updates['activity_type'] not in valid_types:
                raise ValueError(f"Invalid activity type. Must be one of: {', '.join(valid_types)}")

        # Validate status if being updated
        if 'status' in updates:
            valid_statuses = ['active', 'full', 'cancelled', 'completed']
            if updates['status'] not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        # Convert costs to Decimal if provided
        for cost_field in ['cost', 'registration_fee', 'equipment_fee']:
            if cost_field in updates and updates[cost_field] is not None:
                updates[cost_field] = Decimal(str(updates[cost_field]))

        return await self.repository.update(activity_id, updates, updated_by_id)

    async def delete_activity(
        self,
        activity_id: uuid.UUID,
        deleted_by_id: uuid.UUID
    ) -> bool:
        """Soft delete an activity"""
        # Check if activity has active enrollments
        enrollments = await self.enrollment_repository.get_by_activity(
            activity_id, status='active'
        )
        if enrollments:
            raise ValueError("Cannot delete activity with active enrollments. Withdraw students first.")

        return await self.repository.delete(activity_id, deleted_by_id)

    async def enroll_student(
        self,
        activity_id: uuid.UUID,
        student_id: uuid.UUID,
        parent_consent: bool = False,
        medical_clearance: bool = False,
        emergency_contact_provided: bool = False,
        created_by_id: Optional[uuid.UUID] = None
    ) -> ActivityEnrollment:
        """Enroll a student in an activity"""

        # Get activity with relationships
        activity = await self.repository.get_with_relationships(activity_id)
        if not activity:
            raise ValueError("Activity not found")

        # Check if activity is accepting registrations
        if not activity.registration_open:
            raise ValueError("Activity registration is closed")

        if activity.status not in ['active', 'full']:
            raise ValueError(f"Cannot enroll in {activity.status} activity")

        # Get student
        student = await self.student_repository.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

        # Check if student's school matches activity's school
        if student.school_id != activity.school_id:
            raise ValueError("Student and activity must belong to same school")

        # Check if student's grade level is eligible
        if student.grade_level not in activity.grade_levels:
            raise ValueError(f"Activity is not available for grade {student.grade_level}")

        # Check if already enrolled
        existing = await self.enrollment_repository.check_enrollment_exists(
            activity_id, student_id
        )
        if existing and existing.status in ['active', 'waitlisted']:
            raise ValueError("Student is already enrolled in this activity")

        # Check capacity
        active_count = await self.enrollment_repository.count_active_enrollments(activity_id)
        status = 'active'
        if activity.max_participants and active_count >= activity.max_participants:
            # Add to waitlist instead
            status = 'waitlisted'

        # Calculate total cost
        total_cost = float(activity.cost or 0) + float(activity.registration_fee or 0) + float(activity.equipment_fee or 0)

        enrollment_data = {
            'activity_id': activity_id,
            'student_id': student_id,
            'enrollment_date': date.today(),
            'status': status,
            'payment_status': 'pending' if total_cost > 0 else 'paid',
            'amount_paid': Decimal('0.00'),
            'parent_consent': parent_consent,
            'parent_consent_date': date.today() if parent_consent else None,
            'medical_clearance': medical_clearance,
            'emergency_contact_provided': emergency_contact_provided
        }

        enrollment = await self.enrollment_repository.create(enrollment_data, created_by_id)

        # Update activity status to full if needed
        if status == 'active':
            new_count = await self.enrollment_repository.count_active_enrollments(activity_id)
            if activity.max_participants and new_count >= activity.max_participants:
                await self.repository.update(
                    activity_id,
                    {'status': 'full'},
                    created_by_id
                )

        return enrollment

    async def withdraw_student(
        self,
        activity_id: uuid.UUID,
        student_id: uuid.UUID,
        withdrawn_by_id: uuid.UUID,
        reason: Optional[str] = None
    ) -> Optional[ActivityEnrollment]:
        """Withdraw a student from an activity"""

        # Get enrollment
        enrollment = await self.enrollment_repository.check_enrollment_exists(
            activity_id, student_id
        )
        if not enrollment:
            raise ValueError("Enrollment not found")

        if enrollment.status == 'withdrawn':
            raise ValueError("Student is already withdrawn")

        # Update enrollment
        updates = {
            'status': 'withdrawn',
            'withdrawn_at': date.today(),
            'withdrawn_by': withdrawn_by_id,
            'withdrawn_reason': reason
        }

        enrollment = await self.enrollment_repository.update(
            enrollment.id, updates, withdrawn_by_id
        )

        # Check if we can move someone from waitlist to active
        activity = await self.repository.get_by_id(activity_id)
        if activity and enrollment.status != 'waitlisted':
            active_count = await self.enrollment_repository.count_active_enrollments(activity_id)

            # If there are spots available and waitlisted students
            if not activity.max_participants or active_count < activity.max_participants:
                waitlisted = await self.enrollment_repository.get_waitlisted(activity_id)
                if waitlisted:
                    # Activate first person on waitlist
                    first_waitlist = waitlisted[0]
                    await self.enrollment_repository.update(
                        first_waitlist.id,
                        {'status': 'active'},
                        withdrawn_by_id
                    )

                # Update activity status if no longer full
                if activity.status == 'full':
                    await self.repository.update(
                        activity_id,
                        {'status': 'active'},
                        withdrawn_by_id
                    )

        return enrollment

    async def record_payment(
        self,
        enrollment_id: uuid.UUID,
        amount: float,
        updated_by_id: uuid.UUID,
        payment_date: Optional[date] = None
    ) -> Optional[ActivityEnrollment]:
        """Record a payment for an enrollment"""

        enrollment = await self.enrollment_repository.get_with_relationships(enrollment_id)
        if not enrollment:
            raise ValueError("Enrollment not found")

        if amount < 0:
            raise ValueError("Payment amount must be non-negative")

        # Calculate total cost and new amount paid
        activity = enrollment.activity
        total_cost = float(activity.cost or 0) + float(activity.registration_fee or 0) + float(activity.equipment_fee or 0)
        new_amount_paid = float(enrollment.amount_paid or 0) + amount

        # Determine payment status
        if new_amount_paid >= total_cost:
            payment_status = 'paid'
            new_amount_paid = total_cost  # Don't allow overpayment
        elif new_amount_paid > 0:
            payment_status = 'partial'
        else:
            payment_status = 'pending'

        updates = {
            'amount_paid': Decimal(str(new_amount_paid)),
            'payment_status': payment_status,
            'payment_date': payment_date or date.today()
        }

        return await self.enrollment_repository.update(enrollment_id, updates, updated_by_id)

    async def waive_payment(
        self,
        enrollment_id: uuid.UUID,
        updated_by_id: uuid.UUID
    ) -> Optional[ActivityEnrollment]:
        """Waive payment for an enrollment"""

        enrollment = await self.enrollment_repository.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError("Enrollment not found")

        updates = {
            'payment_status': 'waived',
            'payment_date': date.today()
        }

        return await self.enrollment_repository.update(enrollment_id, updates, updated_by_id)

    async def update_consent(
        self,
        enrollment_id: uuid.UUID,
        parent_consent: bool,
        updated_by_id: uuid.UUID
    ) -> Optional[ActivityEnrollment]:
        """Update parent consent for an enrollment"""

        enrollment = await self.enrollment_repository.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError("Enrollment not found")

        updates = {
            'parent_consent': parent_consent,
            'parent_consent_date': date.today() if parent_consent else None
        }

        return await self.enrollment_repository.update(enrollment_id, updates, updated_by_id)

    async def get_activity_roster(
        self,
        activity_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get complete roster for an activity"""

        activity = await self.repository.get_with_relationships(activity_id)
        if not activity:
            raise ValueError("Activity not found")

        active_enrollments = await self.enrollment_repository.get_by_activity(
            activity_id, status='active'
        )

        waitlisted = await self.enrollment_repository.get_waitlisted(activity_id)

        return {
            'activity': activity.to_dict(include_relationships=True),
            'active_enrollments': [e.to_dict(include_relationships=True) for e in active_enrollments],
            'waitlisted_enrollments': [e.to_dict(include_relationships=True) for e in waitlisted],
            'total_enrolled': len(active_enrollments),
            'total_waitlisted': len(waitlisted),
            'available_slots': activity.available_slots
        }

    async def get_student_activities(
        self,
        student_id: uuid.UUID,
        status: Optional[str] = None
    ) -> List[ActivityEnrollment]:
        """Get all activities for a student"""
        return await self.enrollment_repository.get_by_student(student_id, status)

    async def get_payment_summary(
        self,
        activity_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get payment summary for an activity"""

        enrollments = await self.enrollment_repository.get_by_activity(activity_id)

        total_expected = 0
        total_collected = 0
        total_outstanding = 0
        payment_breakdown = {
            'paid': 0,
            'partial': 0,
            'pending': 0,
            'waived': 0
        }

        activity = await self.repository.get_by_id(activity_id)
        activity_cost = float(activity.cost or 0) + float(activity.registration_fee or 0) + float(activity.equipment_fee or 0)

        for enrollment in enrollments:
            if enrollment.status == 'active':
                if enrollment.payment_status != 'waived':
                    total_expected += activity_cost
                    total_collected += float(enrollment.amount_paid or 0)
                    if enrollment.payment_status in ['pending', 'partial']:
                        total_outstanding += (activity_cost - float(enrollment.amount_paid or 0))

                payment_breakdown[enrollment.payment_status] += 1

        return {
            'activity_id': str(activity_id),
            'activity_name': activity.name,
            'total_expected': total_expected,
            'total_collected': total_collected,
            'total_outstanding': total_outstanding,
            'payment_breakdown': payment_breakdown
        }

    async def get_statistics(
        self,
        school_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get activity statistics for a school"""
        return await self.repository.get_statistics(school_id)
