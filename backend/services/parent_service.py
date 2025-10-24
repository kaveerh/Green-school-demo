"""
Parent Service

Business logic layer for Parent operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.parent_repository import ParentRepository
from repositories.user_repository import UserRepository
from repositories.student_repository import StudentRepository
from models.parent import Parent
from models.student import Student, ParentStudentRelationship
import uuid


class ParentService:
    """Service layer for Parent business logic"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ParentRepository(session)
        self.user_repository = UserRepository(session)
        self.student_repository = StudentRepository(session)

    async def create_parent(
        self,
        school_id: uuid.UUID,
        user_id: uuid.UUID,
        created_by_id: uuid.UUID,
        occupation: Optional[str] = None,
        workplace: Optional[str] = None,
        phone_mobile: Optional[str] = None,
        phone_work: Optional[str] = None,
        preferred_contact_method: Optional[str] = None,
        emergency_contact: bool = False,
        pickup_authorized: bool = False,
        receives_newsletter: bool = True
    ) -> Parent:
        """
        Create a new parent

        Args:
            school_id: School UUID
            user_id: User account UUID (must have 'parent' persona)
            created_by_id: UUID of user creating the record
            ... other parent fields

        Returns:
            Created Parent object

        Raises:
            ValueError: If user doesn't exist or doesn't have parent persona
        """
        # Validate user exists and has parent persona
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if user.persona != "parent":
            raise ValueError(f"User must have 'parent' persona, found '{user.persona}'")

        if user.school_id != school_id:
            raise ValueError("User must belong to the same school")

        # Check if parent already exists for this user
        existing = await self.repository.get_by_user_id(user_id)
        if existing:
            raise ValueError("Parent record already exists for this user")

        # Validate contact method if provided
        if preferred_contact_method and preferred_contact_method not in ['email', 'phone', 'sms', 'app_notification']:
            raise ValueError(f"Invalid preferred_contact_method: {preferred_contact_method}")

        # Create parent
        parent_data = {
            'school_id': school_id,
            'user_id': user_id,
            'occupation': occupation,
            'workplace': workplace,
            'phone_mobile': phone_mobile,
            'phone_work': phone_work,
            'preferred_contact_method': preferred_contact_method,
            'emergency_contact': emergency_contact,
            'pickup_authorized': pickup_authorized,
            'receives_newsletter': receives_newsletter
        }

        return await self.repository.create(parent_data, created_by_id)

    async def get_parent_by_id(self, parent_id: uuid.UUID) -> Optional[Parent]:
        """Get parent by ID with relationships"""
        return await self.repository.get_with_relationships(parent_id)

    async def get_parent_by_user_id(self, user_id: uuid.UUID) -> Optional[Parent]:
        """Get parent by user ID"""
        return await self.repository.get_by_user_id(user_id)

    async def get_parents_by_school(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Parent], int]:
        """Get all parents for a school with pagination"""
        return await self.repository.get_by_school(school_id, page, limit)

    async def search_parents(
        self,
        school_id: uuid.UUID,
        search_query: str,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Parent], int]:
        """Search parents by name, email, or phone"""
        if not search_query or len(search_query.strip()) < 2:
            raise ValueError("Search query must be at least 2 characters")

        return await self.repository.search_parents(school_id, search_query, page, limit)

    async def update_parent(
        self,
        parent_id: uuid.UUID,
        updated_by_id: uuid.UUID,
        occupation: Optional[str] = None,
        workplace: Optional[str] = None,
        phone_mobile: Optional[str] = None,
        phone_work: Optional[str] = None,
        preferred_contact_method: Optional[str] = None,
        emergency_contact: Optional[bool] = None,
        pickup_authorized: Optional[bool] = None,
        receives_newsletter: Optional[bool] = None
    ) -> Optional[Parent]:
        """
        Update parent information

        Args:
            parent_id: Parent UUID
            updated_by_id: UUID of user updating the record
            ... optional fields to update

        Returns:
            Updated Parent object or None if not found
        """
        parent = await self.repository.get_by_id(parent_id)
        if not parent:
            return None

        # Validate contact method if provided
        if preferred_contact_method and preferred_contact_method not in ['email', 'phone', 'sms', 'app_notification']:
            raise ValueError(f"Invalid preferred_contact_method: {preferred_contact_method}")

        # Update fields
        if occupation is not None:
            parent.occupation = occupation
        if workplace is not None:
            parent.workplace = workplace
        if phone_mobile is not None:
            parent.phone_mobile = phone_mobile
        if phone_work is not None:
            parent.phone_work = phone_work
        if preferred_contact_method is not None:
            parent.preferred_contact_method = preferred_contact_method
        if emergency_contact is not None:
            parent.emergency_contact = emergency_contact
        if pickup_authorized is not None:
            parent.pickup_authorized = pickup_authorized
        if receives_newsletter is not None:
            parent.receives_newsletter = receives_newsletter

        parent.updated_by = updated_by_id

        return await self.repository.update(parent)

    async def delete_parent(
        self,
        parent_id: uuid.UUID,
        deleted_by_id: uuid.UUID
    ) -> bool:
        """
        Soft delete a parent

        This will also soft delete all parent-student relationships.
        """
        parent = await self.repository.get_by_id(parent_id)
        if not parent:
            return False

        return await self.repository.delete(parent_id, deleted_by_id)

    async def link_student(
        self,
        parent_id: uuid.UUID,
        student_id: uuid.UUID,
        relationship_type: str,
        created_by_id: uuid.UUID,
        is_primary_contact: bool = False,
        has_pickup_permission: bool = True
    ) -> ParentStudentRelationship:
        """
        Link a parent to a student

        Args:
            parent_id: Parent UUID
            student_id: Student UUID
            relationship_type: Type of relationship (mother, father, guardian, etc.)
            created_by_id: UUID of user creating the link
            is_primary_contact: Whether this parent is the primary contact
            has_pickup_permission: Whether parent can pick up student

        Returns:
            Created ParentStudentRelationship

        Raises:
            ValueError: If parent or student not found, or if they're in different schools
        """
        # Validate parent exists
        parent = await self.repository.get_by_id(parent_id)
        if not parent:
            raise ValueError("Parent not found")

        # Validate student exists
        student = await self.student_repository.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

        # Validate same school
        if parent.school_id != student.school_id:
            raise ValueError("Parent and student must be in the same school")

        # Validate relationship type
        valid_types = ['mother', 'father', 'guardian', 'stepmother', 'stepfather',
                      'grandparent', 'foster_parent', 'other']
        if relationship_type not in valid_types:
            raise ValueError(f"Invalid relationship_type. Must be one of: {', '.join(valid_types)}")

        # Check if relationship already exists
        existing = await self.repository.get_relationship(parent_id, student_id)
        if existing:
            raise ValueError("Relationship already exists between this parent and student")

        # Create relationship
        return await self.repository.create_relationship(
            parent_id=parent_id,
            student_id=student_id,
            relationship_type=relationship_type,
            is_primary_contact=is_primary_contact,
            has_pickup_permission=has_pickup_permission,
            created_by_id=created_by_id
        )

    async def unlink_student(
        self,
        parent_id: uuid.UUID,
        student_id: uuid.UUID,
        deleted_by_id: uuid.UUID
    ) -> bool:
        """Remove parent-student relationship"""
        return await self.repository.delete_relationship(parent_id, student_id, deleted_by_id)

    async def get_parent_children(self, parent_id: uuid.UUID) -> List[Student]:
        """Get all children for a parent"""
        parent = await self.repository.get_by_id(parent_id)
        if not parent:
            raise ValueError("Parent not found")

        return await self.repository.get_children(parent_id)

    async def get_student_parents(self, student_id: uuid.UUID) -> List[Parent]:
        """Get all parents for a student"""
        student = await self.student_repository.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

        return await self.repository.get_by_student(student_id)

    async def get_emergency_contacts(self, school_id: uuid.UUID) -> List[Parent]:
        """Get all parents marked as emergency contacts"""
        return await self.repository.get_emergency_contacts(school_id)

    async def get_pickup_authorized(self, school_id: uuid.UUID) -> List[Parent]:
        """Get all parents authorized for pickup"""
        return await self.repository.get_pickup_authorized(school_id)

    async def get_newsletter_subscribers(self, school_id: uuid.UUID) -> List[Parent]:
        """Get all parents subscribed to newsletter"""
        return await self.repository.get_newsletter_subscribers(school_id)

    async def get_statistics(self, school_id: uuid.UUID) -> Dict[str, Any]:
        """Get parent statistics for a school"""
        return await self.repository.get_statistics(school_id)
