"""
Parent Repository

Data access layer for Parent operations with specialized queries.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from models.parent import Parent
from models.user import User
from models.student import Student, ParentStudentRelationship
from repositories.base_repository import BaseRepository
import uuid


class ParentRepository(BaseRepository[Parent]):
    """Repository for Parent data access"""

    def __init__(self, session: AsyncSession):
        super().__init__(Parent, session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Parent]:
        """Get parent by user_id"""
        query = select(Parent).where(
            and_(
                Parent.user_id == user_id,
                Parent.deleted_at.is_(None)
            )
        ).options(
            selectinload(Parent.user),
            selectinload(Parent.student_relationships)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_relationships(self, parent_id: uuid.UUID) -> Optional[Parent]:
        """Get parent with all relationships loaded"""
        query = select(Parent).where(
            and_(
                Parent.id == parent_id,
                Parent.deleted_at.is_(None)
            )
        ).options(
            selectinload(Parent.user),
            selectinload(Parent.school),
            selectinload(Parent.student_relationships).selectinload(ParentStudentRelationship.student).selectinload(Student.user)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Parent], int]:
        """Get all parents for a school with pagination"""
        offset = (page - 1) * limit

        # Count query
        count_query = select(func.count(Parent.id)).where(
            and_(
                Parent.school_id == school_id,
                Parent.deleted_at.is_(None)
            )
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Parent).where(
            and_(
                Parent.school_id == school_id,
                Parent.deleted_at.is_(None)
            )
        ).options(
            selectinload(Parent.user)
        ).offset(offset).limit(limit).order_by(Parent.created_at.desc())

        result = await self.session.execute(query)
        parents = result.scalars().all()

        return list(parents), total

    async def search_parents(
        self,
        school_id: uuid.UUID,
        search_query: str,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Parent], int]:
        """
        Search parents by name, email, or phone

        Args:
            school_id: School UUID
            search_query: Search term
            page: Page number (1-indexed)
            limit: Results per page

        Returns:
            Tuple of (parents list, total count)
        """
        offset = (page - 1) * limit
        search_pattern = f"%{search_query.lower()}%"

        # Build search conditions
        search_conditions = or_(
            func.lower(User.first_name).like(search_pattern),
            func.lower(User.last_name).like(search_pattern),
            func.lower(User.email).like(search_pattern),
            func.lower(Parent.phone_mobile).like(search_pattern),
            func.lower(Parent.phone_work).like(search_pattern),
            func.lower(Parent.occupation).like(search_pattern),
            func.lower(Parent.workplace).like(search_pattern)
        )

        # Count query
        count_query = select(func.count(Parent.id)).join(
            User, Parent.user_id == User.id
        ).where(
            and_(
                Parent.school_id == school_id,
                Parent.deleted_at.is_(None),
                search_conditions
            )
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Parent).join(
            User, Parent.user_id == User.id
        ).where(
            and_(
                Parent.school_id == school_id,
                Parent.deleted_at.is_(None),
                search_conditions
            )
        ).options(
            selectinload(Parent.user)
        ).offset(offset).limit(limit).order_by(Parent.created_at.desc())

        result = await self.session.execute(query)
        parents = result.scalars().all()

        return list(parents), total

    async def get_emergency_contacts(self, school_id: uuid.UUID) -> List[Parent]:
        """Get all parents marked as emergency contacts"""
        query = select(Parent).where(
            and_(
                Parent.school_id == school_id,
                Parent.emergency_contact == True,
                Parent.deleted_at.is_(None)
            )
        ).options(
            selectinload(Parent.user)
        ).order_by(User.last_name, User.first_name)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pickup_authorized(self, school_id: uuid.UUID) -> List[Parent]:
        """Get all parents authorized for pickup"""
        query = select(Parent).where(
            and_(
                Parent.school_id == school_id,
                Parent.pickup_authorized == True,
                Parent.deleted_at.is_(None)
            )
        ).options(
            selectinload(Parent.user)
        ).order_by(User.last_name, User.first_name)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_newsletter_subscribers(self, school_id: uuid.UUID) -> List[Parent]:
        """Get all parents subscribed to newsletter"""
        query = select(Parent).where(
            and_(
                Parent.school_id == school_id,
                Parent.receives_newsletter == True,
                Parent.deleted_at.is_(None)
            )
        ).options(
            selectinload(Parent.user)
        ).order_by(User.last_name, User.first_name)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_student(self, student_id: uuid.UUID) -> List[Parent]:
        """Get all parents for a specific student"""
        query = select(Parent).join(
            ParentStudentRelationship,
            Parent.id == ParentStudentRelationship.parent_id
        ).where(
            and_(
                ParentStudentRelationship.student_id == student_id,
                ParentStudentRelationship.deleted_at.is_(None),
                Parent.deleted_at.is_(None)
            )
        ).options(
            selectinload(Parent.user),
            selectinload(Parent.student_relationships)
        ).order_by(User.last_name, User.first_name)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_children(self, parent_id: uuid.UUID) -> List[Student]:
        """Get all children (students) for a parent"""
        query = select(Student).join(
            ParentStudentRelationship,
            Student.id == ParentStudentRelationship.student_id
        ).where(
            and_(
                ParentStudentRelationship.parent_id == parent_id,
                ParentStudentRelationship.deleted_at.is_(None),
                Student.deleted_at.is_(None)
            )
        ).options(
            selectinload(Student.user)
        ).order_by(Student.grade_level, User.last_name, User.first_name)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_relationship(
        self,
        parent_id: uuid.UUID,
        student_id: uuid.UUID
    ) -> Optional[ParentStudentRelationship]:
        """Get a specific parent-student relationship"""
        query = select(ParentStudentRelationship).where(
            and_(
                ParentStudentRelationship.parent_id == parent_id,
                ParentStudentRelationship.student_id == student_id,
                ParentStudentRelationship.deleted_at.is_(None)
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_relationship(
        self,
        parent_id: uuid.UUID,
        student_id: uuid.UUID,
        relationship_type: str,
        is_primary_contact: bool = False,
        has_pickup_permission: bool = True,
        created_by_id: Optional[uuid.UUID] = None
    ) -> ParentStudentRelationship:
        """Create a parent-student relationship"""
        relationship = ParentStudentRelationship(
            parent_id=parent_id,
            student_id=student_id,
            relationship_type=relationship_type,
            is_primary_contact=is_primary_contact,
            has_pickup_permission=has_pickup_permission,
            created_by=created_by_id,
            updated_by=created_by_id
        )

        self.session.add(relationship)
        await self.session.flush()
        await self.session.refresh(relationship)

        return relationship

    async def delete_relationship(
        self,
        parent_id: uuid.UUID,
        student_id: uuid.UUID,
        deleted_by_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Soft delete a parent-student relationship"""
        relationship = await self.get_relationship(parent_id, student_id)

        if not relationship:
            return False

        relationship.soft_delete(deleted_by_id)
        await self.session.flush()

        return True

    async def get_statistics(self, school_id: uuid.UUID) -> Dict[str, Any]:
        """Get parent statistics for a school"""
        # Total parents
        total_query = select(func.count(Parent.id)).where(
            and_(
                Parent.school_id == school_id,
                Parent.deleted_at.is_(None)
            )
        )
        total_result = await self.session.execute(total_query)
        total_parents = total_result.scalar()

        # Emergency contacts
        emergency_query = select(func.count(Parent.id)).where(
            and_(
                Parent.school_id == school_id,
                Parent.emergency_contact == True,
                Parent.deleted_at.is_(None)
            )
        )
        emergency_result = await self.session.execute(emergency_query)
        emergency_contacts = emergency_result.scalar()

        # Pickup authorized
        pickup_query = select(func.count(Parent.id)).where(
            and_(
                Parent.school_id == school_id,
                Parent.pickup_authorized == True,
                Parent.deleted_at.is_(None)
            )
        )
        pickup_result = await self.session.execute(pickup_query)
        pickup_authorized = pickup_result.scalar()

        # Newsletter subscribers
        newsletter_query = select(func.count(Parent.id)).where(
            and_(
                Parent.school_id == school_id,
                Parent.receives_newsletter == True,
                Parent.deleted_at.is_(None)
            )
        )
        newsletter_result = await self.session.execute(newsletter_query)
        newsletter_subscribers = newsletter_result.scalar()

        # Parents with children
        with_children_query = select(func.count(func.distinct(ParentStudentRelationship.parent_id))).where(
            and_(
                ParentStudentRelationship.deleted_at.is_(None),
                Parent.school_id == school_id,
                Parent.deleted_at.is_(None)
            )
        ).select_from(ParentStudentRelationship).join(Parent)
        with_children_result = await self.session.execute(with_children_query)
        parents_with_children = with_children_result.scalar()

        # Parents without children
        parents_without_children = total_parents - parents_with_children

        return {
            "total_parents": total_parents,
            "emergency_contacts": emergency_contacts,
            "pickup_authorized": pickup_authorized,
            "newsletter_subscribers": newsletter_subscribers,
            "parents_with_children": parents_with_children,
            "parents_without_children": parents_without_children
        }
