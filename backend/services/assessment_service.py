"""
Assessment Service

Business logic layer for Assessment operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.assessment_repository import AssessmentRepository
from repositories.student_repository import StudentRepository
from repositories.teacher_repository import TeacherRepository
from repositories.subject_repository import SubjectRepository
from repositories.class_repository import ClassRepository
from models.assessment import Assessment
from datetime import datetime, date
from decimal import Decimal
import uuid


class AssessmentService:
    """Service layer for Assessment business logic"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = AssessmentRepository(session)
        self.student_repository = StudentRepository(session)
        self.teacher_repository = TeacherRepository(session)
        self.subject_repository = SubjectRepository(session)
        self.class_repository = ClassRepository(session)

    async def create_assessment(
        self,
        school_id: uuid.UUID,
        student_id: uuid.UUID,
        class_id: uuid.UUID,
        subject_id: uuid.UUID,
        teacher_id: uuid.UUID,
        title: str,
        assessment_type: str,
        quarter: str,
        assessment_date: date,
        total_points: Decimal,
        created_by_id: uuid.UUID,
        description: Optional[str] = None,
        due_date: Optional[date] = None,
        points_earned: Optional[Decimal] = None,
        status: str = "pending",
        weight: Decimal = Decimal("1.0")
    ) -> Assessment:
        """Create a new assessment"""

        # Validate entities exist
        student = await self.student_repository.find_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

        teacher = await self.teacher_repository.find_by_id(teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")

        subject = await self.subject_repository.find_by_id(subject_id)
        if not subject:
            raise ValueError("Subject not found")

        assessment_data = {
            'school_id': school_id,
            'student_id': student_id,
            'class_id': class_id,
            'subject_id': subject_id,
            'teacher_id': teacher_id,
            'title': title,
            'description': description,
            'assessment_type': assessment_type,
            'quarter': quarter,
            'assessment_date': assessment_date,
            'due_date': due_date,
            'total_points': total_points,
            'points_earned': points_earned,
            'status': status,
            'weight': weight
        }

        assessment = await self.repository.create(assessment_data, created_by_id)

        # Calculate percentage and letter grade if points_earned provided
        if points_earned is not None:
            assessment.calculate_percentage()
            assessment.letter_grade = assessment.assign_letter_grade()
            await self.session.flush()

        return assessment

    async def grade_assessment(
        self,
        assessment_id: uuid.UUID,
        points_earned: Decimal,
        feedback: Optional[str],
        updated_by_id: uuid.UUID
    ) -> Optional[Assessment]:
        """Grade an assessment"""
        assessment = await self.repository.find_by_id(assessment_id)
        if not assessment:
            return None

        # Calculate values
        percentage = None
        if points_earned is not None:
            percentage = (float(points_earned) / float(assessment.total_points)) * 100

        letter_grade = None
        if percentage is not None:
            if percentage >= 97:
                letter_grade = "A+"
            elif percentage >= 93:
                letter_grade = "A"
            elif percentage >= 90:
                letter_grade = "A-"
            elif percentage >= 87:
                letter_grade = "B+"
            elif percentage >= 83:
                letter_grade = "B"
            elif percentage >= 80:
                letter_grade = "B-"
            elif percentage >= 77:
                letter_grade = "C+"
            elif percentage >= 73:
                letter_grade = "C"
            elif percentage >= 70:
                letter_grade = "C-"
            elif percentage >= 67:
                letter_grade = "D+"
            elif percentage >= 63:
                letter_grade = "D"
            elif percentage >= 60:
                letter_grade = "D-"
            else:
                letter_grade = "F"

        # Prepare update data
        update_data = {
            'points_earned': points_earned,
            'percentage': percentage,
            'letter_grade': letter_grade,
            'feedback': feedback,
            'status': "graded",
            'graded_at': datetime.now()
        }

        return await self.repository.update(assessment_id, update_data, updated_by_id)

    async def get_student_assessments(
        self,
        student_id: uuid.UUID,
        quarter: Optional[str] = None,
        subject_id: Optional[uuid.UUID] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Assessment], int]:
        """Get assessments for a student"""
        return await self.repository.get_by_student(student_id, quarter, subject_id, page, limit)

    async def get_class_assessments(
        self,
        class_id: uuid.UUID,
        quarter: Optional[str] = None,
        assessment_type: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Assessment], int]:
        """Get assessments for a class"""
        return await self.repository.get_by_class(class_id, quarter, assessment_type, page, limit)

    async def get_teacher_assessments(
        self,
        teacher_id: uuid.UUID,
        quarter: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Assessment], int]:
        """Get assessments for a teacher"""
        return await self.repository.get_by_teacher(teacher_id, quarter, status, page, limit)

    async def delete_assessment(self, assessment_id: uuid.UUID, deleted_by_id: uuid.UUID) -> bool:
        """Soft delete an assessment"""
        return await self.repository.delete(assessment_id, deleted_by_id)

    async def get_statistics(self, school_id: uuid.UUID, quarter: Optional[str] = None) -> Dict[str, Any]:
        """Get assessment statistics"""
        return await self.repository.get_statistics(school_id, quarter)
