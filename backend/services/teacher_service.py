"""
Teacher Service
Business logic layer for teacher operations
"""
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.teacher_repository import TeacherRepository
from repositories.user_repository import UserRepository
from models.teacher import Teacher
from schemas.teacher_schema import (
    TeacherCreateSchema,
    TeacherUpdateSchema,
    TeacherResponseSchema,
    TeacherSearchSchema,
    TeacherStatisticsSchema,
)
import uuid
import logging

logger = logging.getLogger(__name__)


class TeacherService:
    """Service layer for teacher business logic"""

    def __init__(self, session: AsyncSession):
        """
        Initialize teacher service

        Args:
            session: Database session
        """
        self.session = session
        self.repository = TeacherRepository(session)
        self.user_repository = UserRepository(session)

    async def create_teacher(
        self,
        teacher_data: TeacherCreateSchema,
        created_by_id: Optional[uuid.UUID] = None
    ) -> TeacherResponseSchema:
        """
        Create a new teacher profile

        Args:
            teacher_data: Teacher creation data
            created_by_id: UUID of user creating this teacher

        Returns:
            Created teacher response schema

        Raises:
            ValueError: If validation fails
        """
        teacher_dict = teacher_data.model_dump()

        # Validate user exists and has teacher persona
        user = await self.user_repository.find_by_id(teacher_data.user_id)
        if not user:
            raise ValueError("User not found")
        if user.persona != "teacher":
            raise ValueError("User must have teacher persona")

        # Check if user already has a teacher profile
        existing_teacher = await self.repository.find_by_user_id(teacher_data.user_id)
        if existing_teacher:
            raise ValueError("User already has a teacher profile")

        # Check if employee_id already exists in the school
        if await self.repository.employee_id_exists(user.school_id, teacher_data.employee_id):
            raise ValueError(f"Employee ID '{teacher_data.employee_id}' already exists in this school")

        # Set school_id from user
        teacher_dict['school_id'] = user.school_id

        # Create teacher
        teacher = await self.repository.create(teacher_dict, created_by_id)
        await self.session.commit()

        logger.info(f"Teacher created: {teacher.employee_id} (ID: {teacher.id})")

        return self._to_response_schema(teacher)

    async def get_teacher(
        self,
        teacher_id: uuid.UUID
    ) -> Optional[TeacherResponseSchema]:
        """
        Get a teacher by ID

        Args:
            teacher_id: Teacher UUID

        Returns:
            Teacher response schema or None
        """
        teacher = await self.repository.find_by_id(teacher_id)
        if not teacher:
            return None

        return self._to_response_schema(teacher)

    async def get_teacher_by_user_id(
        self,
        user_id: uuid.UUID
    ) -> Optional[TeacherResponseSchema]:
        """
        Get a teacher by user ID

        Args:
            user_id: User UUID

        Returns:
            Teacher response schema or None
        """
        teacher = await self.repository.find_by_user_id(user_id)
        if not teacher:
            return None

        return self._to_response_schema(teacher)

    async def get_teacher_by_employee_id(
        self,
        school_id: uuid.UUID,
        employee_id: str
    ) -> Optional[TeacherResponseSchema]:
        """
        Get a teacher by employee ID

        Args:
            school_id: School UUID
            employee_id: Employee ID

        Returns:
            Teacher response schema or None
        """
        teacher = await self.repository.find_by_employee_id(school_id, employee_id)
        if not teacher:
            return None

        return self._to_response_schema(teacher)

    async def search_teachers(
        self,
        school_id: uuid.UUID,
        search_params: TeacherSearchSchema
    ) -> Tuple[List[TeacherResponseSchema], Dict[str, Any]]:
        """
        Search teachers with filters and pagination

        Args:
            school_id: School UUID
            search_params: Search parameters

        Returns:
            Tuple of (teacher list, pagination info)
        """
        # Build filters
        filters = {}
        if search_params.status:
            filters['status'] = search_params.status.value
        if search_params.department:
            filters['department'] = search_params.department
        if search_params.employment_type:
            filters['employment_type'] = search_params.employment_type.value

        # Execute search
        if search_params.search:
            # Search by employee_id, department, or job_title
            teachers, total = await self.repository.search_teachers(
                school_id=school_id,
                search_term=search_params.search,
                page=search_params.page,
                limit=search_params.limit
            )
        elif search_params.grade:
            # Search by grade level
            teachers = await self.repository.find_by_grade(
                school_id=school_id,
                grade=search_params.grade
            )
            total = len(teachers)
            # Manual pagination for grade search
            start_idx = (search_params.page - 1) * search_params.limit
            end_idx = start_idx + search_params.limit
            teachers = teachers[start_idx:end_idx]
        elif search_params.specialization:
            # Search by specialization
            teachers = await self.repository.find_by_specialization(
                school_id=school_id,
                specialization=search_params.specialization
            )
            total = len(teachers)
            # Manual pagination for specialization search
            start_idx = (search_params.page - 1) * search_params.limit
            end_idx = start_idx + search_params.limit
            teachers = teachers[start_idx:end_idx]
        else:
            # Standard search with filters
            teachers, total = await self.repository.find_by_school(
                school_id=school_id,
                page=search_params.page,
                limit=search_params.limit,
                filters=filters if filters else None
            )

        # Convert to response schemas
        teacher_responses = [self._to_response_schema(teacher) for teacher in teachers]

        # Build pagination info
        pagination = {
            "page": search_params.page,
            "limit": search_params.limit,
            "total": total,
            "pages": (total + search_params.limit - 1) // search_params.limit
        }

        return teacher_responses, pagination

    async def update_teacher(
        self,
        teacher_id: uuid.UUID,
        teacher_data: TeacherUpdateSchema,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[TeacherResponseSchema]:
        """
        Update a teacher

        Args:
            teacher_id: Teacher UUID
            teacher_data: Update data
            updated_by_id: UUID of user making the update

        Returns:
            Updated teacher response schema or None

        Raises:
            ValueError: If validation fails
        """
        # Check if teacher exists
        existing_teacher = await self.repository.find_by_id(teacher_id)
        if not existing_teacher:
            return None

        # Prepare update data (exclude None values)
        update_dict = teacher_data.model_dump(exclude_none=True)

        # Validate employee_id uniqueness if changing
        if 'employee_id' in update_dict:
            if await self.repository.employee_id_exists(
                existing_teacher.school_id,
                update_dict['employee_id'],
                exclude_teacher_id=teacher_id
            ):
                raise ValueError(f"Employee ID '{update_dict['employee_id']}' already exists in this school")

        # Update teacher
        updated_teacher = await self.repository.update(teacher_id, update_dict, updated_by_id)
        await self.session.commit()

        logger.info(f"Teacher updated: {updated_teacher.employee_id} (ID: {updated_teacher.id})")

        return self._to_response_schema(updated_teacher)

    async def delete_teacher(
        self,
        teacher_id: uuid.UUID,
        deleted_by_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Soft delete a teacher

        Args:
            teacher_id: Teacher UUID
            deleted_by_id: UUID of user performing deletion

        Returns:
            True if deleted, False if not found
        """
        # Perform soft delete
        success = await self.repository.delete(teacher_id, deleted_by_id)
        if success:
            await self.session.commit()
            logger.info(f"Teacher deleted: ID {teacher_id}")

        return success

    async def change_teacher_status(
        self,
        teacher_id: uuid.UUID,
        new_status: str,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[TeacherResponseSchema]:
        """
        Change teacher status

        Args:
            teacher_id: Teacher UUID
            new_status: New status value
            updated_by_id: UUID of user making the change

        Returns:
            Updated teacher or None
        """
        update_dict = {'status': new_status}
        updated_teacher = await self.repository.update(teacher_id, update_dict, updated_by_id)
        if updated_teacher:
            await self.session.commit()
            logger.info(f"Teacher status changed: {updated_teacher.employee_id} -> {new_status}")

        return self._to_response_schema(updated_teacher) if updated_teacher else None

    async def assign_grades(
        self,
        teacher_id: uuid.UUID,
        grade_levels: List[int],
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[TeacherResponseSchema]:
        """
        Assign grade levels to teacher

        Args:
            teacher_id: Teacher UUID
            grade_levels: List of grade levels (1-7)
            updated_by_id: UUID of user making the assignment

        Returns:
            Updated teacher or None

        Raises:
            ValueError: If grade levels are invalid
        """
        # Validate grades
        for grade in grade_levels:
            if grade < 1 or grade > 7:
                raise ValueError(f"Invalid grade level: {grade}. Must be between 1 and 7")

        update_dict = {'grade_levels': sorted(list(set(grade_levels)))}
        updated_teacher = await self.repository.update(teacher_id, update_dict, updated_by_id)
        if updated_teacher:
            await self.session.commit()
            logger.info(f"Grades assigned to teacher {teacher_id}: {grade_levels}")

        return self._to_response_schema(updated_teacher) if updated_teacher else None

    async def assign_specializations(
        self,
        teacher_id: uuid.UUID,
        specializations: List[str],
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Optional[TeacherResponseSchema]:
        """
        Assign specializations to teacher

        Args:
            teacher_id: Teacher UUID
            specializations: List of subject specializations
            updated_by_id: UUID of user making the assignment

        Returns:
            Updated teacher or None
        """
        # Normalize specializations (uppercase, trim)
        normalized = [s.strip().upper() for s in specializations if s.strip()]

        update_dict = {'specializations': list(set(normalized))}
        updated_teacher = await self.repository.update(teacher_id, update_dict, updated_by_id)
        if updated_teacher:
            await self.session.commit()
            logger.info(f"Specializations assigned to teacher {teacher_id}: {normalized}")

        return self._to_response_schema(updated_teacher) if updated_teacher else None

    async def get_active_teachers(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[TeacherResponseSchema], Dict[str, Any]]:
        """
        Get all active teachers in a school

        Args:
            school_id: School UUID
            page: Page number
            limit: Items per page

        Returns:
            Tuple of (teacher list, pagination info)
        """
        teachers, total = await self.repository.find_active_teachers(
            school_id=school_id,
            page=page,
            limit=limit
        )

        # Convert to response schemas
        teacher_responses = [self._to_response_schema(teacher) for teacher in teachers]

        # Build pagination info
        pagination = {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }

        return teacher_responses, pagination

    async def get_teachers_by_grade(
        self,
        school_id: uuid.UUID,
        grade: int
    ) -> List[TeacherResponseSchema]:
        """
        Get all teachers who teach a specific grade

        Args:
            school_id: School UUID
            grade: Grade level (1-7)

        Returns:
            List of teacher response schemas

        Raises:
            ValueError: If grade is invalid
        """
        if grade < 1 or grade > 7:
            raise ValueError(f"Invalid grade: {grade}. Must be between 1 and 7")

        teachers = await self.repository.find_by_grade(school_id, grade)
        return [self._to_response_schema(teacher) for teacher in teachers]

    async def get_teachers_by_specialization(
        self,
        school_id: uuid.UUID,
        specialization: str
    ) -> List[TeacherResponseSchema]:
        """
        Get all teachers with a specific specialization

        Args:
            school_id: School UUID
            specialization: Subject specialization

        Returns:
            List of teacher response schemas
        """
        teachers = await self.repository.find_by_specialization(school_id, specialization)
        return [self._to_response_schema(teacher) for teacher in teachers]

    async def get_statistics(
        self,
        school_id: uuid.UUID
    ) -> TeacherStatisticsSchema:
        """
        Get teacher statistics for a school

        Args:
            school_id: School UUID

        Returns:
            Teacher statistics
        """
        stats = await self.repository.get_statistics(school_id)

        return TeacherStatisticsSchema(
            total=stats['total'],
            active=stats['active'],
            inactive=stats['inactive'],
            by_employment_type=stats['by_employment_type'],
            by_department=stats['by_department']
        )

    def _to_response_schema(self, teacher: Teacher) -> TeacherResponseSchema:
        """
        Convert Teacher model to response schema

        Args:
            teacher: Teacher model instance

        Returns:
            TeacherResponseSchema
        """
        teacher_dict = teacher.to_dict(include_sensitive=False)

        # Add computed fields from model methods
        teacher_dict['is_currently_employed'] = teacher.is_currently_employed()
        teacher_dict['years_of_service'] = teacher.years_of_service()
        teacher_dict['is_certification_valid'] = teacher.is_certification_valid()
        teacher_dict['is_full_time'] = teacher.is_full_time()

        return TeacherResponseSchema(**teacher_dict)
