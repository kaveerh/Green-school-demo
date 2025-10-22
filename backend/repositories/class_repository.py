"""
Class Repository

Data access layer for Class operations.
"""

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple, Dict, Any
import uuid
from datetime import date

from models.class_model import Class, StudentClass


class ClassRepository:
    """Repository for Class database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, class_obj: Class) -> Class:
        """Create a new class"""
        self.db.add(class_obj)
        await self.db.commit()
        await self.db.refresh(class_obj)
        return class_obj

    async def get_by_id(self, class_id: uuid.UUID) -> Optional[Class]:
        """Get class by ID with relationships"""
        result = await self.db.execute(
            select(Class)
            .options(
                selectinload(Class.subject),
                selectinload(Class.teacher),
                selectinload(Class.room)
            )
            .where(
                and_(
                    Class.id == class_id,
                    Class.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, school_id: uuid.UUID, code: str) -> Optional[Class]:
        """Get class by code within a school"""
        result = await self.db.execute(
            select(Class).where(
                and_(
                    Class.school_id == school_id,
                    Class.code == code.upper(),
                    Class.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 50,
        subject_id: Optional[uuid.UUID] = None,
        teacher_id: Optional[uuid.UUID] = None,
        room_id: Optional[uuid.UUID] = None,
        grade_level: Optional[int] = None,
        quarter: Optional[str] = None,
        academic_year: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Class], int]:
        """Get classes for a school with pagination and filters"""
        query = select(Class).options(
            selectinload(Class.subject),
            selectinload(Class.teacher),
            selectinload(Class.room)
        ).where(
            and_(
                Class.school_id == school_id,
                Class.deleted_at.is_(None)
            )
        )

        # Apply filters
        if subject_id:
            query = query.where(Class.subject_id == subject_id)

        if teacher_id:
            query = query.where(Class.teacher_id == teacher_id)

        if room_id:
            query = query.where(Class.room_id == room_id)

        if grade_level is not None:
            query = query.where(Class.grade_level == grade_level)

        if quarter:
            query = query.where(Class.quarter == quarter)

        if academic_year:
            query = query.where(Class.academic_year == academic_year)

        if is_active is not None:
            query = query.where(Class.is_active == is_active)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination and sorting
        query = query.order_by(Class.grade_level, Class.code)
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        classes = result.scalars().all()

        return list(classes), total

    async def get_by_teacher(
        self,
        school_id: uuid.UUID,
        teacher_id: uuid.UUID,
        quarter: Optional[str] = None,
        academic_year: Optional[str] = None
    ) -> List[Class]:
        """Get all classes for a teacher"""
        query = select(Class).options(
            selectinload(Class.subject),
            selectinload(Class.room)
        ).where(
            and_(
                Class.school_id == school_id,
                Class.teacher_id == teacher_id,
                Class.deleted_at.is_(None)
            )
        )

        if quarter:
            query = query.where(Class.quarter == quarter)

        if academic_year:
            query = query.where(Class.academic_year == academic_year)

        query = query.order_by(Class.grade_level, Class.code)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_subject(
        self,
        school_id: uuid.UUID,
        subject_id: uuid.UUID,
        grade_level: Optional[int] = None,
        quarter: Optional[str] = None
    ) -> List[Class]:
        """Get all classes for a subject"""
        query = select(Class).options(
            selectinload(Class.teacher),
            selectinload(Class.room)
        ).where(
            and_(
                Class.school_id == school_id,
                Class.subject_id == subject_id,
                Class.deleted_at.is_(None)
            )
        )

        if grade_level is not None:
            query = query.where(Class.grade_level == grade_level)

        if quarter:
            query = query.where(Class.quarter == quarter)

        query = query.order_by(Class.grade_level, Class.code)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_room(
        self,
        school_id: uuid.UUID,
        room_id: uuid.UUID
    ) -> List[Class]:
        """Get all classes for a room"""
        result = await self.db.execute(
            select(Class).options(
                selectinload(Class.subject),
                selectinload(Class.teacher)
            ).where(
                and_(
                    Class.school_id == school_id,
                    Class.room_id == room_id,
                    Class.deleted_at.is_(None)
                )
            ).order_by(Class.code)
        )
        return list(result.scalars().all())

    async def search(
        self,
        school_id: uuid.UUID,
        search_query: str,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Class], int]:
        """Search classes by code, name, or description"""
        search_pattern = f"%{search_query}%"

        query = select(Class).options(
            selectinload(Class.subject),
            selectinload(Class.teacher),
            selectinload(Class.room)
        ).where(
            and_(
                Class.school_id == school_id,
                Class.deleted_at.is_(None),
                or_(
                    Class.code.ilike(search_pattern),
                    Class.name.ilike(search_pattern),
                    Class.description.ilike(search_pattern)
                )
            )
        )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination
        query = query.order_by(Class.code)
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        classes = result.scalars().all()

        return list(classes), total

    async def update(self, class_obj: Class) -> Class:
        """Update class"""
        await self.db.commit()
        await self.db.refresh(class_obj)
        return class_obj

    async def delete(self, class_obj: Class) -> None:
        """Soft delete class"""
        class_obj.soft_delete()
        await self.db.commit()

    async def code_exists(
        self,
        school_id: uuid.UUID,
        code: str,
        exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if class code already exists in school"""
        query = select(Class).where(
            and_(
                Class.school_id == school_id,
                Class.code == code.upper(),
                Class.deleted_at.is_(None)
            )
        )

        if exclude_id:
            query = query.where(Class.id != exclude_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_statistics(self, school_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Get class statistics"""
        base_query = select(Class).where(Class.deleted_at.is_(None))

        if school_id:
            base_query = base_query.where(Class.school_id == school_id)

        # Total classes
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(total_query)
        total_classes = total_result.scalar()

        # Active classes
        active_query = select(func.count()).select_from(
            base_query.where(Class.is_active == True).subquery()
        )
        active_result = await self.db.execute(active_query)
        active_classes = active_result.scalar()

        # Classes by grade
        grade_query = select(
            Class.grade_level,
            func.count(Class.id).label('count')
        ).select_from(base_query.subquery()).group_by(Class.grade_level)
        grade_result = await self.db.execute(grade_query)
        by_grade = {str(row[0]): row[1] for row in grade_result}

        # Classes by quarter
        quarter_query = select(
            Class.quarter,
            func.count(Class.id).label('count')
        ).select_from(base_query.subquery()).group_by(Class.quarter)
        quarter_result = await self.db.execute(quarter_query)
        by_quarter = {row[0]: row[1] for row in quarter_result}

        # Classes by subject (need to join)
        from models.subject import Subject
        subject_query = select(
            Subject.code,
            func.count(Class.id).label('count')
        ).join(Class, Class.subject_id == Subject.id).where(
            Class.deleted_at.is_(None)
        )
        if school_id:
            subject_query = subject_query.where(Class.school_id == school_id)
        subject_query = subject_query.group_by(Subject.code)
        subject_result = await self.db.execute(subject_query)
        by_subject = {row[0]: row[1] for row in subject_result}

        # Enrollment statistics
        enrollment_query = select(
            func.sum(Class.current_enrollment).label('total_enrollment'),
            func.avg(Class.current_enrollment).label('avg_enrollment'),
            func.sum(Class.max_students).label('total_capacity')
        ).select_from(base_query.subquery())
        enrollment_result = await self.db.execute(enrollment_query)
        enrollment_row = enrollment_result.first()

        total_enrollment = int(enrollment_row[0]) if enrollment_row[0] else 0
        avg_enrollment = float(enrollment_row[1]) if enrollment_row[1] else 0.0
        total_capacity = int(enrollment_row[2]) if enrollment_row[2] else 0

        capacity_utilization = 0.0
        if total_capacity > 0:
            capacity_utilization = round((total_enrollment / total_capacity) * 100, 1)

        return {
            'total_classes': total_classes,
            'active_classes': active_classes,
            'inactive_classes': total_classes - active_classes,
            'by_grade': by_grade,
            'by_quarter': by_quarter,
            'by_subject': by_subject,
            'total_enrollment': total_enrollment,
            'average_class_size': round(avg_enrollment, 1),
            'capacity_utilization': capacity_utilization
        }


class StudentClassRepository:
    """Repository for StudentClass database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, student_class: StudentClass) -> StudentClass:
        """Create a new student enrollment"""
        self.db.add(student_class)
        await self.db.commit()
        await self.db.refresh(student_class)
        return student_class

    async def get_by_id(self, enrollment_id: uuid.UUID) -> Optional[StudentClass]:
        """Get enrollment by ID"""
        result = await self.db.execute(
            select(StudentClass).where(StudentClass.id == enrollment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_student_and_class(
        self,
        student_id: uuid.UUID,
        class_id: uuid.UUID
    ) -> Optional[StudentClass]:
        """Get enrollment by student and class"""
        result = await self.db.execute(
            select(StudentClass).where(
                and_(
                    StudentClass.student_id == student_id,
                    StudentClass.class_id == class_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_students_in_class(self, class_id: uuid.UUID) -> List[StudentClass]:
        """Get all students enrolled in a class"""
        result = await self.db.execute(
            select(StudentClass).options(
                selectinload(StudentClass.student)
            ).where(
                StudentClass.class_id == class_id
            ).order_by(StudentClass.enrollment_date)
        )
        return list(result.scalars().all())

    async def get_classes_for_student(
        self,
        student_id: uuid.UUID,
        status: Optional[str] = None
    ) -> List[StudentClass]:
        """Get all classes for a student"""
        query = select(StudentClass).options(
            selectinload(StudentClass.class_obj)
        ).where(
            StudentClass.student_id == student_id
        )

        if status:
            query = query.where(StudentClass.status == status)

        query = query.order_by(StudentClass.enrollment_date.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, student_class: StudentClass) -> StudentClass:
        """Update student enrollment"""
        await self.db.commit()
        await self.db.refresh(student_class)
        return student_class

    async def delete(self, student_class: StudentClass) -> None:
        """Delete enrollment (hard delete)"""
        await self.db.delete(student_class)
        await self.db.commit()

    async def enrollment_exists(
        self,
        student_id: uuid.UUID,
        class_id: uuid.UUID
    ) -> bool:
        """Check if student is already enrolled in class"""
        result = await self.db.execute(
            select(StudentClass).where(
                and_(
                    StudentClass.student_id == student_id,
                    StudentClass.class_id == class_id
                )
            )
        )
        return result.scalar_one_or_none() is not None
