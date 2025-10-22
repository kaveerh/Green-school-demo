"""
Lesson Repository

Data access layer for Lesson operations.
"""

from sqlalchemy import select, func, or_, and_, between
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple, Dict, Any
import uuid
from datetime import date, datetime, timedelta

from models.lesson import Lesson


class LessonRepository:
    """Repository for Lesson database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, lesson_data: Dict[str, Any]) -> Lesson:
        """Create a new lesson"""
        lesson = Lesson(**lesson_data)
        self.db.add(lesson)
        await self.db.commit()
        await self.db.refresh(lesson)
        return lesson

    async def get_by_id(self, lesson_id: uuid.UUID) -> Optional[Lesson]:
        """Get lesson by ID with relationships"""
        result = await self.db.execute(
            select(Lesson)
            .options(
                selectinload(Lesson.class_obj),
                selectinload(Lesson.subject),
                selectinload(Lesson.teacher)
            )
            .where(
                and_(
                    Lesson.id == lesson_id,
                    Lesson.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        page: int = 1,
        limit: int = 50,
        class_id: Optional[uuid.UUID] = None,
        teacher_id: Optional[uuid.UUID] = None,
        subject_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        is_template: Optional[bool] = None
    ) -> Tuple[List[Lesson], int]:
        """Get lessons for a school with pagination and filters"""
        query = select(Lesson).options(
            selectinload(Lesson.class_obj),
            selectinload(Lesson.subject),
            selectinload(Lesson.teacher)
        ).where(
            and_(
                Lesson.school_id == school_id,
                Lesson.deleted_at.is_(None)
            )
        )

        # Apply filters
        if class_id:
            query = query.where(Lesson.class_id == class_id)

        if teacher_id:
            query = query.where(Lesson.teacher_id == teacher_id)

        if subject_id:
            query = query.where(Lesson.subject_id == subject_id)

        if status:
            query = query.where(Lesson.status == status)

        if start_date:
            query = query.where(Lesson.scheduled_date >= start_date)

        if end_date:
            query = query.where(Lesson.scheduled_date <= end_date)

        if is_template is not None:
            query = query.where(Lesson.is_template == is_template)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination and sorting
        query = query.order_by(Lesson.scheduled_date.desc(), Lesson.lesson_number)
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        lessons = result.scalars().all()

        return list(lessons), total

    async def get_by_class(
        self,
        class_id: uuid.UUID,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Lesson]:
        """Get all lessons for a class"""
        query = select(Lesson).options(
            selectinload(Lesson.subject),
            selectinload(Lesson.teacher)
        ).where(
            and_(
                Lesson.class_id == class_id,
                Lesson.deleted_at.is_(None)
            )
        )

        if status:
            query = query.where(Lesson.status == status)

        if start_date:
            query = query.where(Lesson.scheduled_date >= start_date)

        if end_date:
            query = query.where(Lesson.scheduled_date <= end_date)

        query = query.order_by(Lesson.lesson_number)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_teacher(
        self,
        school_id: uuid.UUID,
        teacher_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None
    ) -> List[Lesson]:
        """Get all lessons for a teacher"""
        query = select(Lesson).options(
            selectinload(Lesson.class_obj),
            selectinload(Lesson.subject)
        ).where(
            and_(
                Lesson.school_id == school_id,
                Lesson.teacher_id == teacher_id,
                Lesson.deleted_at.is_(None)
            )
        )

        if start_date:
            query = query.where(Lesson.scheduled_date >= start_date)

        if end_date:
            query = query.where(Lesson.scheduled_date <= end_date)

        if status:
            query = query.where(Lesson.status == status)

        query = query.order_by(Lesson.scheduled_date, Lesson.lesson_number)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_date_range(
        self,
        school_id: uuid.UUID,
        start_date: date,
        end_date: date,
        teacher_id: Optional[uuid.UUID] = None,
        class_id: Optional[uuid.UUID] = None,
        subject_id: Optional[uuid.UUID] = None
    ) -> List[Lesson]:
        """Get lessons within a date range (for calendar view)"""
        query = select(Lesson).options(
            selectinload(Lesson.class_obj),
            selectinload(Lesson.subject),
            selectinload(Lesson.teacher)
        ).where(
            and_(
                Lesson.school_id == school_id,
                Lesson.scheduled_date >= start_date,
                Lesson.scheduled_date <= end_date,
                Lesson.deleted_at.is_(None)
            )
        )

        if teacher_id:
            query = query.where(Lesson.teacher_id == teacher_id)

        if class_id:
            query = query.where(Lesson.class_id == class_id)

        if subject_id:
            query = query.where(Lesson.subject_id == subject_id)

        query = query.order_by(Lesson.scheduled_date, Lesson.lesson_number)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_upcoming_lessons(
        self,
        school_id: uuid.UUID,
        teacher_id: Optional[uuid.UUID] = None,
        days: int = 7,
        limit: int = 50
    ) -> List[Lesson]:
        """Get upcoming lessons (within next N days)"""
        today = date.today()
        end_date = today + timedelta(days=days)

        query = select(Lesson).options(
            selectinload(Lesson.class_obj),
            selectinload(Lesson.subject)
        ).where(
            and_(
                Lesson.school_id == school_id,
                Lesson.scheduled_date >= today,
                Lesson.scheduled_date <= end_date,
                Lesson.status.in_(['draft', 'scheduled']),
                Lesson.deleted_at.is_(None)
            )
        )

        if teacher_id:
            query = query.where(Lesson.teacher_id == teacher_id)

        query = query.order_by(Lesson.scheduled_date, Lesson.lesson_number)
        query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_past_due_lessons(
        self,
        school_id: uuid.UUID,
        teacher_id: Optional[uuid.UUID] = None,
        limit: int = 50
    ) -> List[Lesson]:
        """Get lessons that are past their scheduled date but not completed"""
        today = date.today()

        query = select(Lesson).options(
            selectinload(Lesson.class_obj),
            selectinload(Lesson.subject)
        ).where(
            and_(
                Lesson.school_id == school_id,
                Lesson.scheduled_date < today,
                Lesson.status.in_(['draft', 'scheduled', 'in_progress']),
                Lesson.deleted_at.is_(None)
            )
        )

        if teacher_id:
            query = query.where(Lesson.teacher_id == teacher_id)

        query = query.order_by(Lesson.scheduled_date.desc())
        query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search(
        self,
        school_id: uuid.UUID,
        search_query: str,
        page: int = 1,
        limit: int = 50,
        teacher_id: Optional[uuid.UUID] = None,
        class_id: Optional[uuid.UUID] = None
    ) -> Tuple[List[Lesson], int]:
        """Search lessons by title, description, or content"""
        search_pattern = f"%{search_query}%"

        query = select(Lesson).options(
            selectinload(Lesson.class_obj),
            selectinload(Lesson.subject),
            selectinload(Lesson.teacher)
        ).where(
            and_(
                Lesson.school_id == school_id,
                Lesson.deleted_at.is_(None),
                or_(
                    Lesson.title.ilike(search_pattern),
                    Lesson.description.ilike(search_pattern),
                    Lesson.introduction.ilike(search_pattern),
                    Lesson.main_activity.ilike(search_pattern),
                    Lesson.assessment.ilike(search_pattern),
                    Lesson.homework.ilike(search_pattern)
                )
            )
        )

        if teacher_id:
            query = query.where(Lesson.teacher_id == teacher_id)

        if class_id:
            query = query.where(Lesson.class_id == class_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination
        query = query.order_by(Lesson.scheduled_date.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        lessons = result.scalars().all()

        return list(lessons), total

    async def get_templates(
        self,
        school_id: uuid.UUID,
        teacher_id: Optional[uuid.UUID] = None,
        subject_id: Optional[uuid.UUID] = None
    ) -> List[Lesson]:
        """Get all lesson templates"""
        query = select(Lesson).options(
            selectinload(Lesson.class_obj),
            selectinload(Lesson.subject)
        ).where(
            and_(
                Lesson.school_id == school_id,
                Lesson.is_template == True,
                Lesson.deleted_at.is_(None)
            )
        )

        if teacher_id:
            query = query.where(Lesson.teacher_id == teacher_id)

        if subject_id:
            query = query.where(Lesson.subject_id == subject_id)

        query = query.order_by(Lesson.title)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_next_lesson_number(self, class_id: uuid.UUID) -> int:
        """Get the next available lesson number for a class"""
        result = await self.db.execute(
            select(func.max(Lesson.lesson_number))
            .where(
                and_(
                    Lesson.class_id == class_id,
                    Lesson.deleted_at.is_(None)
                )
            )
        )
        max_number = result.scalar()
        return (max_number or 0) + 1

    async def update(self, lesson_id: uuid.UUID, updates: Dict[str, Any]) -> Optional[Lesson]:
        """Update lesson"""
        lesson = await self.get_by_id(lesson_id)
        if not lesson:
            return None

        for key, value in updates.items():
            setattr(lesson, key, value)

        await self.db.commit()
        await self.db.refresh(lesson)
        return lesson

    async def delete(self, lesson_id: uuid.UUID) -> bool:
        """Soft delete lesson"""
        lesson = await self.get_by_id(lesson_id)
        if not lesson:
            return False

        lesson.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def lesson_number_exists(
        self,
        class_id: uuid.UUID,
        lesson_number: int,
        exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if lesson number already exists in class"""
        query = select(Lesson).where(
            and_(
                Lesson.class_id == class_id,
                Lesson.lesson_number == lesson_number,
                Lesson.deleted_at.is_(None)
            )
        )

        if exclude_id:
            query = query.where(Lesson.id != exclude_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_statistics(
        self,
        school_id: Optional[uuid.UUID] = None,
        teacher_id: Optional[uuid.UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get lesson statistics"""
        base_query = select(Lesson).where(Lesson.deleted_at.is_(None))

        if school_id:
            base_query = base_query.where(Lesson.school_id == school_id)

        if teacher_id:
            base_query = base_query.where(Lesson.teacher_id == teacher_id)

        if start_date:
            base_query = base_query.where(Lesson.scheduled_date >= start_date)

        if end_date:
            base_query = base_query.where(Lesson.scheduled_date <= end_date)

        # Total lessons
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(total_query)
        total_lessons = total_result.scalar()

        # By status
        status_query = select(
            Lesson.status,
            func.count(Lesson.id).label('count')
        ).select_from(base_query.subquery()).group_by(Lesson.status)
        status_result = await self.db.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result}

        # By subject (need to join)
        from models.subject import Subject
        subject_query = select(
            Subject.code,
            func.count(Lesson.id).label('count')
        ).join(Lesson, Lesson.subject_id == Subject.id).where(
            Lesson.deleted_at.is_(None)
        )

        if school_id:
            subject_query = subject_query.where(Lesson.school_id == school_id)

        if teacher_id:
            subject_query = subject_query.where(Lesson.teacher_id == teacher_id)

        if start_date:
            subject_query = subject_query.where(Lesson.scheduled_date >= start_date)

        if end_date:
            subject_query = subject_query.where(Lesson.scheduled_date <= end_date)

        subject_query = subject_query.group_by(Subject.code)
        subject_result = await self.db.execute(subject_query)
        by_subject = {row[0]: row[1] for row in subject_result}

        # Duration statistics
        duration_query = select(
            func.avg(Lesson.duration_minutes).label('avg_duration'),
            func.sum(Lesson.duration_minutes).label('total_duration'),
            func.avg(Lesson.actual_duration_minutes).label('avg_actual_duration')
        ).select_from(base_query.subquery())
        duration_result = await self.db.execute(duration_query)
        duration_row = duration_result.first()

        average_duration = float(duration_row[0]) if duration_row[0] else 0.0
        total_teaching_minutes = int(duration_row[1]) if duration_row[1] else 0
        avg_actual_duration = float(duration_row[2]) if duration_row[2] else 0.0

        # Completion rate
        completed_count = by_status.get('completed', 0)
        completion_rate = 0.0
        if total_lessons > 0:
            completion_rate = round((completed_count / total_lessons) * 100, 1)

        # Average completion percentage
        completion_query = select(
            func.avg(Lesson.completion_percentage).label('avg_completion')
        ).select_from(
            base_query.where(Lesson.status == 'completed').subquery()
        )
        completion_result = await self.db.execute(completion_query)
        avg_completion_pct = completion_result.scalar() or 0.0

        return {
            'total_lessons': total_lessons,
            'by_status': by_status,
            'by_subject': by_subject,
            'average_duration': round(average_duration, 1),
            'average_actual_duration': round(avg_actual_duration, 1),
            'total_teaching_minutes': total_teaching_minutes,
            'completion_rate': completion_rate,
            'average_completion_percentage': round(avg_completion_pct, 1)
        }

    async def get_lessons_by_subject(
        self,
        school_id: uuid.UUID,
        subject_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Lesson]:
        """Get all lessons for a subject"""
        query = select(Lesson).options(
            selectinload(Lesson.class_obj),
            selectinload(Lesson.teacher)
        ).where(
            and_(
                Lesson.school_id == school_id,
                Lesson.subject_id == subject_id,
                Lesson.deleted_at.is_(None)
            )
        )

        if start_date:
            query = query.where(Lesson.scheduled_date >= start_date)

        if end_date:
            query = query.where(Lesson.scheduled_date <= end_date)

        query = query.order_by(Lesson.scheduled_date, Lesson.lesson_number)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_class(self, class_id: uuid.UUID) -> int:
        """Count total lessons for a class"""
        result = await self.db.execute(
            select(func.count(Lesson.id))
            .where(
                and_(
                    Lesson.class_id == class_id,
                    Lesson.deleted_at.is_(None)
                )
            )
        )
        return result.scalar()

    async def count_by_teacher(self, teacher_id: uuid.UUID, school_id: uuid.UUID) -> int:
        """Count total lessons for a teacher"""
        result = await self.db.execute(
            select(func.count(Lesson.id))
            .where(
                and_(
                    Lesson.school_id == school_id,
                    Lesson.teacher_id == teacher_id,
                    Lesson.deleted_at.is_(None)
                )
            )
        )
        return result.scalar()
