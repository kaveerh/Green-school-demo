"""
Student Service
Business logic for student operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple
from datetime import date
import uuid

from models.student import Student, ParentStudentRelationship
from repositories.student_repository import StudentRepository, ParentStudentRelationshipRepository
from schemas.student_schema import (
    StudentCreateSchema,
    StudentUpdateSchema,
    StudentSearchSchema,
    ParentStudentLinkSchema
)


class StudentService:
    """Service for student business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = StudentRepository(db)
        self.relationship_repository = ParentStudentRelationshipRepository(db)

    async def create_student(
        self,
        student_data: StudentCreateSchema,
        created_by_id: uuid.UUID
    ) -> Student:
        """
        Create a new student

        Args:
            student_data: Student creation data
            created_by_id: ID of user creating the student

        Returns:
            Created student

        Raises:
            ValueError: If validation fails
        """
        # Check if student_id already exists in school
        existing = await self.repository.get_by_student_id(
            student_data.school_id,
            student_data.student_id
        )
        if existing:
            raise ValueError(f"Student ID {student_data.student_id} already exists in this school")

        # Check if user_id is already assigned to a student
        existing_user = await self.repository.get_by_user_id(student_data.user_id)
        if existing_user:
            raise ValueError(f"User ID is already assigned to another student")

        # Validate age (must be between 5 and 15 for primary school)
        if student_data.date_of_birth:
            age = (date.today() - student_data.date_of_birth).days // 365
            if age < 5 or age > 15:
                raise ValueError(f"Student age ({age}) is outside typical primary school range (5-15)")

        # Create student
        student_dict = student_data.model_dump()
        student_dict['created_by'] = created_by_id

        student = await self.repository.create(student_dict)
        await self.db.commit()
        await self.db.refresh(student)

        return student

    async def get_student(self, student_id: uuid.UUID) -> Optional[Student]:
        """Get student by ID"""
        return await self.repository.get_by_id(student_id)

    async def get_student_by_student_id(
        self,
        school_id: uuid.UUID,
        student_id: str
    ) -> Optional[Student]:
        """Get student by student_id within a school"""
        return await self.repository.get_by_student_id(school_id, student_id)

    async def get_student_by_user_id(self, user_id: uuid.UUID) -> Optional[Student]:
        """Get student by user_id"""
        return await self.repository.get_by_user_id(user_id)

    async def get_enrolled_students(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Student], dict]:
        """Get all currently enrolled students"""
        return await self.repository.get_enrolled_students(school_id, page, limit)

    async def get_students_by_grade(
        self,
        school_id: uuid.UUID,
        grade_level: int,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Student], dict]:
        """Get students by grade level"""
        if grade_level < 1 or grade_level > 7:
            raise ValueError("Grade level must be between 1 and 7")

        return await self.repository.get_by_grade_level(school_id, grade_level, page, limit)

    async def search_students(
        self,
        school_id: uuid.UUID,
        search_params: StudentSearchSchema
    ) -> Tuple[List[Student], dict]:
        """Search students with filters"""
        return await self.repository.search_students(
            school_id=school_id,
            search=search_params.search,
            grade_level=search_params.grade_level,
            status=search_params.status,
            gender=search_params.gender,
            page=search_params.page,
            limit=search_params.limit,
            sort=search_params.sort,
            order=search_params.order
        )

    async def update_student(
        self,
        student_id: uuid.UUID,
        student_data: StudentUpdateSchema,
        updated_by_id: uuid.UUID
    ) -> Optional[Student]:
        """
        Update student information

        Args:
            student_id: Student UUID
            student_data: Update data
            updated_by_id: ID of user updating the student

        Returns:
            Updated student or None if not found
        """
        student = await self.repository.get_by_id(student_id)
        if not student:
            return None

        # Validate grade level if being updated
        if student_data.grade_level is not None:
            if student_data.grade_level < 1 or student_data.grade_level > 7:
                raise ValueError("Grade level must be between 1 and 7")

        update_dict = student_data.model_dump(exclude_unset=True)
        update_dict['updated_by'] = updated_by_id

        updated_student = await self.repository.update(student_id, update_dict)
        await self.db.commit()
        await self.db.refresh(updated_student)

        return updated_student

    async def delete_student(
        self,
        student_id: uuid.UUID,
        deleted_by_id: uuid.UUID
    ) -> bool:
        """
        Soft delete a student

        Args:
            student_id: Student UUID
            deleted_by_id: ID of user deleting the student

        Returns:
            True if deleted, False if not found
        """
        student = await self.repository.get_by_id(student_id)
        if not student:
            return False

        await self.repository.delete(student_id, deleted_by_id)
        await self.db.commit()

        return True

    async def change_student_status(
        self,
        student_id: uuid.UUID,
        new_status: str,
        updated_by_id: uuid.UUID
    ) -> Optional[Student]:
        """Change student status"""
        valid_statuses = ['enrolled', 'graduated', 'transferred', 'withdrawn', 'suspended']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        return await self.update_student(
            student_id,
            StudentUpdateSchema(status=new_status),
            updated_by_id
        )

    async def promote_student(
        self,
        student_id: uuid.UUID,
        updated_by_id: uuid.UUID
    ) -> Optional[Student]:
        """
        Promote student to next grade level

        Args:
            student_id: Student UUID
            updated_by_id: ID of user promoting the student

        Returns:
            Updated student or None if not found

        Raises:
            ValueError: If student cannot be promoted
        """
        student = await self.repository.get_by_id(student_id)
        if not student:
            return None

        if not student.can_promote():
            raise ValueError(
                f"Student cannot be promoted. Current status: {student.status}, "
                f"Grade: {student.grade_level}"
            )

        new_grade = student.grade_level + 1

        # If promoting to grade 7, this is their final year
        update_data = StudentUpdateSchema(grade_level=new_grade)

        return await self.update_student(student_id, update_data, updated_by_id)

    async def link_parent(
        self,
        link_data: ParentStudentLinkSchema,
        created_by_id: uuid.UUID
    ) -> ParentStudentRelationship:
        """
        Link a parent to a student

        Args:
            link_data: Parent-student link data
            created_by_id: ID of user creating the link

        Returns:
            Created relationship

        Raises:
            ValueError: If relationship already exists
        """
        # Check if relationship already exists
        existing = await self.relationship_repository.get_relationship(
            link_data.parent_id,
            link_data.student_id
        )
        if existing:
            raise ValueError("This parent-student relationship already exists")

        # If setting as primary contact, unset any existing primary contact
        if link_data.is_primary_contact:
            primary = await self.relationship_repository.get_primary_contact(link_data.student_id)
            if primary:
                await self.relationship_repository.update(
                    primary.id,
                    {'is_primary_contact': False}
                )

        # Create relationship
        relationship_dict = link_data.model_dump()
        relationship_dict['created_by'] = created_by_id

        relationship = await self.relationship_repository.create(relationship_dict)
        await self.db.commit()
        await self.db.refresh(relationship)

        return relationship

    async def unlink_parent(
        self,
        parent_id: uuid.UUID,
        student_id: uuid.UUID,
        deleted_by_id: uuid.UUID
    ) -> bool:
        """
        Unlink a parent from a student

        Args:
            parent_id: Parent user UUID
            student_id: Student UUID
            deleted_by_id: ID of user removing the link

        Returns:
            True if unlinked, False if relationship not found
        """
        relationship = await self.relationship_repository.get_relationship(parent_id, student_id)
        if not relationship:
            return False

        await self.relationship_repository.delete(relationship.id, deleted_by_id)
        await self.db.commit()

        return True

    async def get_student_parents(self, student_id: uuid.UUID) -> List[ParentStudentRelationship]:
        """Get all parents for a student"""
        return await self.relationship_repository.get_by_student(student_id)

    async def get_parent_children(self, parent_id: uuid.UUID) -> List[ParentStudentRelationship]:
        """Get all children for a parent"""
        return await self.relationship_repository.get_by_parent(parent_id)

    async def get_statistics(self, school_id: uuid.UUID) -> dict:
        """Get student statistics for a school"""
        return await self.repository.get_statistics(school_id)
